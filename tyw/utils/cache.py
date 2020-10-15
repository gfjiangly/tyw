# -*- encoding:utf-8 -*-
# @Time    : 2019/8/30 11:22
# @Author  : gfjiang
# @Site    : 
# @File    : cache.py
# @Software: PyCharm
import os.path as osp
from collections import OrderedDict
from cvtools import get_files_list


class Cache(object):

    def __init__(self, cache_path, capacity=1000):
        self.cache_path = cache_path
        self._cache = OrderedDict()
        self._capacity = int(capacity)
        if capacity <= 0:
            raise ValueError('capacity must be a positive integer')

        for file in get_files_list(cache_path, file_type='.pkl'):
            self.set(file)

    @property
    def capacity(self):
        return self._capacity

    @property
    def size(self):
        return len(self._cache)

    def put(self, key, val):
        if key in self._cache:
            return
        if len(self._cache) >= self.capacity:
            self._cache.popitem(last=False)
        self._cache[key] = val

    def get(self, key, default=None):
        val = self._cache[key] if key in self._cache else default
        return val

    def set(self, file):
        """文件名（不含后缀）作为键（样本id），路径作为值"""
        key = osp.splitext(osp.basename(file))[0]
        self.put(key, file)
