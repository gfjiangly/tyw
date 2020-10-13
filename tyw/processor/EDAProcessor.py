# -*- encoding:utf-8 -*-
# @Time    : 2019/5/15 10:38
# @Author  : gfjiang
# @Site    :
# @File    : EDAProcess.py
# @Software: PyCharm
import os.path as osp
import pandas as pd
import numpy as np
import tsfresh.feature_extraction.feature_calculators as ts_feature

from tyw.utils.ts_utils import down_sample
from tyw.configs.config import cfg
from tyw.utils.draw import draw_dataframe, draw_dataframe_list
from tyw.utils.cache import Cache

# 解决模块调用时代码中使用相对路径访问文件问题
current_path = osp.dirname(__file__) + '/'


class EDAProcess:

    def __init__(self, phase, eda_data=None):
        """
        eda_data is a list, [dict, dict, ...]
        """
        self.phase = phase
        self.eda_data = eda_data
        self.stat_files_mean = {'fear': [], 'nomal': []}

    def extract_feats_from_eda(self, eda_data):
        data = eda_data.to_frame()
        data = down_sample(data, interval=cfg.EDA.DOWN_SAMPLE)
        look_back = cfg.EDA.LOOK_BACK
        features_dict = {
            'mean': [],
            'maximum': [],
            'minimum': [],
            'max-min': []
        }

        data_fragments = []
        color_list = []
        for i in range(0, len(data) - look_back, int(look_back * 0.9)):
            a = data[i:(i + look_back)]
            data_fragments.append(a)
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
                features_dict['mean'].append(mean)

            if cfg.EDA.FEATS_MAX_MIN:
                # maximum = ts_feature.maximum(x)
                # minimum = ts_feature.minimum(x)
                max_index = np.argmax(x)
                maximum = x[max_index]
                min_index = np.argmin(x)
                minimum = x[min_index]
                feature_dict['maximum'] = float('%.6f' % maximum)
                feature_dict['minimum'] = float('%.6f' % minimum)
                features_dict['maximum'].append(maximum)
                features_dict['minimum'].append(minimum)
                features_dict['max-min'].append(maximum - minimum)
                if maximum - minimum > 1:
                    if max_index > min_index:
                        color_list.append(1)
                    else:
                        color_list.append(2)
                else:
                    color_list.append(0)
        for feat in features_dict:
            features_dict[feat] = np.array(features_dict[feat])
        return features_dict

    def extract_feats(self, eda_data, file_id=None):
        """
        eda_data is a dict, dict{'data': DataFrame, 'file_id': str, 'category_id': int}
        """
        data = eda_data.to_frame()
        # file_id = eda_data['file_id']
        file_name = osp.splitext(file_id)[0]
        if self.phase != 'test':
            try:
                file_label = int(file_name.split('_')[-2])
            except IndexError:
                print('{}文件命名有误!'.format(file_id))

        data = down_sample(data, interval=cfg.EDA.DOWN_SAMPLE)
        look_back = cfg.EDA.LOOK_BACK
        features_dict = {
            'mean': [],
            'maximum': [],
            'minimum': [],
            'max-min': []
        }

        im_index = 0

        data_fragments = []
        color_list = []

        learn_max_min = []

        num = len(range(0, len(data) - look_back, int(look_back * 0.9)))

        for i in range(0, len(data) - look_back, int(look_back * 0.9)):
            a = data[i:(i + look_back)]
            data_fragments.append(a)
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
                features_dict['mean'].append(mean)

            if cfg.EDA.FEATS_MAX_MIN:
                # maximum = ts_feature.maximum(x)
                # minimum = ts_feature.minimum(x)
                max_index = np.argmax(x)
                maximum = x[max_index]
                min_index = np.argmin(x)
                minimum = x[min_index]
                feature_dict['maximum'] = float('%.6f' % maximum)
                feature_dict['minimum'] = float('%.6f' % minimum)
                features_dict['maximum'].append(maximum)
                features_dict['minimum'].append(minimum)
                features_dict['max-min'].append(maximum - minimum)
                if maximum - minimum > 1:
                    if max_index > min_index:
                        color_list.append(1)
                    else:
                        color_list.append(2)
                else:
                    color_list.append(0)

            if cfg.EDA.FEATS_LEARN and im_index < num // 2:
                max_index = np.argmax(x)
                maximum = x[max_index]
                min_index = np.argmin(x)
                minimum = x[min_index]
                learns = []
                for max_min_threshold in np.arange(2., 0., -0.1):
                    if maximum - minimum > max_min_threshold and max_index > min_index:
                        learns.append(1)
                    else:
                        learns.append(0)
                learn_max_min.append(learns)

            if cfg.DRAW.EDA_FRAGMENTS:
                save = osp.join(cfg.DRAW.PATH, 
                                'eda/'+file_name+'/'+str(im_index)+'.png')
                draw_dataframe(a,
                               save,
                               ('EDA', ),
                               im_size=(20, 10),
                               show_value=feature_dict)

            im_index += 1

        if cfg.EDA.FEATS_LEARN:
            learn_max_min = np.array(learn_max_min)
            learn_max_min_sum = np.sum(learn_max_min, axis=0)
            position = np.where(learn_max_min_sum > 0)[0]   # 此函数返回的是一个元组
            if self.phase != 'test':
                if file_label == 0:
                    if len(position) > 0:
                        features_dict['unfear_TH'] = 0.1 * (20 - position[0] + 1)
                    else:
                        features_dict['unfear_TH'] = 0.1
                    features_dict['fear_TH'] = features_dict['unfear_TH'] + 0.2
                else:
                    if len(position) > 0:
                        features_dict['fear_TH'] = 0.1 * (20 - position[0] - 1)
                    else:
                        features_dict['fear_TH'] = 0.3
                    features_dict['unfear_TH'] = features_dict['fear_TH'] - 0.2
                    features_dict['unfear_TH'] = 0.1 \
                        if features_dict['unfear_TH'] < 0.1 \
                        else features_dict['unfear_TH']
                print('{}: {}, fear_TH: {}, unfear_TH: {}'.format(
                    file_id, learn_max_min_sum,
                    features_dict['fear_TH'],
                    features_dict['unfear_TH']))

        if cfg.EDA.STAT_FILES_MEAN:
            mean = ts_feature.mean(data.values)
            if self.phase != 'test':
                if file_label == 1:
                    self.stat_files_mean['fear'].append(mean)
                elif file_label == 0:
                    self.stat_files_mean['nomal'].append(mean)

        if cfg.DRAW.EDA_FEATURES:
            features = pd.DataFrame(features_dict)
            save = osp.join(cfg.DRAW.PATH,
                            'eda/' + file_name + '/' + str(im_index) + '.png')
            draw_dataframe(features,
                           save,
                           ('mean', 'maximum', 'minimum', 'max-min'),
                           im_size=(40, 10))

        if cfg.DRAW.EDA_WHOLE:
            if cfg.EDA.FEATS_MAX_MIN:  # 使用到的color_list是根据此特征计算
                # 使用不同颜色标注片段
                save = osp.join(cfg.DRAW.PATH,
                                'eda/' + file_name + '/' + str(im_index) + '.png')
                draw_dataframe_list(data_fragments, 
                                    color_list,
                                    save,
                                    ('EDA', ), 
                                    im_size=(im_index, 10), 
                                    tick_spacing=100)
            save = osp.join(cfg.DRAW.PATH,
                            'eda/' + file_name + '/' + str(im_index) + '.png')
            draw_dataframe(data, save,
                           ('EDA',), im_size=(im_index, 10))

        for feat in features_dict:
            features_dict[feat] = np.array(features_dict[feat])
        return features_dict

    def draw_files(self):
        if cfg.DRAW.EDA_FILES_MEAN:
            files_feature_mean = [pd.DataFrame(self.stat_files_mean[key], columns=['EDA'])
                                  for key in self.stat_files_mean]
            save = osp.join(cfg.DRAW.PATH, 'eda.png')
            draw_dataframe_list(files_feature_mean, 
                                [1, 0],
                                save,
                                ('EDA',), 
                                im_size=(20, 10), 
                                tick_spacing=100)
