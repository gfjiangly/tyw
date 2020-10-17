import numpy as np

from tyw.loader.HungryLoader import HungryLoader
from tyw.model.HungryModel import HungryModel
from tyw.loader.FearLoader import FearLoader
from tyw.model.FearModel import FearModel
from tyw.configs.config import merge_cfg_from_file, cfg
from tyw.deploy.ResultBean import *

hungry_model = HungryModel(mode='test')
hungry_model.test(np.zeros((1, 200, 1)))
fear_model = FearModel(cfg)


def model_trial(df):
    # 将此处的result换为调用算法后的结果
    # 调用饥饿模型
    hungry_code = 0  # 0-未开启测试
    hungry = -1
    if cfg.TEST.HUNGRY_MODEL.OPEN:
        hungry_loader = HungryLoader()
        ppg = hungry_loader.process_test_data(df['PPG'])
        if len(ppg) == 0:
            print('饥饿采集数据太短，请增加采集时间！')
            hungry_code = -1
        else:
            hungry_code = 1
            hungry = hungry_model.test(ppg)
            hungry = process_hungry_result(hungry)
            if hungry:
                hungry = 1
            else:
                hungry = 0

    hungry_res = create_trial_bean(hungry_code, "ok", hungry)

    # 调用恐惧模型
    fear_code = 0
    fear = None
    if cfg.TEST.FEAR_MODEL.OPEN:
        fear_loader = FearLoader()
        eda_feats = fear_loader.process_test_data(df['EDA'])
        if len(eda_feats) == 0:
            print('恐惧采集数据太短，请增加采集时间！')
            fear_code = -1
        else:
            fear_code = 1
            fear = fear_model.test(eda_feats)
            fear = process_fear_result(fear)
            if fear:
                fear = 1
            else:
                fear = 0

    fear_res = create_trial_bean(fear_code, state=fear)

    # 调用恐惧模型
    tired_res = create_trial_bean(0, "未开启测试")

    # 综合结果
    com_res = create_trial_bean(0, "未开启测试")

    result = {"hungry": hungry_res, "fear": fear_res, "tired": tired_res, "comprehensive": com_res}
    return result


def process_hungry_result(hungry):
    """0: 不饿，1：饥饿"""
    return np.sum(hungry) > (len(hungry) // 2)


def process_fear_result(fear):
    return np.sum(fear) > 0
