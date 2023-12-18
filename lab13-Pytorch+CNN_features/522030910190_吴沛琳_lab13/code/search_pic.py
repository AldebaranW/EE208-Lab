import numpy as np
import os
import time

import numpy as np
import torch
import os
import torchvision
import torchvision.transforms as transforms
import cv2
import matplotlib.pyplot as plt
from torchvision.datasets.folder import default_loader

model = torchvision.models.resnet50(pretrained=True)

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
trans = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize,
])

def features(x):
    x = model.conv1(x)
    x = model.bn1(x)
    x = model.relu(x)
    x = model.maxpool(x)
    x = model.layer1(x)
    x = model.layer2(x)
    x = model.layer3(x)
    x = model.layer4(x)
    x = model.avgpool(x)

    return x

def get_top_scores(image_feature, thresh=0.09, feature_path='./features'):
    image_feature = image_feature / (np.linalg.norm(image_feature))

    score = []
    final_name = []
    for feature in os.listdir(feature_path):
        name = feature[:-4]
        feature = os.path.join(feature_path, feature)
        feature = np.load(feature)
        feature = feature / (np.linalg.norm(feature))
        sub = feature - image_feature
        
        score_n = np.linalg.norm(sub)
        if score_n < thresh:
            print(score_n)
            score.sort(reverse=True)
            if len(score) < 5:
                score.append(score_n)
                final_name.append(name)
            else:
                for i in range(5):
                    if score_n < score[i]:
                        score[i] = score_n
                        final_name[i] = name
                        break
    
    return score, final_name
 
input_name = './Dataset/8.jpg' # 输入图片，可以更改
input = default_loader(input_name) 
input_image = trans(input)
input_image = torch.unsqueeze(input_image, 0)

print('Extract features!')
start = time.time()
image_feature = features(input_image)
image_feature = image_feature.detach().numpy()

score, final_name = get_top_scores(image_feature)
for i in range(len(score)):
    print(final_name[i],": ", score[i])


cv2.imshow('input', cv2.imread(input_name))
for name in final_name:
    cv2.imshow('output', cv2.imread('./dataset/' + name))
    cv2.waitKey(3000)