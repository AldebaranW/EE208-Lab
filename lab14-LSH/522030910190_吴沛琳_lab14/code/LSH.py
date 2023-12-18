import numpy as np
from pre_process import get_feature, get_feature2
import cv2
import os


class LSH:

    def __init__(self, tables_num: int, C: int):
        self.tables_num = tables_num
        self.C = C
        self.num = []
        for i in range(C + 1):
            self.num.append('1' * i + '0' * (C - i))
        self.hash_tables = [dict() for _ in range(tables_num)]
        self.I = np.random.randint(12, size=int(np.log2(tables_num)))

    def hash(self, input):
        project = ''.join([self.num[input[i]] for i in range(len(input))])
        hash_val = ''.join([project[i] for i in self.I])
        hash_val = int(hash_val, base=2)
        
        return hash_val

    def insert(self, inputs, index):
        inputs = np.array(inputs)

        hash_index = self.hash(inputs)
        self.hash_tables[hash_index].setdefault(tuple(inputs.tolist()), []).append(index)
        

    def query(self, inputs, nums=3):
        inputs = np.array(inputs)
        hash_val = self.hash(inputs)
        candidate_dict = self.hash_tables[hash_val]

        candidates = sorted(
            candidate_dict, key=lambda x: self.euclidean_dis(x, inputs))
        
        res = []
        for i in candidates[:nums]:
            res += candidate_dict[i] 
        
        return res[:nums]

    @staticmethod
    def euclidean_dis(x, y):
        x = np.array(x)
        y = np.array(y)

        return np.sqrt(np.sum(np.power(x - y, 2)))


lsh = LSH(16, 2)

paths = './Dataset'
dir = os.listdir(paths)

for path in dir:
    img = cv2.imread(os.path.join(paths, path))
    feature = get_feature2(img)
    # feature = get_feature2(img)
    lsh.insert(feature, path)

# for path in dir:
#     print(path)
#     tg = cv2.imread(os.path.join(paths, path))
#     # feature = get_feature(tg)
#     feature = get_feature2(tg)
#     res = np.array(lsh.query(feature))
#     print(res)

tg = cv2.imread('./target.jpg')
feature = get_feature2(tg)
res = np.array(lsh.query(feature))
print(res)
