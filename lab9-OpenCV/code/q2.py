import cv2
from matplotlib import pyplot as plt
import numpy as np

subject = ['blue', 'green', 'red']
color = ['b', 'g', 'r']

def get_grey_hist(img):
    hist = cv2.calcHist([img],[0],None,[256],[0,256]) 
    
    return hist
    

img1 = cv2.imread('/data/lab9-OpenCV/images/img1.jpg', cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread('/data/lab9-OpenCV/images/img2.jpg', cv2.IMREAD_GRAYSCALE)
img3 = cv2.imread('/data/lab9-OpenCV/images/img3.jpg', cv2.IMREAD_GRAYSCALE)
col1 = get_grey_hist(img1)
col2 = get_grey_hist(img2)
col3 = get_grey_hist(img3)

plt.subplot(1, 3, 1)
plt.plot(col1)
plt.title('img1')
plt.subplot(1, 3, 2)
plt.plot(col2)
plt.title('img2')
plt.subplot(1, 3, 3)
plt.plot(col3)
plt.title('img3')
plt.subplots_adjust(wspace=0.5, hspace=0.5)

plt.savefig("grey.jpg")
plt.show()