# -*- encoding:utf-8 -*-
# @Time    : 2020/10/30 18:00
# @Author  : jiang.g.f
from sklearn import svm
import numpy as np
from sklearn.model_selection import train_test_split

from tyw.configs.config import merge_cfg_from_file, cfg


def tired_label(s):
    it = {b'low': 0, b'middle': 1, b'high': 2}
    return it[s]


class TiredModel(object):
    """
    疲劳模型
    """
    def __init__(self, person_info=None):
        self.person_info = person_info
        self.sample_path = '../model_file/tired.txt'
        self.data = np.loadtxt(self.sample_path, dtype=float, delimiter=' ',
                               converters={3: tired_label})
        # x为数据，y为标签
        x, y = np.split(self.data, indices_or_sections=(3,), axis=1)
        x = x[:, 0:3]
        train_data, test_data, train_label, test_label = train_test_split(
            x, y, random_state=1, train_size=0.8, test_size=0.2)
        # ovr:一对多策略
        self.classifier = svm.SVC(
            C=1, kernel='linear', gamma=10, decision_function_shape='ovo')
        self.classifier.fit(train_data, train_label.ravel())
        # 计算svc分类器的准确率
        # print("训练集：", classifier.score(train_data, train_label))
        # print("测试集：", classifier.score(test_data, test_label))

    def test(self, tired_info):
        # # 不疲劳
        # print(classifier.predict([[36, 75, 99]]))
        # # 疲劳
        # print(classifier.predict([[37.4, 156, 90]]))
        tired_info = list(map(float, tired_info))
        res = int(self.classifier.predict([tired_info]))
        return 1 if res > 0 else 0


if __name__ == '__main__':
    model = TiredModel()
    # 不疲劳
    print(model.test([36, 75, 99]))
    # 疲劳
    print(model.test([37.4, 156, 90]))
