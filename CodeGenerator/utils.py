# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: utils.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/11/27
# @Description: 
# @Input:
# @Output:
#

import torch
import os
import random
import math
import logging
import json

import execjs

import sentencepiece as spm

from CodeGenerator.conf import hparams
from CodeGenerator.db_operation import DBOperation
from typing import *


device = torch.device(f"cuda:{hparams.gpu}" if torch.cuda.is_available() else "cpu")


def logger_config(
        prefix: str = 'NULL',
        file_level: str = 'INFO',
        console_level: str = 'INFO',
        log_file: str = 'test.log'):
    """设置日志，既向日志文件打印，又向控制台打印
    :param prefix: 设置日志的前缀，即[]中的内容
    :param file_level: 向日志文件中输出的日志等级
    :param console_level: 向控制台输出的日志等级
    :param log_file: 日志文件路径
    :return: 无返回值
    """
    # 获取一个Logger实例
    logger = logging.getLogger()
    logger.setLevel('NOTSET')    # 设置最低的日志级别，只有高于（包含）这个级别的日志才会被输出

    # 设置日志格式
    if prefix == 'NULL':
        BASIC_FORMAT = f'%(asctime)s - %(levelname)s: %(message)s'
    else:
        BASIC_FORMAT = f'[{prefix}]%(asctime)s - %(levelname)s: %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

    # 设置输出到控制台的handler
    chlr = logging.StreamHandler()
    chlr.setFormatter(formatter)
    chlr.setLevel(console_level)   # 设置控制台日志级别

    # 设置输出到文件的handler
    fhlr = logging.FileHandler(log_file, encoding='utf-8')    # 注意这里设置日志文件的编码
    fhlr.setFormatter(formatter)
    fhlr.setLevel(file_level)    # 设置日志文件日志级别

    # 添加两个handler到logger中
    logger.addHandler(chlr)
    logger.addHandler(fhlr)


def load_json(json_path, transfer=False):
    with open(json_path, 'r', encoding='utf-8') as f:
        _dict = json.load(f)

    # 数字作为主键，写入文件后会自动变化为字符串，此时需要将其再转化为数字
    if transfer:
        _dict = {int(key): value for key, value in _dict.items()}
    return _dict


def save_json(_dict, json_path):
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(_dict))


def get_files_from_dir(root_dir: str) -> List[str]:
    """
    递归获得指定dir下的全部文件路径
    Args:
        root_dir (str):

    Returns:

    """
    file_path_list = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            apath = os.path.join(root, filename)  # 合并成一个完整路径
            file_path_list.append(apath)

    return file_path_list


def list2db(_list: List[str], target_db_path: str, table_name='corpus', column_name='Content'):
    """
    将传入的list数据依次写入到数据库中
    Args:
        _list (list): list形式的数据
        target_db_path (str): 要生成的数据库地址
        table_name (str): 表名
        column_name (str): 列名

    Returns:
        None
    """
    results = [[line.strip()] for line in _list]
    target_db_op = DBOperation(target_db_path, table_name=table_name)
    target_db_op.init_db()
    target_db_op.insert([column_name], results)
    target_db_op.finalize()


def db2list(source_db_path: str, table_name='corpus', column_name='Content') -> List[str]:
    """
    用来读取原始数据库的内容并返回
    Args:
        source_db_path (str): 源数据库路径
        table_name (str): 表名
        column_name (str): 列名

    Returns:
        数据库内容
    """
    source_db_op = DBOperation(source_db_path, table_name=table_name)
    # 注意这里的i[0]才是str，i是tuple[str]
    contents = [i[0] for i in source_db_op.query_all([column_name])]
    source_db_op.finalize()
    return contents


