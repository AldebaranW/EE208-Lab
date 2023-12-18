文件结构：

- code
  - features:用作数据检索的图片feature
  - dataset:图片数据库
    - search_pic:进行图片检索，在文件中替换input为读入图片的路径即可进行比较
    剩下部分功能同示例
- checkpoint:基于resnet20训练checkpoint
- checkpoint_resnet50:基于resnet50训练checkpoint
- lr_ablation:基于不同学习率的函数拟合
- my_experiment:自定义函数的函数拟合
- train_epoch_ablation:基于不同训练epoch的函数拟合
-  final.pth:最终训练结果