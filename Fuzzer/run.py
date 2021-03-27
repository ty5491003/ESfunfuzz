# -*- coding: utf-8 -*-
#
# @Version: python 3.7
# @File: run.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/15
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
from uuid import uuid4

from Fuzzer.utils import seconds_to_date, read_file, write_file, get_id, round_up
from Fuzzer.fuzzer import Fuzzer, Result
from Fuzzer.filter import Filter
from Fuzzer.testcase import DataBase
from Fuzzer.ast_op import js_compile

from CodeGenerator.conf import hparams
from CodeGenerator.utils import load_json, cut
from CodeGenerator.sample import sample_solo
from CodeGenerator.model import LSTM


device = torch.device(f"cuda:{hparams.gpu}" if torch.cuda.is_available() else "cpu")


def get_mutation_points(code_str: str, js_compile) -> List[int]:
    """
    从code_str中选取变异点
    Args:
        code_str (str): 待变异的语法正确的JS代码

    Returns:
        list，变异点的索引的列表
    """
    point_indexes = []
    try:
        # 通过语法树，选择适当的变异点
        point_indexes = js_compile.call('get_mutation_points', code_str)
    except:
        # 假如语法树解析过程发生异常，则随机选取变异点
        length = len(code_str)
        if length > 1:
            point_indexes = [int(length / 3), int(length / 2)]
            for _ in range(3):
                point_indexes.append(random.randint(1, length - 1))

    # 至多返回5个变异点
    random.shuffle(point_indexes)
    return point_indexes[:5]


if __name__ == '__main__':
    # 环境检查
    from Fuzzer.environment_check import check
    check()

    # 读取工作路径和训练词汇表
    print("正在恢复词汇表和模型，请稍等...")
    workspace_path = os.path.dirname(hparams.gen_model)
    char_to_idx = load_json(os.path.join(workspace_path, 'char_to_idx.json'))
    idx_to_char = load_json(os.path.join(workspace_path, 'idx_to_char.json'), transfer=True)

    # 恢复模型（注意load方法没有device参数）
    model = torch.load(hparams.gen_model, map_location=f'cuda:{hparams.gpu}').to(device)
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

    while True:
    # for i in range(1):    # 测试用
        # step1: 从种子数据库中随机选择一个种子，并读取其结果
        seed_testcase = database.get_a_record_randomly()
        code_str = seed_testcase.testcase
        seed_count += 1

        # step2:返回其中的所有变异点的索引
        mutation_point_indexes = get_mutation_points(code_str, js_compile)

        # step3:按变异点，依次变异，并执行fuzzing决定是否保存
        for index in mutation_point_indexes:
            total_count += 1
            prefix = code_str[:index+1]
            tail = code_str[index+1:]

            gen_code = sample_solo(model=model,
                                   prefix=prefix,
                                   max_gen_length=hparams.max_gen_length,
                                   token_to_idx=char_to_idx,
                                   idx_to_token=idx_to_char,
                                   segment_length=hparams.segment_length,
                                   new_line_number=hparams.new_line_number,
                                   temperature=hparams.temperature,
                                   sample=hparams.sample)

            # 根据参数判断是续写生成还是插入生成
            if hparams.new_line_number == -1:
                new_testcase = cut(gen_code)

            # 插入生成
            else:
                assert hparams.new_line_number > 0, '请指定正确的new_line_number参数，应该为-1或者大于0'

                # 对tail做修剪，防止tail中遗留的上一句内容导致用例语法不正确
                tail = tail[tail.find(';') + 1:]
                new_testcase = cut(gen_code + tail)

            # 对new_testcase格式化
            new_testcase = re.sub(' +', ' ', new_testcase.strip().replace('\n', ' ').replace('\t', ' '))

            # 对新生成的用例执行fuzzing
            new_fuzzing_result = fuzzer.run_testcase_multi_threads(new_testcase)
            new_fuzzing_testcase = Result.result_map_to_testcase(new_fuzzing_result, hparams.timeout, seed_testcase.id)
            new_fuzzing_testcase.remark = f'{hparams.new_line_number}, {index}'  # remark中加上更多信息，便于回溯

            # 进行语法正确情况统计
            if Result.is_syntax_correct(new_fuzzing_result.testcase, hparams.uglifyjs_path):
                syntax_correct_count += 1
            if Result.is_semantic_correct(new_fuzzing_result):
                semantic_correct_count += 1

            # 假如新生成的用例是可疑用例，才有意义
            if new_fuzzing_result.is_suspicious():

                # 新旧比较（即去重）
                if database.compare_and_filter(new_fuzzing_testcase):
                    new_seed_count += 1
                    database.add(new_fuzzing_testcase)

                # 被过滤的用例最好也写入数据库，便于回溯
                else:
                    filtered_case_count += 1
                    database.add(Result.testcase_transform_to_filtered_testcase(new_fuzzing_testcase))

            # print('-' * 40)
            # print(f'syntax: {Result.is_syntax_correct(new_fuzzing_result.testcase, hparams.uglifyjs_path)}')
            # print(f'semantic: {Result.is_semantic_correct(new_fuzzing_result)}')
            # print(new_fuzzing_result.serialize())

        # 每fuzzing50个种子，打印一次当前的情况汇总
        if (seed_count % 50 == 0 or seed_count == 1) and total_count != 0:
            this_time = time()
            seconds = int(this_time-start_time) + 1
            print(f'Fuzzing已持续:                 {seconds_to_date(seconds)}')
            print(f'已Fuzzing种子用例:              {seed_count}')
            print(f'已Fuzzing新生成用例:            {total_count}')
            print(f'新生成用例中语法正确的用例及占比:  {syntax_correct_count}({round_up(syntax_correct_count/total_count*100)}%)')
            print(f'新生成用例中语义正确的用例及占比:  {semantic_correct_count}({round_up(semantic_correct_count / total_count * 100)}%)')
            print(f'新生成的种子用例数量:            {new_seed_count}')
            print(f'被过滤的用例数量:               {filtered_case_count}')
            print(f'Fuzzing的速度为:               {format(total_count/seconds, ".2f")}个/秒')
            print('-' * 40)
