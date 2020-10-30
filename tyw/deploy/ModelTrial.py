import numpy as np

from tyw.loader.HungryLoader import HungryLoader
from tyw.model.HungryModel import HungryModel
from tyw.loader.FearLoader import FearLoader
from tyw.model.FearModel import FearModel
from tyw.model.HealthModel import HealthModel
from tyw.loader.FitnessLoader import FitnessLoader
from tyw.model.FitnessModel import FitnessModel
from tyw.configs.config import merge_cfg_from_file, cfg
from tyw.deploy.ResultBean import *

hungry_model = HungryModel(mode='test')
hungry_model.test(np.zeros((1, 200, 1)))
fear_model = FearModel(cfg)
health_model = HealthModel()


def model_trial(df, person_info):
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
            hungry = int(process_hungry_result(hungry))
    hungry_res = create_trial_bean(hungry_code, state=hungry)

    # 调用恐惧模型
    fear_code = 0
    fear = -1
    if cfg.TEST.FEAR_MODEL.OPEN:
        fear_loader = FearLoader()
        eda_feats = fear_loader.process_test_data(df['EDA'])
        if len(eda_feats) == 0:
            print('恐惧采集数据太短，请增加采集时间！')
            fear_code = -1
        else:
            fear_code = 1
            fear = fear_model.test(eda_feats)
            fear = int(process_fear_result(fear))
    fear_res = create_trial_bean(fear_code, state=fear)

    # 调用疲劳模型
    tired_res = create_trial_bean(0, "未开启测试")

    # # 健康结果
    # health_code = 0
    # health = -1
    # if cfg.TEST.HEALTH_MODEL.OPEN:
    #     health = health_model.test(None)
    # health_res = create_trial_bean(health_code, state=health)

    # 调用综合体能模型
    fitness_model = FitnessModel(person_info)
    fitness_code = 0
    fitness = -1
    if cfg.TEST.FITNESS_MODEL.OPEN:
        fitness_loader = FitnessLoader()
        ppg_feats = fitness_loader.process_test_data(df['ECG'])
        if len(ppg_feats) == 0:
            print('心率数据采集太短，请增加采集时间！')
            fitness_code = -1
        else:
            fitness_code = 1
            fitness = fitness_model.test(ppg_feats)
            fitness = int(process_fitness_result(fitness))
    fitness_res = create_trial_bean(fitness_code, state=fitness)

    result = {
        "hungry": hungry_res,
        "fear": fear_res,
        "tired": tired_res,
        "health": health_res,
        "comprehensive": fitness_res
    }
    return result


def health_trial(temperature, curr_heart_rate, blood_oxygen):
    health_info = {
        'temperature': float(temperature),
        'curr_heart_rate': float(curr_heart_rate),
        'blood_oxygen': float(blood_oxygen)
    }
    health = health_model.test(health_info)
    health_res = create_trial_bean(0, state=health)
    result = {
        "health": health_res,
    }
    return result


def process_hungry_result(hungry):
    """0: 不饿，1：饥饿"""
    return np.sum(hungry) > (len(hungry) // 2)


def process_fear_result(fear):
    return np.sum(fear) > 0


def process_fitness_result(fitness):
    return np.mean(fitness)
