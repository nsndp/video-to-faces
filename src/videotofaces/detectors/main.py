from enum import Enum, auto

import torch

from .rcnn import FasterRCNN
from .retina import RetinaNet_TorchVision, RetinaFace_Biubug6, RetinaFace_BBT
from .yolo import YOLOv3
from .ssd import SSD


class Detector():

    def __init__(self, modelnum, device=None):
        if device is None:
            dv = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        else:
            dv = device

        architecture = modelnum.name.split('_')[0]

        print('Initializing %s model for object detection' % architecture)

        if architecture == 'FasterRCNN':
            source, variation = modelnum.name.lower().split('_', 2)[1:3]
            source = 'tv' if source == 'torchvision' else 'mm'
            self.model = FasterRCNN(source + '_' + variation, dv)
        elif architecture == 'RetinaNet':
            self.model = RetinaNet_TorchVision(dv)
        elif architecture == 'RetinaFace':
            parts = modelnum.name.lower().split('_')
            source, variation = parts[1:3]
            if source == 'biubug6':
                self.model = RetinaFace_Biubug6(variation == 'mobilenet', variation, dv)
            elif source == 'bbt':
                self.model = RetinaFace_BBT(variation == 'resnet50', '_'.join(parts[-2:]), dv)
        elif architecture == 'YOLOv3':
            parts = modelnum.name.lower().split('_')[1:]
            dataset = parts[0]
            bbone = parts[1] if len(parts) > 1 else 'darknet'
            csize = int(parts[2]) if len(parts) > 2 else 608
            n = 80 if dataset == 'coco' else 1
            self.model = YOLOv3(bbone, csize, n, '_'.join(parts), dv)
        elif architecture == 'SSD':
            parts = modelnum.name.lower().split('_')[1:]
            canvas_size = int(parts[0])
            source = parts[1]
            num_classes = 90 if source == 'torchvision' else 80
            self.model = SSD(canvas_size, num_classes, source, dv)
        
        self.model.eval()

    def __call__(self, imgs):
        with torch.inference_mode():
            return self.model(imgs)


class detmodels(Enum):
    FasterRCNN_TorchVision_ResNet50_v1 = auto()
    FasterRCNN_TorchVision_ResNet50_v2 = auto()
    FasterRCNN_TorchVision_MobileNetV3L_HiRes = auto()
    FasterRCNN_TorchVision_MobileNetV3L_LoRes = auto()
    FasterRCNN_MMDet_ResNet50 = auto()
    FasterRCNN_MMDet_ResNet50_AnimeFaces = auto()
    RetinaNet = auto()
    RetinaFace_Biubug6_MobileNet = auto()
    RetinaFace_Biubug6_ResNet50 = auto()
    RetinaFace_BBT_ResNet50_Mixed = auto()
    RetinaFace_BBT_ResNet50_Wider = auto()
    RetinaFace_BBT_ResNet50_iCartoon = auto()
    RetinaFace_BBT_ResNet152_Mixed = auto()
    YOLOv3_Anime = auto()
    YOLOv3_Wider = auto()
    YOLOv3_COCO_Darknet = auto()
    YOLOv3_COCO_Mobile2_416 = auto()
    YOLOv3_COCO_Mobile2_320 = auto()
    SSD_300_TorchVision = auto()
    SSD_300_MMDetection = auto()
    SSD_512_MMDetection = auto()