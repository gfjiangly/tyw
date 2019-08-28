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
                'filename': 'E:/tyw-data/clear/who_date_cat.txt',
                'original_name': 'xxx'
            },
            ...
        ]
    """
    def __init__(self, ):
        """
        首先要加载原始数据，经过初步处理后，分发到各个类中提取特征
        """
        self.channel_map = {
            'min': 'time',
            'CH1': 'PPG',
            'CH3': 'SKT',
            'CH10': 'ECG',
            'CH13': 'EDA'
        }
        self.dataset = []
        if cfg.PROCESSOR.USE_CLEAR:
            self.dataset = cvtools.load(
                osp.join(cfg.DATA_SRC, 'data_info.json'))
        else:
            file_list = cvtools.get_files_list(cfg.DATA_SRC, file_type='txt')
            for file in tqdm(file_list):
                file_info = self.split_channels(file)
                self.dataset.append(file_info)

    def split_channels(self, file):
        file_info = dict()
        file_id = osp.splitext(osp.basename(file))[0]
        file_info['id'] = file_id
        with open(file, 'r') as fp:
            raw_data = fp.readlines()
        file_info['original_name'] = raw_data[0].strip()
        data = pd.DataFrame(    # 10分钟150W, 4s1W
            [item.split() for item in raw_data[46:]],
            columns=[item.strip() for item in raw_data[45].split()])
        data = data[self.channel_map.keys()]
        # 使用data.columns = []修改不了
        data.rename(columns=self.channel_map, inplace=True)
        data = data[cfg.PROCESSOR.DISCARD:]
        # save clear data
        filename = osp.join(cfg.DATA_SRC, 'clear', file_id+'.pkl')
        cvtools.makedirs(filename)
        cvtools.dump(data, filename)
        file_info['filename'] = filename
        return file_info

    def save(self):
        filename = osp.join(cfg.DATA_SRC, 'data_info.json')
        cvtools.dump(self.dataset, filename)


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    data_processor = DataProcessor()
    data_processor.save()
