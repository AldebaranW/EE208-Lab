dataset文件夹中包含了运行结果，其中：

cv_Canny：调用cv2.Canny函数得到的边缘图片
Prewitt: 基于Prewitt算子，在阈值为40, 120的条件下得到的边缘图片
thresh_40_120: 基于Sobel算子（下同），在阈值为40, 120的条件下得到的边缘图片
thresh_160: 在阈值为64， 160的条件下得到的边缘图片
thresh_200: 在阈值为80， 200的条件下得到的边缘图片