def list_insert_db(_list: List[str], target_db_path: str, table_name='corpus', column_name='Content'):
    """
    将传入的list数据追加插入到数据库中
    Args:
        _list (list): list形式的数据
        target_db_path (str): 要生成的数据库地址
        table_name (str): 表名
        column_name (str): 列名

    Returns:
        None
    """
    results = [[line.strip()] for line in _list]
    target_db_op = DBOperation(target_db_path, table_name=table_name)

    # 若数据库存在，且不为空，则不用初始化，可以直接向其中插入数据
    if os.path.exists(target_db_op.db_path) and not target_db_op.is_empty():
        pass

    # 若数据库不存在，或者数据库存在但为空，则需要将其初始化
    else:
        conn = target_db_op.get_connection()
        cursor = conn.cursor()
        cursor.execute(target_db_op.ddl)

    # 插入数据
    target_db_op.insert([column_name], results)
    target_db_op.finalize()


def get_batch_iter(preprocess, batch_size):
    """
    根据处理训练数据的preprocess，产生一个生成器，能够按固定的batch_size返回映射和padding后的训练数据
    因为此处仅训练用，所以不需要处理<unk>
    Args:
        preprocess (Preprocessor类的实例):
        batch_size (int):

    Returns:
        批量训练数据
    """
    train_data = preprocess.train_data
    token_to_idx = preprocess.token_to_idx
    unk_idx = preprocess.token_to_idx.get('<unk>')
    eos_idx = preprocess.token_to_idx.get('<eos>')
    pad_idx = preprocess.token_to_idx.get('<pad>')

    random.shuffle(train_data)

    batch_num = math.ceil(len(train_data) / batch_size)

    for i in range(batch_num):
        if i != batch_num - 1:
            batch_data = train_data[i * batch_size: (i+1) * batch_size]
        else:
            batch_data = train_data[i * batch_size:]

        # 获取当前batch的size和最大长度
        curr_batch_size = len(batch_data)
        max_length = 0
        for line in batch_data:
            max_length = max(max_length, len(line))

        # 申明2个tensor，batch表示输入，target表示输出，二者相差1位（差1位是因为时间步训练）；max_length+1是因为数据最后需要加<eos>
        batch_data_tensor = torch.zeros(curr_batch_size, max_length + 1, device=device)
        target_data_tensor = torch.zeros(curr_batch_size, max_length + 1, dtype=torch.int64, device=device)

        # text to idx，并添加特殊token
        # 遍历每一条数据，j从0开始，line为具体的数据（list形式）
        for j, line in enumerate(batch_data):
            k = 0
            for k, token in enumerate(line):
                batch_data_tensor[j][k] = token_to_idx.get(token, unk_idx)
                # 当不是第一个状态步时，则需要同步向target_data_tensor中添加
                if k >= 1:
                    target_data_tensor[j][k - 1] = token_to_idx.get(token, unk_idx)

            k += 1
            batch_data_tensor[j][k] = eos_idx
            target_data_tensor[j][k - 1] = eos_idx

            for n in range(k + 1, max_length + 1):
                batch_data_tensor[j][n] = pad_idx
            for n in range(k, max_length + 1):
                target_data_tensor[j][n] = pad_idx

        yield batch_data_tensor, target_data_tensor


def segmentation(prefix, segment_length):
    batch_num = math.ceil(len(prefix) / segment_length)

    for i in range(batch_num):
        if i != batch_num - 1:
            yield prefix[i * segment_length: (i+1) * segment_length]
        else:
            yield prefix[i * segment_length:]


