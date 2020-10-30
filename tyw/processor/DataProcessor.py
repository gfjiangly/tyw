# -*- encoding:utf-8 -*-
# @Time    : 2019/8/28 16:00
# @Author  : gfjiang
# @Site    : 
# @File    : DataProcessor.py
# @Software: PyCharm
import os.path as osp
import pandas as pd
from tqdm import tqdm
import mmcv
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
    def __init__(self, data_path=None, cache_path=cfg.CACHE.CLEAR):
        """
        首先要加载原始数据，经过初步处理后，分发到各个类中提取特征
        """
        # self.channel_map = {
        #     'CH1': 'PPG',
        #     'CH3': 'SKT',
        #     'CH10': 'ECG',
        #     'CH13': 'EDA'
        # }
        self.channels = {
            'PPG': cfg.PPG.CHANNEL,
            'EDA': cfg.EDA.CHANNEL,
            'ECG': cfg.ECG.CHANNEL,
            'SKT': cfg.SKT.CHANNEL,
        }
        self.channel_map = dict(
            zip(self.channels.values(), self.channels.keys())
        )
        self.dataset = []
        self.files_info = []
        if data_path:
            # 创建了文件名对应清洗后的文件路径的缓存索引
            self._cache = Cache(cache_path)
            print('Loading Dataset...')
            if cfg.PROCESSOR.USE_CLEAR:
                # TODO：这里有问题，待修复
                self.dataset = mmcv.load(data_path)
            else:
                file_list = cvtools.get_files_list(
                    data_path, file_type='.txt')
                for file in tqdm(file_list):
                    file_info = self.parsing_ann(
                        osp.join(cfg.PROCESSOR.ANN_SRC,
                                 osp.basename(file)))
                    self.clear_csv_file(file, file_info)
                    self.files_info.append(file_info)
            self.dataset = self.files_info

    def clear_csv_file(self, file, file_info):
        """从原始数据中加载有用的通道，并保存成pkl格式"""
        file_id = file_info['id']
        if self._cache.get(file_id) is None:
            try:
                data = self.load_data_from_csv(file)
                # 将清洗后的数据保存成pkl文件
                filename = osp.join(cfg.CLEAR_SRC, file_id + '.pkl')
                cvtools.makedirs(filename)
                mmcv.dump(data, filename)
                # 更新干净数据的缓存
                self._cache.put(file_id, filename)
            except Exception as e:
                print(file, e)
        file_info['filename'] = self._cache.get(file_id)
        return file_info

    def get_file_id(self, filename):
        return osp.splitext(osp.basename(filename))[0]

    def parsing_ann(self, filename):
        """解析文件名，生成样本的元信息"""
        file_info = dict()
        file_id = self.get_file_id(filename)
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

    def load_data(self, file):
        """从原始文件中加载数据"""
        file_path = self._cache.get(self.get_file_id(file))
        if file_path is None:
            return self.load_data_from_csv(file)
        else:
            return self.load_data_from_pkl(file_path)

    def load_data_from_csv(self, file):
        """从原始数据中读取有用的通道"""
        with open(file, 'r') as fp:
            raw_data = fp.readlines()
        return self.load_data_from_raw_data(raw_data)

    def load_data_from_raw_data(self, raw_data):
        """从原始数据中清洗出有用的通道"""
        hz_value_str, hz_unit = raw_data[1].split()
        if hz_unit == 'msec/sample':
            hz = int(1000 / float(hz_value_str))
        else:
            hz = cfg.PROCESSOR.HZ  # 信号采样频率
        discard = cfg.PROCESSOR.DISCARD * hz  # 丢弃前后discard个数据
        try:
            data = pd.DataFrame(    # 10分钟150W, 4s1W
                [item.split(',') for item in raw_data[46+discard:-discard]],
                columns=[item.strip() for item in raw_data[45].split(',')])
        except KeyError:
            data = pd.DataFrame(    # 10分钟150W, 4s1W
                [item.split() for item in raw_data[46+discard:-discard]],
                columns=[item.strip() for item in raw_data[45].split()])
        # self.channel_map[data.columns.tolist()[0]] = 'time'
        data = data[self.channel_map.keys()][1:].astype(float)
        # 使用data.columns = []修改不了
        data.rename(columns=self.channel_map, inplace=True)
        return data

    def load_data_from_pkl(self, file):
        """从pkl文件加载数据"""
        return mmcv.load(file)

    def save(self, filename='data_info.json'):
        mmcv.dump(self.dataset, filename)


if __name__ == '__main__':
    cfg_file = '../configs/8-28.yaml'
    merge_cfg_from_file(cfg_file)
    data_processor = DataProcessor(cfg.DATA)
    data_processor.save(filename='E:/tyw-data/original/data_info.json')
