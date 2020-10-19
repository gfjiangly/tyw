# -*- encoding:utf-8 -*-
# @Time    : 2019/8/29 10:47
# @Author  : gfjiang
# @Site    : 
# @File    : HungryLoader.py
# @Software: PyCharm
import numpy as np
import pandas as pd

from tyw.processor.DataProcessor import DataProcessor
from tyw.processor.PPGProcessor import PPGProcessor
from tyw.configs.config import merge_cfg_from_file, cfg


class HungryLoader(DataProcessor):

    def __init__(self, data_path=None):
        super().__init__(data_path)
        self.column_num = cfg.TRAIN.HUNGRY_MODEL.COLUMN_NUM
        self.class_num = cfg.TRAIN.HUNGRY_MODEL.CLASS_NUM
        self.look_back = cfg.TRAIN.HUNGRY_MODEL.LOOK_BACK
        # self.look_back = 4
        self.dataX = []
        self.dataY = []
        if data_path:
            for data in self.dataset:
                if 'hungry' in data:
                    label = data['hungry']
                    self.dataY.append(label)
                    # 筛选含PPG信号文件
                    if 'PPG' in data['signals']:
                        self.dataX.append(data['filename'])
        self.ppg_processor = PPGProcessor(cache=cfg.CACHE.PPG)

    def get_train_data(self, filter_func=None):
        assert len(self.dataX) == len(self.dataY)
        batch_data_X, batch_data_Y = self.prep_train_data(filter_func)
        return batch_data_X, batch_data_Y

    def prep_train_data(self, filter_func=None):
        batch_data_X = np.empty(shape=(0, self.look_back, self.column_num))
        batch_data_Y = np.empty(shape=(0, self.class_num))
        for file, label in zip(self.dataX, self.dataY):
            if filter_func and filter_func(file):
                continue
            # 现在仅用到PPG特征
            ppg_feats = self.ppg_processor.extract_ppg_t(file)
            assert self.column_num == ppg_feats.shape[1]
            X, Y = self._split_data(ppg_feats, label)
            try:
                batch_data_X = np.vstack((batch_data_X, X))  # batch维度
                batch_data_Y = np.vstack((batch_data_Y, Y))
            except ValueError:
                print("特征长度小于窗口大小，跳过此数据：{}".format(file))
                continue
        return batch_data_X, batch_data_Y

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

    def process_test_data(self, ppg):
        feats = self.ppg_processor.extract_feats_from_ppg_parallel(ppg)
        feats = feats['ppg_t']
        feats = feats.values
        overlap = 0.8
        X = []
        if 0 < len(feats) < self.look_back:
            X.append(feats)
        else:
            for i in range(0, len(feats) - self.look_back,
                           int(self.look_back * overlap)):
                a = feats[i:(i + self.look_back)]
                X.append(a)
        if len(X) > 0:
            a = np.zeros(self.look_back)
            a[:len(X[-1])] = X[-1]
            X[-1] = a
        X = np.array(X)
        X = X[..., np.newaxis]
        return X


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    hungryDataLoder = HungryLoader()
    X, Y = hungryDataLoder.get_train_data()
