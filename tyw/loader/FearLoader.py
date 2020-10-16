# -*- encoding:utf-8 -*-
# @Time    : 2020/10/12 23:55
# @Author  : jiang.g.f
from tyw.processor.DataProcessor import DataProcessor
from tyw.processor.EDAProcessor import EDAProcess


class FearLoader(DataProcessor):

    def __init__(self):
        super().__init__()
        self.files = []
        self.labels = []
        for file_info in self.files_info:
            if 'fear' in file_info:
                label = file_info['fear']
                self.labels.append(label)
                # 筛选含EDA信号文件
                if 'EDA' in file_info['signals']:
                    self.files.append(file_info['filename'])

    def process_train_data(self, filter_func=None):
        assert len(self.files) == len(self.labels)
        for file, label in zip(self.files, self.labels):
            if filter_func and filter_func(file):
                continue
            data = self.load_data(file)
            eda_processor = EDAProcess(data['EDA'])
            eda_processor.extract_feata()
            eda_processor.draw(self.get_file_id(file))

    def process_test_data(self, eda):
        eda_processor = EDAProcess(eda)
        return eda_processor.extract_feats_from_eda(eda)


if __name__ == '__main__':
    from tyw.configs.config import merge_cfg_from_file
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    fear_loader = FearLoader()
    fear_loader.process_train_data()
