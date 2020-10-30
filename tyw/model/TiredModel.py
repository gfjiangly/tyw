# -*- encoding:utf-8 -*-
# @Time    : 2020/10/30 18:00
# @Author  : jiang.g.f
from tyw.configs.config import merge_cfg_from_file, cfg


class TiredModel(object):
    """
    疲劳模型
    """
    def __init__(self, person_info=None):
        self.person_info = person_info

    def test(self, tired_info):
        curr_state = 0
        return curr_state
