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

    def test(self, curr_state):
        return curr_state


if __name__ == '__main__':
    pass
