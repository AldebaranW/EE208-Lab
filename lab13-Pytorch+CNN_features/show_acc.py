import matplotlib.pyplot as plt
import numpy as np


acc_resnet20 = [
    41.73,
    46.64,
    60.41,
    58.08,
    55.24,
    67.59,
    65.35,
    50.98,
    71.7,
    69.76,
    73.1,
]
acc_resnet50 = [
    64.05,
    70.9,
    74.98,
    78.55,
    80.16,
    80.31,
    81.39,
    13.06,
    83.35,
    82.31,
    82.61,
]

plt.plot(acc_resnet20, label='resnet20')
plt.plot(acc_resnet50, label='resnet50')
plt.legend()

plt.show()