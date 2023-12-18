import cv2
import numpy as np
import skimage.feature
import os


def compute_one_hot2(array):
    max_val = max(array)
    res = []
    for i in array:
        if i < max_val / 3:
            res.append(0)
        elif i < max_val * 2 / 3:
            res.append(1)
        elif i > max_val * 2 / 3:
            res.append(2)
    
    return res

def compute_one_hot(array):
    res = []
    for i in array:
        if i < 0.3:
            res.append(0)
        elif i < 0.6:
            res.append(1)
        elif i > 0.6:
            res.append(2)
    
    return res


def get_feature(img):
    height, width, _ = np.shape(img)
    pts = []
    pts.append(img[0:(height // 2), 0:(width // 2)])
    pts.append(img[0:(height // 2), (width // 2):])
    pts.append(img[(height // 2):, 0:(width // 2)])
    pts.append(img[(height // 2):, (width // 2):])

    feature = []
    for pt in pts:
        col = []
        col.append(
            sum(i * cv2.calcHist([pt], [0], None, [256], [0, 256])[i] for i in range(256))[0])
        col.append(
            sum(i * cv2.calcHist([pt], [1], None, [256], [0, 256])[i] for i in range(256))[0])
        col.append(
            sum(i * cv2.calcHist([pt], [2], None, [256], [0, 256])[i] for i in range(256))[0])
        col /= sum(col)

        feature.append(col[0])
        feature.append(col[1])
        feature.append(col[2])

    return compute_one_hot(feature)

def get_feature2(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    feature = skimage.feature.hog(img)
    feature = compute_one_hot2(feature)
    return feature[:1000]

tg = cv2.imread('./target.jpg')
paths = './Dataset'
dir = os.listdir(paths)

for path in dir:
    img = cv2.imread(os.path.join(paths, path))
    # feature = get_feature(img)
    feature = get_feature2(img)
# feature = get_feature(tg)
feature = get_feature2(tg)
