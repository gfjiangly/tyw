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

from tyw.deploy import ResultBean
from tyw.deploy.constant import *
from tyw.deploy.setting import *
from tyw.deploy import dao
from tyw.deploy.ModelTrial import *

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
    config = flask.request.form['config']

    if f:
        # 保存文件
        f.save(file_dir + '/' + md5 + '.pkl')

        # 持久化文件属性
        fid = dao.setFileAttr(filename, md5)

        file_path = file_dir + '/' + md5 + '.pkl'
        item = do_trial(fid, config, file_path)

        return flask.jsonify(item)
    else:
        # 把 files:md5 中的记录删除
        dao.deleteMd5(md5)
        item = ResultBean.create_fail_bean("文件上传失败")
        return flask.jsonify(item)


# 算法测试接口
@app.route('/do_trial', methods=['POST'])
def do_trial_file():
    file_dir = osp.join(log_save_root, app.config['UPLOAD_FOLDER'])
    if not osp.exists(file_dir):
        return flask.jsonify(ResultBean.create_fail_bean("文件夹不存在"))

    fid = flask.request.form['fid']
    md5 = flask.request.form['md5']
    config = flask.request.form['config']

    file_path = ""

    if md5 is not None and md5 != '':
        file_path = md5
    elif fid is not None and fid != '':
        file_path = dao.getMd5ById(fid)

    if file_path == "":
        return flask.jsonify(ResultBean.create_fail_bean("文件不存在"))

    file_path = file_dir + '/' + file_path + '.pkl'

    item = do_trial(fid, config, file_path)

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


def do_trial(fid, config, file_path):

    f = open(file_path, mode='rb')

    df = pickle.load(f)

    # 算法调用处
    res = model_trial(df, config)
    ###################

    f.close()

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
