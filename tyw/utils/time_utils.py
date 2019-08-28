# -*- encoding:utf-8 -*-
# @Time    : 2019/5/13 11:03
# @Author  : gfjiang
# @Site    : 
# @File    : time_utils.py
# @Software: PyCharm


def print_func_time(function):
    """ 计算程序运行时间
    """
    from functools import wraps

    @wraps(function)
    def func_time(*args, **kwargs):
        import time
        t0 = time.clock()
        result = function(*args, **kwargs)
        t1 = time.clock()
        print("Total running time: %s s" % (str(t1 - t0)))
        return result
    return func_time
