# -*- encoding:utf-8 -*-
# @Time    : 2019/11/13 22:19
# @Author  : gfjiang
# @Site    : 
# @File    : main.py
# @Software: PyCharm

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
import _pickle as pickle

import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
from mpl_toolkits.axisartist.axislines import SubplotZero
import matplotlib.pyplot as plt

from tyw.gui.ui.main_page import Ui_MainWindow as Main
from tyw.gui.ui.train_page import Ui_MainWindow as Train
from tyw.gui.ui.test_page import Ui_MainWindow as Test


# 创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        # 第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_tight_layout(True)
        self.fig.set_facecolor('None')
        # 第二步：在父类中激活Figure窗口
        super(MyFigure, self).__init__(self.fig)     # 此句必不可少，否则不能显示图形
        # 第三步：创建一个子图，用于绘制图形用，111表示子图编号
        # self.axes = self.fig.add_subplot(111)
        self.ax = SubplotZero(self.fig, 1, 1, 1)
        self.axes = self.fig.add_subplot(self.ax)
        # self.ecg_axes = self.fig.add_subplot(411)
        # self.ppg_axes = self.fig.add_subplot(412)
        # self.eda_axes = self.fig.add_subplot(413)
        # self.skt_axes = self.fig.add_subplot(414)
        fig, ax = plt.subplots()
        fig.add_axes()
        ax1 = fig.add_subplot(111)
        ax1.set_grid()
        plt.show()

    def plot(self, data):
        # 第四步：就是画图，【可以在此类中画，也可以在其它类中画】
        self.axes.plot(data)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        # 去掉边框
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'].set_visible(False)
        return self.axes

    def plot_ecg(self, ecg):
        self.ecg_axes.plot(ecg)
        # self.ecg_axes.set_xticks([])
        # self.ecg_axes.set_yticks([])
        # y 轴不可见
        self.ecg_axes.get_yaxis().set_visible(False)
        # x 轴不可见
        self.ecg_axes.get_xaxis().set_visible(False)
        # # 去掉边框
        # # self.ecg_axes.spines['top'].set_visible(False)
        # self.ecg_axes.spines['right'].set_visible(False)
        # # self.ecg_axes.spines['bottom'].set_visible(False)
        # self.ecg_axes.spines['left'].set_visible(False)

    def plot_ppg(self, ppg):
        self.ppg_axes.plot(ppg)
        self.ppg_axes.set_xticks([])
        self.ppg_axes.set_yticks([])

    def plot_eda(self, eda):
        self.eda_axes.plot(eda)
        self.eda_axes.set_xticks([])
        self.eda_axes.set_yticks([])

    def plot_skt(self, skt):
        self.skt_axes.plot(skt)
        self.skt_axes.set_xticks([])
        self.skt_axes.set_yticks([])


class TestFrame(QMainWindow, Test):

    def __init__(self):
        super(TestFrame, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("体态识别")
        self.setMinimumSize(0, 0)

        file = 'jgf_5-8_0_2_1.pkl'
        data = pickle.load(open(file, 'rb'), encoding='utf-8')

        # 第五步：定义MyFigure类的一个实例
        self.ecg_fig = MyFigure(width=20, height=10, dpi=100)
        self.ppg_fig = MyFigure(width=20, height=10, dpi=100)
        self.eda_fig = MyFigure(width=20, height=10, dpi=100)
        self.skt_fig = MyFigure(width=20, height=10, dpi=100)

        # 第六步：在GUI的groupBox中创建一个布局，用于添加MyFigure类的实例
        self.gridlayout = QGridLayout(self.ecg_groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.ecg_fig)
        self.ecg_fig.plot(data['ECG'].values[:10000])
        # self.ecg_fig.autoFillBackground()

        self.gridlayout = QGridLayout(self.ppg_groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.ppg_fig)
        self.ppg_fig.plot(data['PPG'].values[:10000])

        self.gridlayout = QGridLayout(self.eda_groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.eda_fig)
        self.eda_fig.plot(data['EDA'].values[:10000])

        self.gridlayout = QGridLayout(self.skt_groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.skt_fig)
        self.skt_axes = self.skt_fig.plot(data['SKT'].values[:1000])
        # 设置网格样式
        self.skt_axes.grid(True, linestyle='-.')
        # self.skt_axes.set_ylim(20, 40)
        # 于 offset 处新建一条纵坐标
        offset = (5, 0)
        new_axisline = self.skt_fig.ax.get_grid_helper().new_fixed_axis
        self.skt_fig.ax.axis["新建2"] = new_axisline(loc="right", offset=offset, axes=self.skt_fig.ax)


class MainFrame(QMainWindow, Main):

    def __init__(self, parent=None):
        super(MainFrame, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("体态识别软件")

        palette1 = QPalette()
        palette1.setColor(self.backgroundRole(), QColor(174, 238, 238))  # 设置背景颜色
        self.setPalette(palette1)

        mylayout = QVBoxLayout()
        self.setLayout(mylayout)


class TrainFrame(QMainWindow, Train):

    def __init__(self, parent=None):
        super(TrainFrame, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("模型训练")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # ui = MainFrame()
    # ui = TrainFrame()
    ui = TestFrame()
    ui.show()
    sys.exit(app.exec_())
