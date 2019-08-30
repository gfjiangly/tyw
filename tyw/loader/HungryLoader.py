# -*- encoding:utf-8 -*-
# @Time    : 2019/8/29 10:47
# @Author  : gfjiang
# @Site    : 
# @File    : HungryLoader.py
# @Software: PyCharm
import os.path as osp
import mmcv
import numpy as np
import pandas as pd

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
            if 'hungry' in data:
                label = data['hungry']
                self.dataY.append(label)
                signals = []
                if 'PPG' in data['signals']:
                    signals = data['filename']
                self.dataX.append(signals)

    def get_train_data(self):
        assert len(self.dataX) == len(self.dataY)
        batch_data_X = np.empty(shape=(0, self.look_back, self.column_num))
        batch_data_Y = np.empty(shape=(0, self.class_num))
        self.prep_train_data(batch_data_X, batch_data_Y)
        return batch_data_X, batch_data_Y

    def prep_train_data(self, batch_data_X, batch_data_Y):
        ppg_processor = PPGProcessor(cache=cfg.PPG.CACHE)
        for file, label in zip(self.dataX, self.dataY):
            # 现在仅用到PPG特征
            file_id = osp.splitext(osp.basename(file))[0]
            data = mmcv.load(file)['PPG']
            ppg_feats = ppg_processor.extract_feats(data, file_id)
            assert self.column_num == ppg_feats.shape[1]
            X, Y = self._split_data(ppg_feats, label)
            batch_data_X = np.vstack((batch_data_X, X))  # batch维度
            batch_data_Y = np.vstack((batch_data_Y, Y))

    def _split_data(self, data, label, overlap=0.8):
        # data类型需要是个array，否则会报ValueError
        if isinstance(data, pd.DataFrame):
            data = data.values
        X = []
        for i in range(0, len(data) - self.look_back, int(self.look_back * overlap)):
            # 这里dataset是numpy数组，逗号前是行操作逗号后是列操作
            a = data[i:(i + self.look_back)]
            X.append(a)
        Y = np.zeros(shape=[len(X), self.class_num], dtype=np.float32)
        if label >= self.class_num:
            label = self.class_num - 1
        Y[:, label] = 1  # one hot encode
        return np.array(X), Y


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    hungryDataLoder = HungryLoader()
    X, Y = hungryDataLoder.get_train_data()
