# -*- encoding:utf-8 -*-
# @Time    : 2020/10/12 23:55
# @Author  : jiang.g.f
from tyw.processor.DataProcessor import DataProcessor
from tyw.processor.EDAProcessor import EDAProcess


class FearLoader(DataProcessor):

    def __init__(self):
        super().__init__()
        self.eda_processor = EDAProcess('test')

    def process_test_data(self, eda):
        return self.eda_processor.extract_feats_from_eda(eda)


if __name__ == '__main__':
    pass
