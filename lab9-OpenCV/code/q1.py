import cv2
from matplotlib import pyplot as plt
import numpy as np

subject = ['blue', 'green', 'red']
color = ['b', 'g', 'r']

def show_col_bar(img):
    hist1 = cv2.calcHist([img],[0],None,[256],[0,256]) #blue
    hist2 = cv2.calcHist([img],[1],None,[256],[0,256]) # green
    hist3 = cv2.calcHist([img],[2],None,[256],[0,256]) # red

    col = [0, 0, 0]
    for i in range(255):
        col[0] += hist1[i][0] * i
        col[1] += hist2[i][0] * i
        col[2] += hist3[i][0] * i

    col = np.array(col)
    col = col / np.sum(col)
    
    return col

    

img1 = cv2.imread('/data/lab9-OpenCV/images/img1.jpg')
img2 = cv2.imread('/data/lab9-OpenCV/images/img2.jpg')
img3 = cv2.imread('/data/lab9-OpenCV/images/img3.jpg')
col1 = show_col_bar(img1)
col2 = show_col_bar(img2)
col3 = show_col_bar(img3)

plt.subplot(1, 3, 1)
plt.bar(subject, col1, color=color)
plt.title('img1')
plt.subplot(1, 3, 2)
plt.bar(subject, col2, color=color)
plt.title('img2')
plt.subplot(1, 3, 3)
plt.bar(subject, col3, color=color)
plt.title('img3')
plt.subplots_adjust(wspace=0.4, hspace=0.4)

plt.savefig("color.jpg")
plt.show()