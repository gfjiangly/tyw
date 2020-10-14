success_code = 1
success_msg = "success"
fail_code = -1


def create_res_bean(code, msg, data):
    return {'code': code, 'msg': msg, 'data': data}


def create_status_bean(code, msg):
    return create_res_bean(code, msg, "")


def create_success_bean(msg):
    return create_status_bean(success_code, msg)


def create_success_bean2(data):
    return create_res_bean(success_code, success_msg, data)


def create_fail_bean(msg):
    return create_status_bean(fail_code, msg)
