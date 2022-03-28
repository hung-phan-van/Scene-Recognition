import torchvision.models as models
import torch
import os
from torchvision import transforms

def load_model(model_name='fixres50', num_classes=365, cuda_device=os.environ['DEVICE']):
    weights_path = './weights'
    model_name_path = '{}/{}'.format(weights_path, model_name)
    checkpoint_path = '{}/{}/checkpoint.pth'.format(weights_path, model_name)

    if not os.path.exists(weights_path):
        os.makedirs(weights_path)
    if not os.path.exists(model_name_path):
        os.makedirs(model_name_path)
    if not os.path.exists(checkpoint_path):
        try:
            os.system("gdown https://drive.google.com/uc?id=1f1oHRT5t-tItQtlXknq4Dd9kH3ubhEV0 -O {}".format(checkpoint_path))
        except:
            return None

    model = models.resnet50(pretrained=False, num_classes=num_classes)
    pretrained_dict=torch.load(checkpoint_path, map_location='cpu')['model']
    model_dict = model.state_dict()
    count=0
    count2=0
    for k in model_dict.keys():
        count=count+1.0
        if(('module.'+k) in pretrained_dict.keys()):
            count2=count2+1.0
            model_dict[k]=pretrained_dict.get(('module.'+k))
    model.load_state_dict(model_dict)
    model.to(cuda_device)
    return model

def build_transform():
    mean, std = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
    transformations = transforms.Compose(
                [transforms.Resize(256),
                 transforms.ToTensor(),
                 transforms.Normalize(mean, std)])
    return transformations
