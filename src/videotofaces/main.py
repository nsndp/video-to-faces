import os
import os.path as osp

import cv2
import torch

from .prep import validate_args, get_clusters, get_class_ref, get_paths_for_grouping, get_video_list
from .detection import get_detector_model, detect_faces
from .grouping import get_encoder_model, encode_faces, cluster_faces, classify_faces, test_grouping
from .dupes import remove_dupes_overall


def video_to_faces(input_path=None, input_ext=None,
                   mode='full', style='anime', device=None,
                   out_dir=None, out_prefix='', resize_to=None, save_frames=False, save_rejects=False, save_dupes=False,
                   video_step=1, video_fragment=None, video_area=None, video_reader='opencv',
                   det_model='yolo', det_batch_size=32, det_min_score=0.6, det_min_size=100, det_min_border=5, det_scale=(1.5, 1.5, 2.2, 1.2), det_square=True,
                   hash_thr=8,
                   enc_model='vit_l', enc_batch_size=128,
                   group_mode='clustering', clusters=None, clusters_save_all=False, ref_dir=None, random_state=0, group_log=True,
                   enc_dup_thr=0.5, enc_oth_thr=1.5,
                   _test_enc=False, _test_exclude_other=False
                   ):
    """TBD"""
    valid = validate_args(mode, input_path, out_dir, style, group_mode, video_reader)
    if not valid:
        return
        
    if not out_dir:
        out_dir = input_path if osp.isdir(input_path) else osp.dirname(osp.abspath(input_path))
    if not device:
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    
    if mode != 'detection' and (group_mode == 'clustering' or _test_enc):
        clusters = get_clusters(clusters)
        if not clusters:
            return
    if mode != 'detection' and (group_mode == 'classification' or _test_enc):
        refs = get_class_ref(ref_dir, out_dir)
        if not refs:
            return
    if mode == 'grouping':
        imgpaths = get_paths_for_grouping(out_dir)
        if not imgpaths:
            return
    if mode == 'full' or mode == 'detection':
        files = get_video_list(input_path, input_ext)
        if not files:
            return
        vid_params = (video_step, video_fragment, video_area, video_reader)
        det_params = (det_batch_size, det_min_score, det_min_size, det_min_border, det_scale, det_square)
        save_params = (out_dir, out_prefix, resize_to, save_frames, save_rejects, save_dupes)
        
        detector = get_detector_model(style, det_model, device)
        imgpaths = detect_faces(files, detector, vid_params, det_params, save_params, hash_thr)

    if (mode == 'full' or mode == 'grouping') and imgpaths:
        if _test_enc:
            test_params = (style, enc_model, device, out_dir, _test_exclude_other, enc_batch_size, enc_oth_thr, random_state)
            test_grouping(imgpaths, refs, test_params)
            return
        encoder = get_encoder_model(style, enc_model, device)
        features = encode_faces(imgpaths, encoder, enc_batch_size)
        if enc_dup_thr:
            dup_params = ('enc', enc_dup_thr, save_dupes, out_dir)
            features, _ = remove_dupes_overall(features, imgpaths, dup_params)
        if group_mode == 'clustering':
            cluster_params = (clusters, clusters_save_all, random_state, group_log, out_dir)
            cluster_faces(imgpaths, features, cluster_params)
        if group_mode == 'classification':
            classif_params = (refs, enc_oth_thr, group_log, out_dir)
            classify_faces(imgpaths, features, encoder, classif_params)

    print('Done')