# -*- encoding:utf-8 -*-
# @Time    : 2018/8/3 16:58
# @Author  : gfjiang
# @Site    :
# @File    : main.py
# @Software: PyCharm Community Edition
import matplotlib
matplotlib.use('Agg')
import time
from keras.layers import LSTM
from keras.layers.core import Dense
from keras.models import Sequential

from tyw.configs.config import cfg


def lstm():
    layers = cfg.TRAIN.HUNGRY_MODEL.LAYERS
    seq_len = cfg.TRAIN.HUNGRY_MODEL.LOOK_BACK
    model = Sequential()
    # return_sequences = (默认是False)True
    # 则返回整个序列，否则仅返回输出序列的最后一个输出.
    model.add(LSTM(layers[1], input_shape=(seq_len, layers[0]), return_sequences=True))
    # model.add(LSTM(layers[2], return_sequences=True))
    # model.add(Dropout(0.2))
    model.add(LSTM(layers[2], return_sequences=False))
    # model.add(Dropout(0.2))
    model.add(Dense(units=layers[3], activation='softmax'))
    start = time.time()
    # rmsprop = optimizers.RMSprop(lr=0.0001)
    # model.compile(loss="mse", optimizer=rmsprop)
    # model.compile(loss="mse", optimizer="adagrad")
    model.compile(
        loss="categorical_crossentropy", optimizer="rmsprop", metrics=['accuracy', 'mse']
    )
    print("Compilation Time : ", time.time() - start)
    return model


class HungryModel(object):
    def __init__(self):
        self.model = self.build_model()
        self.seq_len = cfg.TRAIN.HUNGRY_MODEL.LOOK_BACK
        self.batch_size = cfg.TRAIN.HUNGRY_MODEL
        self.epochs = cfg.TRAIN.HUNGRY_MODEL

    def build_model(self):
        return eval(cfg.HUNGRY_MODEL.TYPE)()

    def train(self, trainX, trainY):
        print(time.strftime("> %Y-%m-%d %H:%M:%S", time.localtime()) + ": training...")
        # 模型训练
        self.model.fit(trainX, trainY, batch_size=self.batch_size,
                       epochs=self.epochs, validation_split=0.2, verbose=1, shuffle=True)
        print(time.strftime("> %Y-%m-%d %H:%M:%S", time.localtime()) + "train end")

    def test(self, testX):
        pass


if __name__ == '__main__':
    pass