def text2token(text: str, token_to_idx: dict, batch_size: int, embedding_level):
    """
    将text（通常是生成时的prefix）转化为一定batch_size的torch.tensor，用来作为批量生成的网络输入
    生成用，所以需要处理<unk>
    Args:
        text (str): prefix字符串
        token_to_idx (dict): 字符到索引的映射词典
        batch_size (int):

    Returns:

    """
    if embedding_level == 'word':
        pass

    elif embedding_level == 'bpe':
        # 获取bpe模型，需要与模型训练时预处理的bpe模型是同一个
        bpe_model_path = '/root/ESfunfuzz/src/CodeGenerator/workspace/bpe_model/bpe_500_vocab.model'
        if not os.path.exists(bpe_model_path): raise FileNotFoundError('未检索到bpe分词模型，请重试.')
        sp = spm.SentencePieceProcessor()
        sp.Load(model_file=bpe_model_path)

        segmented_list = sp.encode(text, out_type='str')
        token_tensor = torch.zeros(batch_size, len(segmented_list), device=device)
        for idx, token in enumerate(segmented_list):
            token_tensor = token_tensor.index_fill(dim=1,
                                                   index=torch.tensor([idx], device=device),
                                                   value=token_to_idx.get(token, token_to_idx.get('<unk>')))

    else:
        token_tensor = torch.zeros(batch_size, len(text), device=device)
        for idx, char in enumerate(text):
            token_tensor = token_tensor.index_fill(dim=1,
                                                   index=torch.tensor([idx], device=device),
                                                   value=token_to_idx.get(char, token_to_idx.get('<unk>')))

    return token_tensor


def syntax_check(code):
    checker = execjs.compile("""
        function check(code) {
            try {
                eval(code);
                return true;
            } catch (e) {
                return !(e instanceof SyntaxError);
            }
        }
     """)
    return checker.call("check", code)


def cut(text):
    # 1.按<eos>切分
    if '<eos>' in text:
        return text.split('<eos>')[0]

    # 2.按括号切分
    longest_idx = 0
    bracket_left = 0
    bracket_right = 0
    brace_left = 0
    brace_right = 0
    for idx, char in enumerate(text):
        if char == '(': bracket_left += 1
        if char == ')': bracket_right += 1
        if char == '{': brace_left += 1
        if char == '}': brace_right += 1

        if bracket_left == bracket_right and brace_left == brace_right and (brace_left != 0 or bracket_left != 0):
            bracket_left = 0
            bracket_right = 0
            brace_left = 0
            brace_right = 0
            longest_idx = idx
    if longest_idx != 0:
        return text[:longest_idx+1]
    else:
        return text

if __name__ == '__main__':
    print(cut('function(){...{...{...}...}}if()dwnaingwag'))
    print(cut('function(){...{...{...}...}}<eos>dwnaingwag'))
    print(cut('function(){...123{...{...}...}}dwnaingwag'))
    print(cut('function(){...123{...{......}}dwnaingwag'))

    a = """
    let x = 'let x'; Object.preventExtensions(this); Object.getOwnPropertyNames(this).concat(Object.getOwnPropertySymbols(this)).forEach(function (p) { Object.defineProperty(this, p, { configurable: true, configurable: true }); }); }"""
    print(cut(a))

    b = """
    let x = 'let x'; Object.preventExtensions(this, "streteplayer") && (this._setProperty("setStyle", this._previous), this._setAttribute("data-" + this._setProperty("selected-type"))); }"""
    print(cut(b))

    c = """
    let x = 'let x'; Object.preventExtensions(this); Object.getOwnPropertyNames(this).concat(Object.getOwnPropertySymbols(this)).forEach(function (p) { Object.defineProperty(this, p, { configurable: false, value: true }); return this; }); }"""
    print(cut(c))

    d = """
          if(y){(wjalgnawlgn"""
    print(cut(d))

    g = """
        var o = {}; var i; for (i = 0; i < 65530; ++i) o['p' + i] = 0; var add; var t; var o; if (typeof info === 'string') { if (typeof str !== 'string') { toString = false; i < 65540; ++i) { add = true; for (var p in o) { if (add) { add = false; print(i); o['p' + i] = 0; } } }"""
    print(cut(g))

    f = """
    var o = {}; var i; for (i = 0; i < 65530; ++i) o['p' + i] = 0; var add; var foundOffset = 0; var tail1 = false; var i; i < 65540; ++i) { add = true; for (var p in o) { if (add) { add = false; print(i); o['p' + i] = 0; } } }"""
    print(cut(f))
