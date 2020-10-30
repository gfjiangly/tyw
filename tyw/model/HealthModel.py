# -*- encoding:utf-8 -*-
# @Time    : 2020/10/30 10:44
# @Author  : jiang.g.f
from tyw.configs.config import merge_cfg_from_file, cfg


class HealthModel(object):
    """健康：
    心率：60~100，血氧饱和度: >94%，体温：35.8~37.0
    """
    def __init__(self, person_info=None):
        self.person_info = person_info

    def test(self, health_info):
        curr_state = 0
        temperature = health_info['temperature']
        curr_heart_rate = health_info['curr_heart_rate']
        blood_oxygen = health_info['blood_oxygen']
        if blood_oxygen < 94 or curr_heart_rate < 60 or curr_heart_rate > 100 \
                or temperature < 35.8 or temperature > 37.0:
            curr_state = 1
        return curr_state


if __name__ == '__main__':
    pass
