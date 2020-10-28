# -*- encoding:utf-8 -*-
# @Time    : 2020/10/28 15:23
# @Author  : jiang.g.f
import numpy as np
import pandas as pd

from tyw.processor.DataProcessor import DataProcessor
from tyw.processor.ECGProcessor import ECGProcess
from tyw.configs.config import merge_cfg_from_file, cfg


class FitnessLoader(DataProcessor):

    def __init__(self, data_path=None):
        super().__init__(data_path)
        self.ecg_processor = ECGProcess()

    def process_test_data(self, ecg):
        return self.ecg_processor.extract_heart_rate(ecg)


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    fitnessDataLoder = FitnessLoader()
