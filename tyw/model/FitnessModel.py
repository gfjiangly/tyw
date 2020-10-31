# -*- encoding:utf-8 -*-
# @Time    : 2020/10/28 13:51
# @Author  : jiang.g.f
import numpy as np
import pandas as pd
import os.path as osp

from tyw.configs.config import merge_cfg_from_file, cfg
from tyw.loader.HungryLoader import HungryLoader


class FitnessModel(object):
    """
    男子最高心率=205-年龄。女子最高心率=220-年龄。国际一般用220 - 年龄所得值为最大心率。
    最高心率的60%~85%是合适有效的运动心率范围。
    """
    def __init__(self, person_info):
        self.person_info = person_info
        if 'min_beats' in person_info:
            self.min_heart_rate = int(person_info['min_beats'])
        else:
            self.min_heart_rate = cfg.TEST.FITNESS_MODEL.MIN_HEART_RATE
        self.max_heart_rate = int(person_info['max_beats'])
        self.body_weight = float(person_info['weight'])
        self.heart_rate_diff = self.max_heart_rate - self.min_heart_rate
        self.calories_o2 = [
            (5.7, 40.),
            (8.8, 50.),
            (9.2, 60.),
            (10.9, 70.),
            (12.4, 80.),
            (13.9, 90.),
            (20.0, 100.)
        ]

    def process_fitness_result(self, fitness):
        return np.mean(fitness)

    def process_sport_file(self, sport_file):
        info = osp.splitext(osp.basename(sport_file))[0].split('_')
        run, walk = int(info[-1]), int(info[-2])
        df = pd.read_csv(sport_file, header=None).iloc[:, [3]]
        status_t = df.value_counts()
        # print(status_t.index)
        # if run == 0 and walk != 0:
        #     ave_heart = (status_t[(1,)] * walk) / status_t[(1,)]
        # elif run != 0 and walk == 0:
        #     ave_heart = (status_t[(2,)] * run) / status_t[(2,)]
        # elif run != 0 and walk != 0:
        #     ave_heart = (status_t[(1,)] * walk + status_t[(2,)] * run) / \
        #                 (status_t[(1,)] + status_t[(2,)])
        # else:
        #     ave_heart = 0.
        if run == 0 and walk != 0:
            ave_heart = walk
        elif run != 0 and walk == 0:
            ave_heart = run
        elif run != 0 and walk != 0:
            ave_heart = (status_t[(1,)] * walk + status_t[(2,)] * run) / \
                        (status_t[(1,)] + status_t[(2,)])
        else:
            ave_heart = 0.
        if (1,) not in status_t:
            walk_t = 0
        else:
            walk_t = status_t[(1,)] / 3600.
        if (2,) not in status_t:
            run_t = 0
        else:
            run_t = status_t[(2,)] / 3600.
        calories = self.body_weight * walk_t * 3 + self.body_weight * run_t * 6
        calories = calories / (walk_t + run_t) / 60.
        index = -1
        for i in range(len(self.calories_o2)-1):
            if self.calories_o2[i+1][0] > calories >= self.calories_o2[i][0]:
                index = i
                break
        if index != -1:
            o2 = (calories - self.calories_o2[index][0]) / \
                 (self.calories_o2[index+1][0] - self.calories_o2[index][0]) * \
                 (self.calories_o2[index+1][1] - self.calories_o2[index][1]) + \
                 self.calories_o2[index][1]
        else:
            if calories < self.calories_o2[0][0]:
                o2 = calories / self.calories_o2[0][0] * self.calories_o2[0][1]
            else:
                o2 = self.calories_o2[-1][1]
        return ave_heart, o2

    def test(self, curr_heart_rate, sport_file=None):
        if sport_file is not None:
            ave_heart, o2 = self.process_sport_file(sport_file)
        else:
            ave_heart = curr_heart_rate
            o2 = -1
        fitness = (ave_heart - self.min_heart_rate) / self.heart_rate_diff
        print('for fitness test: {}'.format(fitness))
        # # 100 - fitness，表示人体剩余能量状态
        # fitness = 1. - np.clip(fitness, 0., 1.)

        fitness_status = {
            # 体态综合识别结果：98%(强度：>45%，较强)
            'ours': float(self.process_fitness_result(fitness)) * 100.,
            # 'sport': 99.0   # 基于运行状态识别结果：93%(强度：<=45%，较弱)
        }
        if o2 != -1:
            fitness_status['sport'] = o2
        return fitness_status
