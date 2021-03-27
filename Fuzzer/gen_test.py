# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: gen_test.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2021/1/7
# @Description: 
# @Input:
# @Output:
#


import os
import re
import torch
import random

from typing import *
from time import time

from Fuzzer.utils import seconds_to_date, read_file, get_id, round_up
from Fuzzer.fuzzer import Fuzzer, Result
from Fuzzer.testcase import DataBase
from Fuzzer.ast_op import js_compile
from Fuzzer.run import get_mutation_points

from CodeGenerator.conf import hparams
from CodeGenerator.utils import load_json, cut
from CodeGenerator.sample import sample_solo
from CodeGenerator.model import LSTM


device = torch.device(f"cuda:{hparams.gpu}" if torch.cuda.is_available() else "cpu")


def write_file(file_path, content: str):
    with open(file_path, 'a+', encoding='utf-8') as f:
        f.write(content)


if __name__ == '__main__':
    # 读取工作路径和训练词汇表
    print("正在恢复词汇表和模型，请稍等...")
    workspace_path = os.path.dirname(hparams.gen_model)
    char_to_idx = load_json(os.path.join(workspace_path, 'char_to_idx.json'))
    idx_to_char = load_json(os.path.join(workspace_path, 'idx_to_char.json'), transfer=True)

    # 恢复模型（注意load方法没有device参数）
    model = torch.load(hparams.gen_model).to(device)
    model.device = device

    # 设置计数器
    seed_count = 0
    total_count = 0
    new_seed_count = 0
    syntax_correct_count = 0
    semantic_correct_count = 0
    filtered_case_count = 0

    # 构建Fuzzer和Filter
    fuzzer = Fuzzer(hparams.engines, hparams.timeout)
    start_time = time()

    # 创建数据库连接
    database = DataBase(hparams.seed_pool_url)

    code_str = """var o = {}; var i; for (i = 0; i < 65530; ++i) o['p' + i] = 0; var add; for (; i < 65540; ++i) { add = true; for (var p in o) { if (add) { add = false; print(i); o['p' + i] = 0; } } }
    """
    new_file = 'Fuzzer/gen_test.js'
    seed_count += 1

    write_file(new_file, code_str + '\n')

    # step2:返回其中的所有变异点的索引
    mutation_point_indexes = get_mutation_points(code_str, js_compile)
    print(mutation_point_indexes)

    # step3:按变异点，依次变异，并执行fuzzing决定是否保存
    for index in mutation_point_indexes:
        total_count += 1
        prefix = code_str[:index+1]
        tail = code_str[index+1:]

        write_file(new_file, 'prefix:\n')
        write_file(new_file, prefix + '\n')

        gen_code = sample_solo(model=model,
                               prefix=prefix,
                               max_gen_length=hparams.max_gen_length,
                               char_to_idx=char_to_idx,
                               idx_to_char=idx_to_char,
                               segment_length=hparams.segment_length,
                               new_line_number=hparams.new_line_number,
                               sample=hparams.sample)

        # 根据参数判断是续写生成还是插入生成
        if hparams.new_line_number == -1:
            new_testcase = cut(gen_code)
            write_file(new_file, 'gen_code:\n')
            write_file(new_file, gen_code + '\n')

        # 插入生成
        else:
            assert hparams.new_line_number > 0, '请指定正确的new_line_number参数，应该为-1或者大于0'

            # 对tail做修剪，防止tail中遗留的上一句内容导致用例语法不正确
            tail = tail[tail.find(';') + 1:]
            new_testcase = cut(gen_code + tail)
            write_file(new_file, 'gen_code:\n')
            write_file(new_file, gen_code + tail + '\n')

        # 对new_testcase格式化
        new_testcase = re.sub(' +', ' ', new_testcase.strip().replace('\n', ' ').replace('\t', ' '))

        write_file(new_file, 'new_testcase:\n')
        write_file(new_file, new_testcase + '\n')
        write_file(new_file, '\n\n')
