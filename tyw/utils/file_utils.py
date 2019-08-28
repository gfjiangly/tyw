# -*- encoding:utf-8 -*-
# @Time    : 2019/5/13 11:01
# @Author  : gfjiang
# @Site    : 
# @File    : file_utils.py
# @Software: PyCharm
import os


# 递归文件夹下所有文件夹，得到文件路径列表
def get_file_list(root_dir):
    if not os.path.isdir(root_dir):
        return [root_dir]
    file_list = []
    for lists in os.listdir(root_dir):  # 相当于调用多个递归
        file_list += get_file_list(os.path.join(root_dir, lists))
    return file_list


# 在字符串列表中查找字符串，查到返回True, 否则返回False
def find_in_list(check_file, file_list, strict=True):
    if check_file is None or len(file_list) == 0:
        return None
    for file in file_list:
        if strict:
            if check_file == file:
                return True
        else:
            if file.find(check_file) != -1:
                return True
    return False
