# -*- encoding:utf-8 -*-
# @Time    : 2019/8/28 16:00
# @Author  : gfjiang
# @Site    : 
# @File    : DataProcessor.py
# @Software: PyCharm
import os.path as osp
import pandas as pd
from tqdm import tqdm
import cvtools

from tyw.configs.config import merge_cfg_from_file, cfg
from tyw.utils.cache import Cache

# 解决模块调用时代码中使用相对路径访问文件问题
current_path = osp.dirname(__file__) + '/'


class DataProcessor:
    """数据处理类
        将原始txt清理成较干净的pkl保存二进制文件，
        抽取有意义的通道 CH1-PPG; CH3-SKT; CH10-ECG; CH13-EDA。
        Data format:
        [
            {
                'file_id': 'who_date_cat',
                'filename': 'E:/tyw-data/clear/who_date_cat.pkl',
                'original_name': 'xxx',
                'signals': ['PPG', 'EDA', ...],
                'cats': {'hungry': x, 'tired': x, ...}
                'bad': {'PPG': [], 'ECG': []}
            },
            ...
        ]
    """
    def __init__(self, ):
        """
        首先要加载原始数据，经过初步处理后，分发到各个类中提取特征
        """
        self.channel_map = {
            'CH1': 'PPG',
            'CH3': 'SKT',
            'CH10': 'ECG',
            'CH13': 'EDA'
        }
        self.dataset = []
        self._cache = Cache(cfg.CACHE.DATASET)
        print('Loading Dataset...')
        if cfg.PROCESSOR.USE_CLEAR:
            self.dataset = cvtools.load(
                osp.join(cfg.DATA_SRC, 'data_info.json'))
        else:
            file_list = cvtools.get_files_list(
                cfg.DATA_SRC, file_type='.txt')
            for file in tqdm(file_list):
                file_info = self.parsing_ann(
                    osp.join(cfg.ANN_SRC, osp.basename(file)))
                self.split_channels(file, file_info)
                self.dataset.append(file_info)

    def split_channels(self, file, file_info):
        file_id = file_info['id']
        if self._cache.get(file_id) is None:
            try:
                with open(file, 'r') as fp:
                    raw_data = fp.readlines()
                # file_info['original_name'] = raw_data[0].strip()
                data = pd.DataFrame(    # 10分钟150W, 4s1W
                    [item.split() for item in raw_data[46:]],
                    columns=[item.strip() for item in raw_data[45].split()])
                # self.channel_map[data.columns.tolist()[0]] = 'time'
                data = data[self.channel_map.keys()][1:].astype(float)
                # 使用data.columns = []修改不了
                data.rename(columns=self.channel_map, inplace=True)
                # save clear data
                filename = osp.join(cfg.CLEAR_SRC, file_id + '.pkl')
                cvtools.makedirs(filename)
                cvtools.dump(data, filename)
                self._cache.put(file_id, filename)
            except Exception as e:
                print(file, e)
        file_info['filename'] = self._cache.get(file_id)
        return file_info

    def parsing_ann(self, filename):
        file_info = dict()
        file_id = osp.splitext(osp.basename(filename))[0]
        file_info['id'] = file_id
        file_split = file_id.split('_')
        file_info['who'] = file_split[0]
        file_info['time'] = file_split[1]
        try:
            file_info['hungry'] = int(file_split[2])
        except ValueError:
            if cfg.DEBUG:
                print('{}: Hunger tag has no default value'
                      .format(file_id))
        try:
            file_info['tired'] = int(file_split[3])
        except ValueError:
            file_info['tired'] = 0
        try:
            file_info['fear'] = int(file_split[4])
        except ValueError:
            file_info['fear'] = 0

        ann = cvtools.readlines(filename)
        file_info['original_name'] = ann[0].strip()
        file_info['signals'] = [signal.strip()
                                for signal in ann[1].split()]
        file_info['bad'] = dict()
        for signal_ann in ann[2:]:
            signal_ann = signal_ann.split()
            file_info['bad'][signal_ann[0].strip()] = \
                [qun.strip() for qun in signal_ann[1:]]
        return file_info

    def save(self, filename='data_info.json'):
        cvtools.dump(self.dataset, filename)


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    data_processor = DataProcessor()
    data_processor.save(filename='E:/tyw-data/original/data_info.json')
