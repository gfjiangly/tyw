# -*- encoding:utf-8 -*-
# @Time    : 2019/5/13 10:57
# @Author  : gfjiang
# @Site    : 
# @File    : PPGProcess.py
# @Software: PyCharm
import sys
import pandas as pd
import os.path as osp
import mmcv
import cvtools
from sklearn.preprocessing import MinMaxScaler

from tyw.configs.config import cfg
from tyw.utils.cache import Cache
from tyw.utils.draw import draw_dataframe


class Pulse:
    def __init__(self, index, ppg_h, ppg_l, ppg_t):
        self.index = index
        self.ppg_h = ppg_h
        self.ppg_l = ppg_l
        self.ppg_t = ppg_t


class PPGProcessor:
    """
    PPG features are processed by LiuChangxin，saved in csv files.
    features are inlcude PPG Waveform extreme max points(PPG_H),
    extreme min points(PPG_L) and cycle(PPG_T).
    """
    def __init__(self, cache=cfg.CACHE.PPG):
        self._cache = Cache(cache)
        self.feat_name = ['index', 'ppg_h', 'ppg_l', 'ppg_t']

    def extract_ppg_t(self, file):
        """废弃"""
        return self.extract_ppg_t_from_file(file)

    def extract_ppg_t_from_file(self, file):
        ppg_feats = self.extract_feats(file)
        ppg_feats = ppg_feats['ppg_t'].to_frame()
        scaler = MinMaxScaler(feature_range=(0, 1))
        feats = scaler.fit_transform(ppg_feats.values)
        return feats

    def extract_ppg_t_from_ppg(self, ppg):
        ppg_feats = self.extract_feats_from_ppg(ppg)
        ppg_feats = ppg_feats['ppg_t'].to_frame()
        scaler = MinMaxScaler(feature_range=(0, 1))
        feats = scaler.fit_transform(ppg_feats.values)
        return feats

    def extract_feats(self, file):
        """废弃"""
        return self.extract_feats_from_file(file)

    def extract_feats_from_file(self, file):
        file_id = osp.splitext(osp.basename(file))[0]
        cache = self._cache.get(file_id)
        if cache is not None:
            feats = mmcv.load(cache)
        else:
            data = mmcv.load(file)['PPG']
            ppg = list(data)
            feats = self._extract_feats(ppg)
            if file_id is not None:
                file = osp.join(self._cache.cache_path, file_id + '.pkl')
                cvtools.makedirs(file)
                mmcv.dump(feats, file)
                self._cache.put(file_id, file)
        if cfg.DRAW.PPG:
            self.draw(file_id, feats)
        return feats

    def extract_feats_from_ppg(self, ppg):
        feats = self._extract_feats(ppg)
        if cfg.DRAW.PPG:
            filename = cvtools.get_time_str()
            self.draw(filename, feats)
        return feats

    def _extract_feats(self, data):
        if cfg.PPG.ORIGIN_DISCARD > 0:
            data = data[cfg.PPG.ORIGIN_DISCARD:-cfg.PPG.ORIGIN_DISCARD]
        data = data.reset_index(drop=True)
        count = 0
        ppg_h = -sys.maxsize
        max_interval = -sys.maxsize
        ppg_l = sys.maxsize
        min_interval = sys.maxsize
        up_threshold = 0
        interval = 0
        res = []
        for i in range(cfg.PPG.THRESHOLD, len(data) - cfg.PPG.THRESHOLD):
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
        if cfg.DEBUG:
            print("max_interval:    " + str(max_interval))
            print("min_interval:    " + str(min_interval))
            print("up_interval_threshold " +
                  str(cfg.PPG.INTERVAL_UP_THRESHOLD) + "  :   "
                  + str(up_threshold))
        res = pd.DataFrame(res, columns=self.feat_name, dtype=float)
        return res

    def _judge(self, data, index):
        """判断是否为极大值点"""
        for i in range(index - cfg.PPG.THRESHOLD, index + cfg.PPG.THRESHOLD):
            if data[index] < data[i]:
                return False
        return True

    def draw(self, file_id, feats):
        draw_dataframe(feats, ['ppg_t'],
                       dst=osp.join(cfg.DRAW.PPG_PATH, file_id+'.png'))


