# -*- encoding:utf-8 -*-
# @Time    : 2019/5/15 10:38
# @Author  : gfjiang
# @Site    :
# @File    : EDAProcess.py
# @Software: PyCharm
import os.path as osp
import pandas as pd
import numpy as np
import cvtools
import tsfresh.feature_extraction.feature_calculators as ts_feature

from tyw.utils.ts_utils import down_sample
from tyw.configs.config import cfg
from tyw.utils.draw import draw_dataframe, draw_dataframe_list

# 解决模块调用时代码中使用相对路径访问文件问题
current_path = osp.dirname(__file__) + '/'


class EDAProcess:

    def __init__(self, eda_data=None):
        self.eda_data = eda_data
        self.downsample_eda = None
        self.features_dict = {
            'mean': [],
            'maximum': [],
            'minimum': [],
            'max-min': []
        }
        self.look_back = cfg.EDA.LOOK_BACK
        self.overlap = 0.1
        self.down_sample = cfg.EDA.DOWN_SAMPLE
        self.data_fragments = self.gen_data_frames()
        self.unfear_th = None
        self.fear_th = None
        self.stat_files_mean = {'fear': [], 'normal': []}
        self.color_list = []

    def set_eda_data(self, eda_data):
        self.eda_data = eda_data
        self.data_fragments = self.gen_data_frames()
        self.color_list = []

    def gen_data_frames(self):
        data_fragments = []
        if self.eda_data is not None:
            data = self.eda_data.to_frame()
            self.downsample_eda = down_sample(data, interval=self.down_sample)
            step = int(self.look_back * (1 - self.overlap))
            for i in range(0, len(self.downsample_eda) - self.look_back, step):
                a = self.downsample_eda[i:(i + self.look_back)]
                data_fragments.append(a)
        return data_fragments

    def extract_feata(self):
        self._extract_feats()

    def _extract_feats(self):
        for i in range(len(self.data_fragments)):
            a = self.data_fragments[i]
            # 转置(或transpose)之后可能会出现某一维shape为1（如一行转成一列）
            # 因此需要去掉多余维度，否则可能会带来一些切片问题x[np.argmax(x)]越界问题
            # x = a.values.transpose((1, 0))    # 等同于.T
            x = a.values.T
            x = np.squeeze(x)
            feature_dict = {}

            if cfg.EDA.FEATS_MEAN:
                mean = ts_feature.mean(x)
                # mean_change只能按行处理，
                # 内部用的np.diff函数并没有指定axis，
                # 所以只有一列时，np.diff是空，最后得到nan
                mean_change = ts_feature.mean_change(x)
                feature_dict['mean'] = float('%.6f' % mean)
                feature_dict['mean_change'] = float('%.6f' % mean_change)
                self.features_dict['mean'].append(mean)

            if cfg.EDA.FEATS_MAX_MIN:
                # maximum = ts_feature.maximum(x)
                # minimum = ts_feature.minimum(x)
                max_index = np.argmax(x)
                maximum = x[max_index]
                min_index = np.argmin(x)
                minimum = x[min_index]
                feature_dict['maximum'] = float('%.6f' % maximum)
                feature_dict['minimum'] = float('%.6f' % minimum)
                self.features_dict['maximum'].append(maximum)
                self.features_dict['minimum'].append(minimum)
                self.features_dict['max-min'].append(maximum - minimum)
                if maximum - minimum > 1:
                    if max_index > min_index:
                        self.color_list.append(1)
                    else:
                        self.color_list.append(2)
                else:
                    self.color_list.append(0)

        for feat in self.features_dict:
            self.features_dict[feat] = np.array(self.features_dict[feat])

    def extract_feats_from_eda(self, eda_data):
        self.set_eda_data(eda_data)
        self._extract_feats()
        return self.features_dict

    def config_params_with_label(self, eda_data, fear_label):
        """根据有label的信号，校准阈值"""
        self.set_eda_data(eda_data)
        self._extract_feats()
        num = len(self.data_fragments)
        learn_max_min = []
        for i in range(len(self.data_fragments)):
            a = self.data_fragments[i]
            x = np.squeeze(a.values.T)
            # 只统计前一半的片段，这是因为样本采集过程，
            # 用户手抖动对于信号采集影响很大
            if i < num // 2:
                max_index = np.argmax(x)
                maximum = x[max_index]
                min_index = np.argmin(x)
                minimum = x[min_index]
                learns = []
                # 不断降低阈值，对于fear样本，超阈值数量会越来越多
                # 对于unfear样本，超阈值数量变换不明显
                for max_min_threshold in np.arange(2., 0., -0.1):
                    if maximum - minimum > max_min_threshold and \
                            max_index > min_index:
                        # 出现恐惧
                        learns.append(1)
                    else:
                        learns.append(0)
                learn_max_min.append(learns)
        # TODO: 有问题，待解决
        learn_max_min = np.array(learn_max_min)
        learn_max_min_sum = np.sum(learn_max_min, axis=0)
        # 大于阈值为True，小于阈值为False
        position = np.where(learn_max_min_sum > 0)[0]

        if fear_label == 0:
            if len(position) > 0:
                #
                self.unfear_th = 0.1 * (20 - position[0] + 1)
            else:
                self.unfear_th = 0.1
            self.fear_th = self.unfear_th + 0.2
        else:
            if len(position) > 0:
                self.fear_th = 0.1 * (20 - position[0] - 1)
            else:
                self.fear_th = 0.3
            self.unfear_th = self.fear_th - 0.2
            if self.unfear_th < 0.1:
                self.unfear_th = 0.1

    def draw(self, save_name=None):
        if save_name is None:
            save_name = cvtools.get_time_str()
        if cfg.DRAW.EDA_FEATURES:
            features = pd.DataFrame(self.features_dict)
            save = osp.join(cfg.DRAW.PATH, 'eda', save_name, 'features.png')
            draw_dataframe(features,
                           ('mean', 'maximum', 'minimum', 'max-min'),
                           im_size=(40, 10),
                           dst=save)
        if cfg.DRAW.EDA_WHOLE:
            num_frames = len(self.data_fragments)
            if cfg.EDA.FEATS_MAX_MIN:  # 使用到的color_list是根据此特征计算
                # 使用不同颜色标注片段
                save = osp.join(cfg.DRAW.PATH, 'eda', save_name,
                                'eda_color.png')
                draw_dataframe_list(self.data_fragments,
                                    self.color_list,
                                    ('EDA',),
                                    im_size=(num_frames, 10),
                                    dst=save,
                                    tick_spacing=100)
            else:
                save = osp.join(cfg.DRAW.PATH, 'eda', save_name, 'eda.png')
                draw_dataframe(self.downsample_eda, ('EDA',), dst=save,
                               im_size=(num_frames, 10))


if __name__ == '__main__':
    from tyw.processor.DataProcessor import DataProcessor
    data_processor = DataProcessor()
    eda_processor = EDAProcess()
    # 测试见FearLoader.py
