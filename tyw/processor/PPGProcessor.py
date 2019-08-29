# -*- encoding:utf-8 -*-
# @Time    : 2019/5/13 10:57
# @Author  : gfjiang
# @Site    : 
# @File    : PPGProcess.py
# @Software: PyCharm
import sys
import pandas as pd
from collections import OrderedDict
import os.path as osp
import mmcv
from cvtools import get_files_list

from tyw.configs.config import cfg


class Pulse:
    def __init__(self, index, ppg_h, ppg_l, ppg_t):
        self.index = index
        self.ppg_h = ppg_h
        self.ppg_l = ppg_l
        self.ppg_t = ppg_t


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
        key = osp.splitext(osp.basename(file))[0]
        self.put(key, file)


class PPGProcessor:
    """
    PPG features are processed by LiuChangxin，saved in csv files.
    features are inlcude PPG Waveform extreme max points(PPG_H),
    extreme min points(PPG_L) and cycle(PPG_T).
    """
    def __init__(self, cahce=cfg.PPG.CACHE):
        self._cache = Cache(cahce)

    def extract_feats(self, data=None, file_id=None):
        assert data is not None or file_id is not None
        if file_id is not None:
            cache = self._cache.get(file_id)
            if cache is not None:
                return mmcv.load(cache)
        if isinstance(data, pd.Series):
            ppg = list(data)
            return self._extract_feats(ppg, file_id)
        else:
            print('不支持的参数类型 {}: {}'.format(data, type(data)))
            return None

    def _extract_feats(self, data, file_id=None):
        count = 0
        ppg_h = -sys.maxsize
        max_interval = -sys.maxsize
        ppg_l = sys.maxsize
        min_interval = sys.maxsize
        up_threshold = 0
        interval = 0
        res = []
        for i in range(10000, len(data) - 10000):
            if self._judge(data, i) and interval > 5 * cfg.PPG.THRESHOLD:
                if count != 0:
                    if interval < cfg.PPG.INTERVAL_UP_THRESHOLD:
                        res.append([i, ppg_h, ppg_l, interval])
                    min_interval = min(min_interval, interval)
                    max_interval = max(max_interval, interval)
                    ppg_h = -sys.maxsize
                    ppg_l = sys.maxsize
                    if interval > 3000:
                        up_threshold += 1
                count += 1
                interval = 0
            interval += 1
            ppg_h = max(ppg_h, data[i])
            ppg_l = min(ppg_l, data[i])
        print("max_interval:    " + str(max_interval))
        print("min_interval:    " + str(min_interval))
        print("up_interval_threshold " +
              str(cfg.PPG.INTERVAL_UP_THRESHOLD) + "  :   " + str(up_threshold))
        res = pd.DataFrame(res, dtype=float)
        if file_id is None:
            file = osp.join(self._cache.cache_path, file_id+'.pkl')
            mmcv.dump(res, file)
            self._cache.put(file_id, file)
        return res

    def _judge(self, data, index):
        for i in range(index - cfg.PPG.THRESHOLD, index + cfg.PPG.THRESHOLD):
            if data[index] < data[i]:
                return False
        return True

