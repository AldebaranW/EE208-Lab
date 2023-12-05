import cv2
import numpy as np
from math import sin, cos, pi, atan2
import random


class Sift():
    def __init__(self, img) -> None:
        self.width, self.height = np.shape(img)
        self.corners = [
            [int(i[0][0]), int(i[0][1])]
            for i in cv2.goodFeaturesToTrack(img, 300, 0.01, 10)
        ]

        img = cv2.GaussianBlur(img, (3, 3), 1, 1)
        img = np.array(img, dtype="float")

        self.gradient, self.angle = self.get_gradient(img)
        self.bins = (self.width + self.height) // 80

        self.length = len(self.corners)
        self.direction = self.vote_for_direction()

    def __call__(self):
        features = []
        for i in range(self.length):
            val = self.get_feature(self.corners[i], self.direction[i])
            square = sum(v * v for v in val) ** 0.5
            nrom = [v / square for v in val]
            features.append(nrom)
        return features, self.corners, self.length

    def get_gradient(self, img):
        x, y = self.width, self.height

        kernel = (
            np.array([[[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
                     [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]], dtype="float") / 6
        )

        gx = cv2.filter2D(img, -1, np.array(kernel[1]))
        gy = cv2.filter2D(img, -1, np.array(kernel[0]))
        gradient = np.zeros([x, y], "float")
        angle = np.zeros([x, y], "float")
        for i in range(x):
            for j in range(y):
                gradient[i][j] = ((gx[i][j]) ** 2 + (gy[i][j]) ** 2) ** 0.5
                angle[i][j] = atan2(gy[i][j], gx[i][j])
        return gradient, angle

    def vote_for_direction(self):
        direction = []
        for corner in self.corners:
            y, x = corner
            voting = [0 for _ in range(37)]
            for i in range(max(x - self.bins, 0), min(x + self.bins + 1, self.width)):
                for j in range(max(y - self.bins, 0), min(y + self.bins + 1, self.height)):
                    k = int((self.angle[i][j] + pi) / (pi / 18) + 1)
                    if k >= 37:
                        k = 36
                    voting[k] += self.gradient[i][j]
            p = 1
            for i in range(2, 37):
                if voting[i] > voting[p]:
                    p = i
            direction.append((p / 18 - 1 - 1 / 36) * pi)

        return direction

    def get_feature(self, pos, theta):

        def bilinear_interpolation(x, y): # 双线性插值
            def angle(x, y):
                if (x < 0 or x >= self.width) or (y < 0 or y >= self.height):
                    return 0
                dif = self.angle[x][y] - theta
                return dif if dif > 0 else dif + 2 * pi
            
            xx, yy = int(x), int(y)
            dy1, dy2 = y - yy, yy + 1 - y
            dx1, dx2 = x - xx, xx + 1 - x
            res = (
                angle(xx, yy) * dx2 * dy2
                + angle(xx + 1, yy) * dx1 * dy2
                + angle(xx, yy + 1) * dx2 * dy1
                + angle(xx + 1, yy + 1) * dx1 * dy1
            )
            return res

        def count(x1, x2, y1, y2, xsign, ysign, H, V):
            voting = [0 for _ in range(9)]
            for x in range(x1, x2):
                for y in range(y1, y2):
                    dp = [x * xsign, y * ysign]
                    p = H * dp[0] + V * dp[1]
                    bin = int(
                        (bilinear_interpolation(p[0] + x0, p[1] + y0)) // (pi / 4) + 1)
                    if bin > 8:
                        bin = 8
                    voting[bin] += 1
            return voting[1:]

        y0, x0 = pos
        H = np.array([cos(theta), sin(theta)])
        V = np.array([-sin(theta), cos(theta)])

        val = []

        bins = (self.width + self.height) // 150
        for xsign in [-1, 1]:
            for ysign in [-1, 1]:
                val += count(0, bins, 0, bins, xsign, ysign, H, V)
                val += count(bins, bins * 2, 0, bins, xsign, ysign, H, V)
                val += count(bins, bins * 2, bins, bins * 2, xsign, ysign, H, V)
                val += count(0, bins, bins, bins * 2, xsign, ysign, H, V)

        return val


def padding(img1, img2):
    h1, w1, _ = np.shape(img1)
    h2, w2, _ = np.shape(img2)
    if h1 < h2:
        padding = np.array([[[0, 0, 0] for _ in range(w1)]
                            for _ in range(h2 - h1)])
        img1 = np.vstack([img1, padding])
    elif h1 > h2:
        padding = np.array([[[0, 0, 0] for _ in range(w2)]
                            for _ in range(h1 - h2)])
        img2 = np.vstack([img2, padding])

    return np.hstack([img1, img2])


def match_img(threshold, w, imgs, sift_tg, sift_img):
    feature_tg, corner_tg, length_tg = sift_tg()
    features = []
    corners = []
    lengths = []

    for i in range(len(sift_img)):
        sift = sift_img[i]
        feature, corner, length = sift()
        features.append(feature)
        corners.append(corner)
        lengths.append(length)

    for id in range(len(sift_img)):
        x = []
        cnt = 0
        for i in range(length_tg):
            tmp = []
            for j in range(lengths[id]):
                sc = np.dot(np.array(feature_tg[i]), np.array(features[id][j]))
                tmp.append(sc)
            x.append([tmp.index(max(tmp)), max(tmp)])
        for a in range(len(x)):
            b, s = x[a]
            if s < threshold:
                continue
            cnt += 1
            color = (
                (random.randint(0, 255)),
                (random.randint(0, 255)),
                (random.randint(0, 255)),
            )
            cv2.line(
                imgs[id],
                tuple(corner_tg[a]),
                tuple([corners[id][b][0] + w, corners[id][b][1]]),
                color,
                1,
            )
        if cnt > 10:
            print("match" + str(id))
            img = np.array(imgs[id], dtype="uint8")
            cv2.imwrite("./match.jpg", img)
            cv2.imshow("result", img)
            cv2.waitKey(0)


tg = cv2.imread("./target.jpg", cv2.IMREAD_GRAYSCALE)
tg0 = cv2.imread("./target.jpg")
img_lst = [
    cv2.imread("./dataset/" + str(i + 1) + ".jpg", cv2.IMREAD_GRAYSCALE) for i in range(5)
]
img_lst0 = [cv2.imread("./dataset/" + str(i + 1) + ".jpg") for i in range(5)]


sift_tg = Sift(tg)
sifts = []
for i in range(len(img_lst)):
    sift = Sift(img_lst[i])
    sifts.append(sift)

w = np.shape(tg)[1]
pad_imgs = [padding(tg0, img_lst0[i]) for i in range(len(img_lst0))]

match_img(0.8, w, pad_imgs, sift_tg, sifts)
