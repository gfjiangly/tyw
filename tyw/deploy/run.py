# -*- encoding:utf-8 -*-
# @Time    : 2020/9/28 16:40
# @Author  : jiang.g.f
import flask
import cvtools
import os
import os.path as osp


app = flask.Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pkl', 'csv'}

model = None

log_save_root = "../../log/"
logger = cvtools.get_logger('INFO', name='deploy_tyw_model')
logger = cvtools.logger_file_handler(logger,
                                     log_save_root+'/deploy_tyw_model.log',
                                     mode='a')


@app.route('/')
def upload_test():
    return flask.render_template('upload.html')


# 上传数据处理接口
@app.route('/up_data', methods=['POST'], strict_slashes=False)
def upload_image():
    file_dir = osp.join(log_save_root, app.config['UPLOAD_FOLDER'])
    if not osp.exists(file_dir):
        os.makedirs(file_dir)
    f = flask.request.files['data']
    if f:
        data = f.read()
        # response = flask.make_response(data)
        # response.headers['Content-Type'] = 'image/png'
        return None
    else:
        return flask.jsonify({"error": 1001, "msg": "上传失败"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
