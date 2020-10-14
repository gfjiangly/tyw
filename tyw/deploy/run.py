# -*- encoding:utf-8 -*-
# @Time    : 2020/9/28 16:40
# @Author  : jiang.g.f
import flask
from flask import session
import cvtools
import os
import os.path as osp
import time
import pickle
import numpy as np

from tyw.deploy import ResultBean
from tyw.deploy.setting import *

from tyw.deploy import dao
from tyw.loader.HungryLoader import HungryLoader
from tyw.model.HungryModel import HungryModel
from tyw.loader.FearLoader import FearLoader
from tyw.model.FearModel import FearModel
from tyw.configs.config import merge_cfg_from_file, cfg


app = flask.Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SESSION_SECRET_KEY
ALLOWED_EXTENSIONS = {'txt', 'pkl', 'csv'}

model = None

log_save_root = "../../log/"
logger = cvtools.get_logger('INFO', name='deploy_tyw_model')
logger = cvtools.logger_file_handler(logger,
                                     log_save_root + '/deploy_tyw_model.log',
                                     mode='a')

cfg_file = '../configs/8-28.yaml'
merge_cfg_from_file(cfg_file)
hungry_model = HungryModel(mode='test')
hungry_model.test(np.zeros((1, 200, 1)))
fear_model = FearModel(cfg)


# 根接口
@app.route('/')
def upload_test():
    return flask.redirect("/overview")


# 上传 md5 和文件名
@app.route('/up_md5', methods=['GET'])
def upload_file_attr():
    md5 = flask.request.args['md5']
    item = dao.isMd5Existed(md5)
    session['md5'] = md5
    return flask.jsonify(item)


# 上传数据处理接口
@app.route('/up_data', methods=['POST'], strict_slashes=False)
def upload_image():
    file_dir = osp.join(log_save_root, app.config['UPLOAD_FOLDER'])
    if not osp.exists(file_dir):
        os.makedirs(file_dir)

    filename = flask.request.form['filename']
    md5 = flask.request.form['md5']
    f = flask.request.files['data']

    if f:
        # 保存文件
        f.save(file_dir + '/' + md5)

        # 持久化文件属性
        dao.setFileAttr(filename, md5)

        # 要在这里调用算法吗
        #
        ################

        df = pickle.loads(f.read())

        # 将此处的result换为调用算法后的结果
        # 调用饥饿模型
        hungry = 0  # 0-未开启测试
        if cfg.TEST.HUNGRY_MODEL.OPEN:
            hungry_loader = HungryLoader()
            ppg = hungry_loader.process_test_data(df['PPG'])
            if len(ppg) == 0:
                print('饥饿采集数据太短，请增加采集时间！')
                hungry = -1
            else:
                hungry = hungry_model.test(ppg)
        # 调用恐惧模型
        fear = 0
        if cfg.TEST.FEAR_MODEL.OPEN:
            fear_loader = FearLoader()
            eda_feats = fear_loader.process_test_data(df['EDA'])
            fear = fear_model.test(eda_feats)
        result = {"hungry": hungry, "fear": fear, "cc": 3}

        # 持久化数据

        item = ResultBean.create_success_bean("文件上传成功")
        return flask.jsonify(item)
    else:
        # 把 files:md5 中的记录删除
        dao.deleteMd5(md5)
        item = ResultBean.create_fail_bean("文件上传失败")
        return flask.jsonify(item)


# 总览模块入口
@app.route('/overview', methods=['GET'])
def overview_entry():
    return flask.render_template("overview.html")


# 测试模块入口
@app.route('/trial', methods=['GET'])
def trial_entry():
    return flask.render_template("trial.html")


# 历史模块入口
@app.route('/history', methods=['GET'])
def history_entry():
    return flask.render_template("history.html")


# 请求历史结果
@app.route('/history/result/all', methods=['GET'])
def history_all_result():
    return flask.jsonify(dao.getAllResult())


# 请求搜索数据
@app.route('/history/result/search', methods=['GET'])
def history_search_result():
    prefix = flask.request.args['prefix']
    items = dao.getSearchResult(prefix)
    # print(items)
    return flask.jsonify(items)


# 重新测试接口
@app.route('/retrial', methods=['POST'])
def retrial_file():
    items = []
    return flask.jsonify(items)


# 删除接口
@app.route('/delete/all', methods=['POST'])
def delete_record_all():
    fid = flask.request.form['fid']
    return flask.jsonify(dao.deleteRecordAll(fid))


@app.route("/test")
def test():
    # str = 'hpc_2019-01-21-19-58_0_1_x'
    # enc = dao.encoding(str)
    # dec = dao.decoding(enc)
    # print(enc)
    # print(dec)
    # idx = dao.findPrefixRange('hpc')
    # print(idx)
    # items = dao.getSearchResult("hp")
    # print(items)
    # res = dao.getAllResult()
    dao.deleteRecordAll(1)
    return flask.jsonify('res')


@app.errorhandler(400)
def handle_400_error(err_msg):
    md5 = session.get('md5')
    print('file uploaded aborted. file md5 is ' + md5)
    if md5 is not None:
        dao.deleteMd5(md5)


def do_trial(file, filename):
    if file:
        data = file.read()

        # 获取文件的一些属性，存储到redis
        file_attr = filename.split("_")
        result_attr = {'name': file_attr[0], 'exper_time': file_attr[1], 'trial_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}

        # 将此处的result换为调用算法后的结果
        result = {"aa": 1, "bb": 2, "cc": 3}

        # 持久化数据
        dao.setResult(filename, result_attr, result)

    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
