# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: utils.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/1/16
# @Description: 
# @Input:
# @Output:
#

import typing
import os
import datetime
import random


def get_file_abspath_list_from_dir(root_dir: str,
                                   recursive: bool = False,
                                   filter_file_type: str = 'Closed') -> typing.List[str]:
    """
    从某个目录下读取某类型文件的绝对路径列表，可以选择是否启用递归查找以及筛选器
    Args:
        root_dir (str): 要读取的目录地址，绝对相对均可
        recursive (bool): 是否进行递归读取，默认关闭
        filter_file_type (str): 是否启用过滤器，默认关闭

    Returns:
        List[str]，文件名列表
    """
    # 根据是否开启递归，获取到不同的文件绝对路径列表
    if recursive == 0:
        absolute_dir = os.path.abspath(root_dir)
        filename_list = os.listdir(root_dir)
        file_path_list = [os.path.join(absolute_dir, i) for i in filename_list]
        # 非递归模式，只需要读取其中的file，丢掉dir
        file_path_list = [i for i in file_path_list if os.path.isfile(i)]

    else:
        file_path_list = []
        for root, dirs, files in os.walk(root_dir):
            for filename in files:
                apath = os.path.join(root, filename)  # 合并成一个完整路径
                file_path_list.append(apath)

    # 文件类型筛选
    if filter_file_type == 'Closed':
        pass
    else:
        if not filter_file_type.startswith('.'):
            file_path_list = [i for i in file_path_list if os.path.splitext(i)[1] == ('.' + filter_file_type)]
        else:
            print('无法识别当前文件类型')

    return file_path_list


def remove_dir(dir_path: str) -> typing.NoReturn:
    """删除临时文件夹
    """
    # 先将该文件夹内所有文件移除，再将文件夹移除
    file_list = get_file_abspath_list_from_dir(dir_path, False)
    for file in file_list:
        os.remove(file)
    os.rmdir(dir_path)


def cut(function_str: str) -> str:
    """
    用来对生成的function按其括号进行截取，尽量保证其语法正确性.
    Args:
        function_str (str):

    Returns:

    """
    temp_str = ''

    for c in function_str:
        temp_str += c

        left_count = temp_str.count('{')
        right_count = temp_str.count('}')
        if (left_count == right_count) and (left_count != 0):
            return temp_str

    return function_str


def select_a_file_randomly(pool_path : str) -> str:
    """
    从一个目录下，随机返回其中一个文件的地址
    Args:
        pool_path (str): 目录

    Returns:
        目录下任意一个文件地址
    """
    file_list = os.listdir(pool_path)
    a_random_file = file_list[random.randint(0, len(file_list) - 1)]
    return os.path.join(pool_path, a_random_file)


def seconds_to_date(seconds: int):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d时%02d分%02d秒" % (h, m, s)


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


def write_file(file_path, content: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_id(file_name: str):
    """
    从给定文件名中，获取到该文件的标识符（16位）
    Args:
        file_name (str): 种子文件的文件名，有两种形式：
                        (1)原始的种子文件: 命名形式为 "original_uuid(前16位).js"
                        (2)生成的种子文件: 命名形式为 "generated_uuid(前16位)_uuid(前16位).js"，第一个uuid是该种子的标识符，第二个是其父亲的标识符

    Returns:
        该文件本身的标识符（即第一个uuid）
    """
    return os.path.basename(file_name).split('.')[0].split('_')[1]


def get_parent_id(file_name: str):
    """
    从给定文件名中，获取到该文件的父文件的标识符（16位）
    Args:
        file_name (str): 种子文件的文件名，有两种形式：
                        (1)原始的种子文件: 命名形式为 "original_uuid(前16位).js"
                        (2)生成的种子文件: 命名形式为 "generated_uuid(前16位)_uuid(前16位).js"，第一个uuid是该种子的标识符，第二个是其父亲的标识符

    Returns:
        该文件本身的标识符（即第二个uuid）
    """
    if file_name.startswith('original'):
        return '0000000000000000'
    return os.path.basename(file_name).split('.')[0].split('_')[2]


def round_up(value):
    return round(value * 100) / 100.0


if __name__ == '__main__':
    # code = """logging.info(132); wajgoawng{}wagmlawg"""
    # print(cut(code))
    # code = """
    # var NISLFuzzingFunc = function() {
    # var a = this.getValue();
    # var b = this.getValue();
    # if (b == a) {
    #     this._callbacks = [ this._created, this._defaultSwmerMay, removeStates, the[_]; }, __webpack_require__:
    #     function() { return this.__skill__.apply(this, arguments); }; }; }
    # """
    # print(cut(code))

    file1 = 'generated_1587190571967_69726.js'
    file2 = 'original_thgawkth206u2.js'
    print(get_id(file1))
    print(get_parent_id(file1))
    print(get_id(file2))
    print(get_parent_id(file2))

