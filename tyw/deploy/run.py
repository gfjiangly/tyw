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
import yaml
import json
import sys

from tyw.configs.config import merge_cfg_from_file, cfg
from tyw.processor.DataProcessor import DataProcessor
from tyw.deploy import ResultBean
from tyw.deploy.constant import *
from tyw.deploy.setting import *
from tyw.deploy import dao
from tyw.deploy.ModelTrial import *
from tyw.utils.collections import AttrDict

sys.path.append('../../')

app = flask.Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SESSION_SECRET_KEY
ALLOWED_EXTENSIONS = {'txt', 'pkl', 'csv'}

cfg_file = '../configs/8-28.yaml'
merge_cfg_from_file(cfg_file)
model = None

init_config = AttrDict()

log_save_root = "../../log/"
logger = cvtools.get_logger('INFO', name='deploy_tyw_model')
logger = cvtools.logger_file_handler(logger,
                                     log_save_root + '/deploy_tyw_model.log',
                                     mode='a')


# 根接口
@app.route('/')
def upload_test():
    return flask.redirect("/overview")


# 上传配置信息
@app.route('/person/upload', methods=['POST'])
def upload_person_info():
    username = flask.request.form['username']
    age = flask.request.form['age']
    max_beats = int(flask.request.form['max_beats'])
    min_beats = int(flask.request.form['min_beats'])

    # 设置 Session
    setUser(username)

    # 计算最小心率
    if min_beats == -1:
        # 此处调用算法计算最小心率
        min_beats = 0
    ###########

    # 计算最大心率
    if max_beats == -1:
        max_beats = 220 - int(age)

    # 持久化
    dao.setPersonInfo(username, age, min_beats, max_beats)

    result = {"min": min_beats, "max": max_beats}

    return create_success_data_bean(result)


# 获取配置信息
@app.route('/person/info', methods=['GET'])
def get_person_info():
    username = getUser()
    if username is None:
        return flask.jsonify(create_fail_bean("未配置"))
    res = dao.getPersonInfo(username)
    return flask.jsonify(create_success_data_bean(res))


# 上传 md5 和文件名
@app.route('/up_md5', methods=['GET'])
def upload_file_attr():

    username = flask.request.args['username']

    # 判断当前用户是否已配置
    if getUser() is None or getUser() == '':
        return flask.jsonify(create_fail_bean("nouser"))

    # 获取用户信息
    info = dao.getPersonInfo(username)
    if info is None or info == {} or len(info) == 0:
        return flask.jsonify(create_fail_bean("nofound"))

    # 设置当前用户
    setUser(username)

    if session.get('md5') is not None:
        session.pop('md5')

    md5 = flask.request.args['md5']
    item = dao.isMd5Existed(md5)

    if item['code'] == 1:
        session['md5'] = md5

    return flask.jsonify(item)


def parse_file(f, filename):
    suffix = osp.splitext(filename)[-1]
    if suffix == '.csv' or suffix == '.txt':
        # data = str(f.read(), encoding='gbk')
        data = list(map(lambda a: str(a, encoding='gbk'), f.readlines()))
        data_processor = DataProcessor()
        data = data_processor.load_data_from_raw_data(data)
        # data_processor.save(filename)
        return data
    elif suffix == '.pkl':
        return pickle.loads(f.read())
    else:
        raise ValueError("请上传后缀为csv或pkl的信号文件！")


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
        data = parse_file(f, filename)
        # 持久化文件属性
        fid = dao.setFileAttr(filename, md5)

        if session.get('md5') is not None:
            session.pop('md5')

        # 保存文件
        cvtools.dump_pkl(data, osp.join(file_dir, md5 + '.pkl'))

        return flask.jsonify(ResultBean.create_success_bean("ok"))
    else:
        # 把 files:md5 中的记录删除
        dao.deleteMd5(md5)
        item = ResultBean.create_fail_bean("文件上传失败")
        return flask.jsonify(item)


# 上传体态文件
@app.route('/up_body', methods=['POST'], strict_slashes=False)
def upload_body_file():

    # 判断用户是否存在
    # 其实在MD5验证那里就已经判断了，这里可以不用再判断的
    username = getUser()
    if username is None or username == '':
        return flask.jsonify(create_fail_bean("请先配置测试者信息"))

    file_dir = osp.join(log_save_root, app.config['UPLOAD_FOLDER'])
    if not osp.exists(file_dir):
        os.makedirs(file_dir)

    filename = flask.request.form['filename']
    f = flask.request.files['data']

    if f:

        # 保存文件
        filename = username + '_' + filename
        f.save(file_dir + '/' + filename)

        # 持久化文件属性
        dao.setBodyFileAttr(username, filename)

        if session.get('md5') is not None:
            session.pop('md5')

        return flask.jsonify(ResultBean.create_success_bean("ok"))
    else:
        item = ResultBean.create_fail_bean("文件上传失败")
        return flask.jsonify(item)


