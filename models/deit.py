import torch

from timm.models import create_model
from models import models

import os
from torchvision import transforms
from timm.data import create_transform
from timm.data.constants import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD


def load_model(model_name='deit_small_patch16_224', nb_classes=365, cuda_device=os.environ['DEVICE']):
    weights_path = './weights'
    model_name_path = '{}/{}'.format(weights_path, model_name)
    checkpoint_path = '{}/{}/checkpoint.pth'.format(weights_path, model_name)

    if not os.path.exists(weights_path):
        os.makedirs(weights_path)
    if not os.path.exists(model_name_path):
        os.makedirs(model_name_path)
    if not os.path.exists(checkpoint_path):
        try:
            os.system("gdown https://drive.google.com/uc?id=1-27_2Fqc0v0tNbmouRF20KrC41E_TYKO -O {}".format(checkpoint_path))
        except:
            return None
    model = create_model(
        model_name,
        pretrained=False,
        num_classes=nb_classes,
        drop_rate=0.0,
        drop_path_rate=0.1,
        drop_block_rate=None,
    )
    # device = torch.device("cuda")
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    checkpoint_model = checkpoint['model']
    state_dict = model.state_dict()
    model.load_state_dict(checkpoint_model, strict=False)
    model.to(cuda_device)
    return model

def build_transform(is_train=False, input_size=224):
    resize_im = input_size > 32
    if is_train:
        transform = create_transform(
            input_size=224,
            is_training=False,
            color_jitter=0.4,
            auto_augment='rand-m9-mstd0.5-inc1',
            interpolation='bicubic',
            re_prob=0.25,
            re_mode='pixel',
            re_count=1,
        )
        if not resize_im:
            # replace RandomResizedCropAndInterpolation with
            # RandomCrop
            transform.transforms[0] = transforms.RandomCrop(
                args.input_size, padding=4)
        return transform

    t = []
    if resize_im:
        size = int((256 / 224) * input_size)
        t.append(
            transforms.Resize(size, interpolation=3),  # to maintain same ratio w.r.t. 224 images
        )
        t.append(transforms.CenterCrop(input_size))

    t.append(transforms.ToTensor())
    t.append(transforms.Normalize(IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD))
    return transforms.Compose(t)
