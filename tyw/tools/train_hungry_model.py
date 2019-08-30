# -*- encoding:utf-8 -*-
# @Time    : 2019/8/30 20:12
# @Author  : gfjiang
# @Site    : 
# @File    : train_hungry_model.py
# @Software: PyCharm
from tyw.loader.HungryLoader import HungryLoader
from tyw.model.HungryModel import HungryModel
from tyw.configs.config import merge_cfg_from_file


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    hungryDataLoder = HungryLoader()
    X, Y = hungryDataLoder.get_train_data()
    model = HungryModel()
    model.train(X, Y, test_size=0.2)
