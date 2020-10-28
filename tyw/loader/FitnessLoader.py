# -*- encoding:utf-8 -*-
# @Time    : 2020/10/28 15:23
# @Author  : jiang.g.f
import numpy as np
import pandas as pd

from tyw.processor.DataProcessor import DataProcessor
from tyw.processor.PPGProcessor import PPGProcessor
from tyw.configs.config import merge_cfg_from_file, cfg


class FitnessLoader(DataProcessor):

    def __init__(self, data_path=None):
        super().__init__(data_path)
        self.dataX = []
        if data_path:
            for data in self.dataset:
                # 筛选含PPG信号文件
                if 'PPG' in data['signals']:
                    self.dataX.append(data['filename'])
        self.ppg_processor = PPGProcessor(cache=cfg.CACHE.PPG)

    def process_test_data(self, ppg):
        feats = self.ppg_processor.extract_feats_from_ppg_parallel(ppg)
        feats = feats['ppg_t']
        feats = feats.values
        return feats


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    fitnessDataLoder = FitnessLoader()
