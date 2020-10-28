# -*- encoding:utf-8 -*-
# @Time    : 2019/8/31 12:50
# @Author  : gfjiang
# @Site    : 
# @File    : draw.py
# @Software: PyCharm
import numpy as np
import pandas as pd
import cvtools
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker


def draw_class_distribution(y,
                            save_path='cls_dist.png'):
    """绘制饼图,其中y是标签列表
    """
    from collections import Counter
    from matplotlib import pyplot as plt
    target_stats = Counter(y)
    labels = list(target_stats.keys())
    sizes = list(target_stats.values())
    explode = tuple([0.1] * len(target_stats))
    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels,
           shadow=True, autopct='%1.1f%%')
    ax.axis('equal')
    plt.savefig(save_path)


def draw_dataframe(data,
                   col,
                   im_size=(20 * 4, 5),
                   show_value=None,
                   dst='draw.png'):
    """根据列名选择DataFrame的列，绘制图像
    """
    if not isinstance(data, (pd.DataFrame,)):
        print('!not supported data type: {}'.format(type(data)))
    ax = data.loc[:, col].plot(sharey=False, figsize=im_size, grid=True)
    fig = ax.get_figure()
    if np.max(data.index.values) - np.min(data.index.values) < 200:
        tick_spacing = 5
        ax.xaxis.set_major_locator(
            ticker.MultipleLocator(tick_spacing))
    elif np.max(data.index.values) - np.min(data.index.values) < 1000:
        tick_spacing = 10
        ax.xaxis.set_major_locator(
            ticker.MultipleLocator(tick_spacing))
    else:
        tick_spacing = 100
        ax.xaxis.set_major_locator(
            ticker.MultipleLocator(tick_spacing))
    if show_value is not None:
        x = np.min(data.index.values)
        y = data.loc[:, col].max().values[0]
        value = str(show_value)
        ax.text(x, y, value)
    # save draw
    cvtools.makedirs(dst)
    fig.savefig(dst)
    plt.close()


def draw_dataframe_list(data_list,
                        color_list,
                        col,
                        im_size=None,
                        tick_spacing=None,
                        dst='draw.png'):
    """根据列名选择DataFrame的列，绘制图像
    """
    colors = ['green', 'red', 'skyblue', 'blue']
    if im_size is not None:
        plt.figure(figsize=im_size)
        ax = plt.subplot(111)
        if tick_spacing is not None:
            ax.xaxis.set_major_locator(
                ticker.MultipleLocator(tick_spacing))
        plt.grid()  # 设置为网格
    for index, data in enumerate(data_list):
        x = data.index.values
        y = data.loc[:, col].values
        plt.plot(x, y, color=colors[color_list[index]])
    # save draw
    cvtools.makedirs(dst)
    plt.savefig(dst)
    plt.close()


def draw_waveforms(data, label, dst, figsize=(20 * 4, 5), colour=None):
    if colour is None:
        colour = ('cornflowerblue', 'red', 'blue', 'green', 'orange', 'black')
    fig = plt.figure(figsize=figsize)
    # 画图区域分成1行1列。选择第一块区域。
    ax1 = fig.add_subplot(1, 1, 1)
    for i, item in enumerate(label):
        if item[0] == 'scatter':
            ax1.scatter(data.index, data[item[1]], color=colour[i])
        if item[0] == 'plot':
            ax1.plot(data.index, data[item[1]], color=colour[i])
    cvtools.makedirs(dst)
    plt.savefig(dst)
    plt.close()


if __name__ == '__main_':
    data = None
    label = (('plot', 'ECG'), ('scatter', 'Q'), ('scatter', 'R'),
             ('scatter', 'S'), ('plot', 'PPG'), ('scatter', 'PPG_H'))
    draw_waveforms(draw, label, 'pic/temp/test.png')
