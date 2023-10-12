# SJTU EE208

import math
import numpy as np
import random
import sys
# from GeneralHashFunctions.GeneralHashFunctions import BKDRHash
def BKDRHash(key, seed):
    hash = 0
    for i in range(len(key)):
      hash = (hash * seed) + ord(key[i])
    return hash


class Bitarray:
    def __init__(self, size):
        """ Create a bit array of a specific size """
        self.size = size
        self.bitarray = bytearray(math.ceil(size / 8.))

    def set(self, n):
        """ Sets the nth element of the bitarray """

        index = int(n / 8)
        position = n % 8
        self.bitarray[index] = self.bitarray[index] | 1 << (7 - position)

    def get(self, n):
        """ Gets the nth element of the bitarray """

        index = n // 8
        position = n % 8
        return (self.bitarray[index] & (1 << (7 - position))) > 0


class BloomFilter:
    def __init__(self, capacity=1e8, error = 1e-5) -> None:
        self.capacity = capacity
        self.m = math.ceil(-(capacity * math.log(error) / pow(math.log(2), 2)))
        self.k = math.ceil(0.7 * self.m / self.capacity)
        self.bitarray = Bitarray(self.m)
        self.seed_lst = [random.randint(1, 1000) for _ in range(self.k)]
    
    def add(self, keyword):
       for seed in self.seed_lst:
           idx = BKDRHash(keyword, seed) % self.m
           self.bitarray.set(idx)
    
    def lookup(self, target):
        for seed in self.seed_lst:
            idx = BKDRHash(target, seed) % self.m
            if not self.bitarray.get(idx):
                return False
        
        return True


def get_random_str():
    length = random.randint(1, 20)
    letters = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    letters = list(letters)
    res_str = ''.join([random.choice(letters) for _ in range(length)])
    return res_str


if __name__ == "__main__":
    try:
        num = sys.argv[0]
    except:
        num = 1e5
        
    bloom_filter = BloomFilter(num)
    wordlst = []
    for _ in range(int(1e5)):
        text = get_random_str()
        wordlst.append(text)
        bloom_filter.add(text)
    
    count = 0
    for i in range(int(5e5)):
        print(i)
        text = get_random_str()
        res = bloom_filter.lookup(text)
        if res != (text in wordlst):
            count += 1
    
    p = count / (5e5)
    print(p)