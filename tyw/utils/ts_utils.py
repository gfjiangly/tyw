# -*- encoding:utf-8 -*-
# @Time    : 2019/5/21 17:14
# @Author  : gfjiang
# @Site    : 
# @File    : ts_utils.py
# @Software: PyCharm
import numpy as np
import pandas as pd


def down_sample(data, interval=2):
    """对DataFrame或Series或np.array下采样
    """
    if isinstance(data, (pd.DataFrame,)):
        data = data.iloc[0:data.shape[0]:interval]
        data = data.reset_index(drop=True)
    elif isinstance(data, np.ndarray):
        data = data[0:data.shape[0]:interval]
    else:
        data = None
        print('!!!Warning: not supported data type')
    return data
