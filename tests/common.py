import os.path as osp

import cv2
import numpy as np
import torch

from videotofaces import Detector


def run_training_coco(detmodels_val, seed=None):
    model = Detector(detmodels_val, train=True)
    imgs, targ = _get_input_coco(True)
    # since we're only checking loss values and not backproping,
    # we can disable gradients to save up on memory usage
    with torch.no_grad():
        ret = model(imgs, targ, seed=seed)
    return [r.item() for r in ret]


def run_inference_coco(test_class, detmodels_val):
    model = Detector(detmodels_val)
    imgs = _get_input_coco()
    b, s, l = model(imgs)
    test_class.assertEqual((len(b), len(s), len(l)), (2, 2, 2))
    return b, s, l


def run_inference_wider(test_class, detmodels_val, imidx=[1, 2, 3, 4]):
    # from WIDER_val:
    # irl_det_1 = "12_Group_Group_12_Group_Group_12_10.jpg"
    # irl_det_2 = "12_Group_Group_12_Group_Group_12_29.jpg"
    # irl_det_3 = "2_Demonstration_Demonstration_Or_Protest_2_58.jpg"
    # irl_det_4 = "17_Ceremony_Ceremony_17_171.jpg"
    model = Detector(detmodels_val)
    testdir = osp.dirname(osp.realpath(__file__))
    imgs = [cv2.imread(osp.join(testdir, 'images', 'irl_det_%u.jpg' % i)) for i in imidx]
    ret = model(imgs)
    test_class.assertEqual((len(ret[0]), len(ret[1])), (len(imidx), len(imidx)))
    return ret[0], ret[1]


def run_inference_anime(test_class, detmodels_val):
    model = Detector(detmodels_val)
    testdir = osp.dirname(osp.realpath(__file__))
    imgs = [cv2.imread(osp.join(testdir, 'images', 'anime_det_%u.jpg' % i)) for i in [1, 2, 3, 4]]
    ret = model(imgs)
    test_class.assertEqual((len(ret[0]), len(ret[1])), (4, 4))
    return ret[0], ret[1]


def _get_input_coco(with_targets=False):
    testdir = osp.dirname(osp.realpath(__file__))
    im1 = cv2.imread(osp.join(testdir, 'images', 'coco_val2017_000139.jpg'))
    im2 = cv2.imread(osp.join(testdir, 'images', 'coco_val2017_455157.jpg'))
    if not with_targets:
        return [im1, im2]
    gt1 = np.array([[236.98, 142.51, 261.68, 212.01], [  7.03, 167.76, 156.35, 262.63],
                    [557.21, 209.19, 638.56, 287.92], [358.98, 218.05, 414.98, 320.88],
                    [290.69, 218.  , 352.52, 316.48], [413.2 , 223.01, 443.37, 304.37],
                    [317.4 , 219.24, 338.98, 230.83], [412.8 , 157.61, 465.85, 295.62],
                    [384.43, 172.21, 399.55, 207.95], [512.22, 205.75, 526.96, 221.72],
                    [493.1 , 174.34, 513.39, 282.65], [604.77, 305.89, 619.11, 351.6 ],
                    [613.24, 308.24, 626.12, 354.68], [447.77, 121.12, 461.74, 143.  ],
                    [549.06, 309.43, 585.74, 399.1 ], [350.76, 208.84, 362.13, 231.39],
                    [412.25, 219.02, 421.88, 231.54], [241.24, 194.99, 255.46, 212.62],
                    [336.79, 199.5 , 346.52, 216.23], [321.21, 231.22, 446.77, 320.15]])
    gt2 = np.array([[243.83, 135.79, 446.04, 308.57], [286.2 , 286.2 , 589.66, 526.38],
                    [159.13, 158.14, 332.87, 504.14], [210.18, 365.73, 459.96, 564.18],
                    [353.8 , 329.35, 634.25, 496.18], [547.34, 322.7 , 640.  , 370.74],
                    [530.89, 257.95, 640.  , 326.39], [274.72, 272.47, 341.06, 299.12]])
    cl1 = np.array([64, 72, 72, 62, 62, 62, 62, 1, 1, 78, 82, 84, 84, 85, 86, 86, 62, 86, 86, 67])
    cl2 = np.array([28, 67, 1, 15, 15, 15, 67, 73])
    return [im1, im2], ([gt1, gt2], [cl1, cl2])