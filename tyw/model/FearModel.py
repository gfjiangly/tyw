# -*- encoding:utf-8 -*-
# @Time    : 2020/10/12 21:02
# @Author  : jiang.g.f
from tyw.configs.config import cfg


class FearModel:

    def __init__(self, configs):
        self.cfg = {
            'mean_low': -2.56,
            'mean_hight': 1.18,
            'categories': {
                'normal': 0,
                'fear': 1
            }
        }
        self._load_configs(configs)

    def _load_configs(self, file):
        pass

    def predict(self, feats):
        value = 0.
        prop = 0.
        if cfg.EDA.FEATS_MEAN:
            value += (feats['mean'] - cfg.EDA.MEAN) / cfg.EDA.MEAN_STD * cfg.EDA.MEAN_PROP
            prop += cfg.EDA.MEAN_PROP
        if cfg.EDA.FEATS_MAX_MIN:
            if cfg.EDA.ADAPT_TH:
                feats['max-min'] = feats['max-min'][len(feats['max-min']) // 2:]
            value += (feats['max-min'] - cfg.EDA.MAX_MIN) / cfg.EDA.MAX_MIN_STD * cfg.EDA.MAX_MIN_PROP
            prop += cfg.EDA.MAX_MIN_PROP

        value /= prop

        if cfg.EDA.ADAPT_TH and cfg.EDA.FEATS_MAX_MIN:
            value = value[(value < feats['unfear_TH']) | (value > feats['fear_TH'])]
            value[value < feats['unfear_TH']] = 0.
            value[value > feats['fear_TH']] = 1.
        else:
            value = value[(value < cfg.EDA.L_TH) | (value > cfg.EDA.H_TH)]
            value[value < cfg.EDA.L_TH] = 0.
            value[value > cfg.EDA.H_TH] = 1.
        return value

    def test(self, example):
        return self.predict(example)


if __name__ == '__main__':
    pass