# 算法测试接口，放在test文件夹下测试
@app.route('/do_trial', methods=['POST'])
def do_trial_file():
    file_dir = osp.join(log_save_root, app.config['UPLOAD_FOLDER'])
    if not osp.exists(file_dir):
        return flask.jsonify(ResultBean.create_fail_bean("文件夹不存在"))

    fid = flask.request.form['fid']
    md5 = flask.request.form['md5']
    config = flask.request.form['config']
    is_save = flask.request.form['save_config']

    filename = ""

    if md5 is not None and md5 != '':
        # 上传时通过md5定位文件
        filename = md5
    elif fid is not None and fid != '':
        # 重测时通过fid定位文件
        filename = dao.getMd5ById(fid)

    # 持久化结果需要用到 fid
    if fid is None or fid == '':
        fid = dao.getFidByMd5(md5)

    # fid 为 None 说明没能通过 md5 获取得到 fid。即存在 MD5 但是 不存在 fid
    # 出现这种情况的原因是：用户点击上传后又马上刷新页面或者关闭浏览器，这有可能造成上传了 MD5 但是还没上传文件
    # 所以这里做预防措施
    if fid is None:
        dao.deleteMd5(md5)
        return flask.jsonify(create_fail_bean("请重新上传文件"))

    tmp_config = cfg['TEST']
    save_config(config)

    if filename == "":
        return flask.jsonify(ResultBean.create_fail_bean("文件不存在"))

    file_path = file_dir + '/' + filename + '.pkl'
    item = do_trial(fid, file_path)

    # 如果此次测试不保存配置信息，则恢复
    if not is_save:
        cfg['TEST'] = tmp_config

    return flask.jsonify(item)


# 总览模块入口
@app.route('/overview', methods=['GET'])
def overview_entry():
    return flask.render_template("overview.html")


# 个人信息模块入口
@app.route('/person', methods=['GET'])
def person_entry():
    return flask.render_template("person.html")


# 测试模块入口
@app.route('/trial', methods=['GET'])
def trial_entry():
    arr = []
    for item in CONFIG_ITEM:
        arr.append(init_config[item]['OPEN'])

    config = json.dumps(dict(zip(TARGET_ITEM, arr)))
    return flask.render_template("trial.html", config=config)


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


# 查看图像入口地址
@app.route('/graph/<path:fid>', methods=['GET'])
def graph_entry(fid):
    return flask.render_template("graph.html", fid=fid)


# 获取图像数据结果
@app.route('/graph/data', methods=['GET'])
def get_graph_data():
    fid = flask.request.args['fid']
    res = dao.getGraphData(fid)
    if res['code'] == fail_code:
        return flask.jsonify(res)

    data = res['data']
    count = len(data)
    for i in range(2, count):
        data[i] = eval(data[i])

    res['data'] = data
    return flask.jsonify(res)


# 删除接口
@app.route('/delete/all', methods=['POST'])
def delete_record_all():
    fid = flask.request.form['fid']
    return flask.jsonify(dao.deleteRecordAll(fid))


@app.errorhandler(400)
def handle_400_error(err_msg):
    md5 = session.get('md5')
    print('file uploaded aborted. file md5 is ' + md5)
    if md5 is not None:
        dao.deleteMd5(md5)
        session.pop('md5')


@app.errorhandler(500)
def handle_500_error(err_msg):
    md5 = session.get('md5')
    print('file uploaded aborted. file md5 is ' + md5)
    if md5 is not None:
        dao.deleteMd5(md5)
        session.pop('md5')


def do_trial(fid, file_path):
    f = open(file_path, mode='rb')

    df = pickle.load(f)

    # 算法调用处
    person_info = dao.getPersonInfo(getUser())
    res = model_trial(df, person_info)
    ###################

    # 持久化测试结果
    flag = dao.setResult(fid, res)

    # return_data = []
    # for target in TARGET_ITEM:
    #     return_data.append(res[target]['state'])
    #
    # return_data = dict(zip(TARGET_ITEM, return_data))
    # return_data['fid'] = fid

    item = ResultBean.create_success_data_bean(res)
    return item


# 保存 config
def save_config(config):
    dic = json.loads(config)
    for item in CONFIG_ITEM:
        cfg['TEST'][item]['OPEN'] = dic[item]


# 读 yaml
def read_yaml(cfg_filename):
    with open(cfg_filename, 'r', encoding='UTF-8') as f:
        return AttrDict(yaml.load(f, Loader=yaml.FullLoader))['TEST']


# 获取当前测试者
def getUser():
    return session.get(USERNAME_SESSION)


# 设置当前测试者
def setUser(username):
    session[USERNAME_SESSION] = username


if __name__ == '__main__':
    init_config = read_yaml(cfg_file)
    app.run(host='0.0.0.0', port=5000)
