import cv2
import numpy as np


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


tg = cv2.imread('./target.jpg')
feature = get_feature(tg)
