# -*- encoding:utf-8 -*-
# @Time    : 2019/8/30 20:12
# @Author  : gfjiang
# @Site    : 
# @File    : train_hungry_model.py
# @Software: PyCharm
import os.path as osp
import numpy as np
from sklearn.metrics import confusion_matrix

from tyw.loader.HungryLoader import HungryLoader
from tyw.model.HungryModel import HungryModel
from tyw.configs.config import merge_cfg_from_file

from tyw.utils.ts_utils import calc_variance


def filter_func(file):
    filename = osp.basename(file)
    who = filename.split('_')[0]
    if who == 'hpc':
        return False
    else:
        return True


def calc_var_threshold(val, y):
    assert len(val) == len(y)
    y = [np.argmax(v) for v in y]   # 由one-hot转换为普通np数组
    init_thr = np.min(val)
    max_thr = np.max(val)
    setp = (max_thr - init_thr) / 100.
    best_correct_num = 0
    cm = None
    best_thr = 0
    for thr in np.arange(init_thr, max_thr, setp):
        result = val > thr
        r = confusion_matrix(y, result)
        correct_num = 0
        for i in range(len(r)):
            correct_num += r[i][i]
        if correct_num > best_correct_num:
            best_correct_num = correct_num
            cm = r
            best_thr = thr
    print("confusion matrix: {}".format(cm))
    return best_thr


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    hungryDataLoder = HungryLoader()
    X, Y = hungryDataLoder.get_train_data(filter_func=filter_func)
    var = calc_variance(X)
    calc_var_threshold(var, Y)
    model = HungryModel()
    model.train(X, Y, test_size=0.2)
