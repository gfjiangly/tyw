# -*- encoding:utf-8 -*-
# @Time    : 2020/9/28 16:40
# @Author  : jiang.g.f
import flask
import cvtools
import os
import os.path as osp
from tyw.deploy import dao
import time

app = flask.Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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


# 上传数据处理接口
@app.route('/up_data', methods=['POST'], strict_slashes=False)
def upload_image():
    file_dir = osp.join(log_save_root, app.config['UPLOAD_FOLDER'])
    if not osp.exists(file_dir):
        os.makedirs(file_dir)
    f = flask.request.files['data']
    filename = flask.request.form['filename'][:-4]
    # trial_time = flask.request.form
    if f:
        data = f.read()

        # 获取文件的一些属性，存储到redis
        file_attr = filename.split("_")
        result_attr = {'name': file_attr[0], 'exper_time': file_attr[1], 'trial_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}

        # 将此处的result换为调用算法后的结果
        result = {"aa": 1, "bb": 2, "cc": 3}

        # 持久化数据
        dao.setResult(filename, result_attr, result)
        # results = model(data)
        # response = flask.make_response(data)
        # response.headers['Content-Type'] = 'image/png'
        return flask.jsonify(result)
    else:
        return flask.jsonify({"error": 1001, "msg": "上传失败"})


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


@app.route("/test")
def test():
    # str = 'hpc_2019-01-21-19-58_0_1_x'
    # enc = dao.encoding(str)
    # dec = dao.decoding(enc)
    # print(enc)
    # print(dec)
    # idx = dao.findPrefixRange('hpc')
    # print(idx)
    items = dao.getSearchResult("hp")
    print(items)
    return flask.jsonify("res")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)