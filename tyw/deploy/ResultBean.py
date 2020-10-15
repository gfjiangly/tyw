success_code = 1
success_msg = "success"
fail_code = -1


# 以下产生的 bean 是用于存放算法测试结果的
# @param code 代码
# @param msg 消息
# @param state 状态，即 饿/不饿，恐惧/不恐惧
# @param data 数据，即用于绘制图像的数组数据
def create_trial_bean(code, msg,  data=None, state=-1):
    if data is None:
        data = []
    return {'code': code, 'msg': msg, 'state': state, 'data': data}


# 以下产生的 bean 是用于反馈给前端的
def create_bean(code, msg, data):
    return {'code': code, 'msg': msg, 'data': data}


def create_status_bean(code, msg):
    return create_bean(code, msg, "")


def create_success_bean(msg):
    return create_status_bean(success_code, msg)


def create_success_data_bean(data):
    return create_bean(success_code, success_msg, data)


def create_fail_bean(msg):
    return create_status_bean(fail_code, msg)
