# -*- encoding:utf-8 -*-
# @Time    : 2019/8/29 10:47
# @Author  : gfjiang
# @Site    : 
# @File    : HungryLoader.py
# @Software: PyCharm
import mmcv
import numpy as np

from tyw.processor.DataProcessor import DataProcessor
from tyw.processor.PPGProcessor import PPGProcessor
from tyw.configs.config import merge_cfg_from_file, cfg


class HungryLoader(DataProcessor):

    def __init__(self):
        super().__init__()
        self.column_num = cfg.TRAIN.HUNGRY_MODEL.COLUMN_NUM
        self.class_num = cfg.TRAIN.HUNGRY_MODEL.CLASS_NUM
        self.look_back = cfg.TRAIN.HUNGRY_MODEL.LOOK_BACK
        self.dataX = []
        self.dataY = []
        for data in self.dataset:
            if 'PPG' in data['signals']:
                ppg = mmcv.load(data['signals'])
                self.dataX.append(ppg)
            if 'hungry' in data['cats']:
                label = data['cats']['hungry']
                self.dataY.append(label)

    def get_train_data(self):
        assert len(self.dataX) == len(self.dataY)
        batch_data_X = np.empty(shape=(0, self.look_back, self.column_num))
        batch_data_Y = np.empty(shape=(0, self.class_num))
        self.prep_train_data(batch_data_X, batch_data_Y)
        return batch_data_X, batch_data_Y

    def prep_train_data(self, batch_data_X, batch_data_Y):
        pass


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    hungryDataLoder = HungryLoader()
    X, Y = hungryDataLoder.get_train_data()
