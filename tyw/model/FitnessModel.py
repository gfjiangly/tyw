# -*- encoding:utf-8 -*-
# @Time    : 2020/10/28 13:51
# @Author  : jiang.g.f
import numpy as np
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
        self.heart_rate_diff = self.max_heart_rate - self.min_heart_rate

    def test(self, curr_heart_rate, sport_file=None):
        fitness = (curr_heart_rate - self.min_heart_rate) / self.heart_rate_diff
        print('for fitness test: {}'.format(fitness))
        # # 100 - fitness，表示人体剩余能量状态
        # fitness = 1. - np.clip(fitness, 0., 1.)
        fitness_status = {
            'ours': fitness * 100.,  # 体态综合识别结果：98%(强度：>45%，较强)
            'sport': 99.0   # 基于运行状态识别结果：93%(强度：<=45%，较弱)
        }
        return fitness_status


if __name__ == '__main__':
    pass
