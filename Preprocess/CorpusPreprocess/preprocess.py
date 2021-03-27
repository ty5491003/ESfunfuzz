# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: 新数据处理.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2021/3/18
# @Description: 
# @Input:
# @Output:
#

import re
import math
import execjs

from tqdm import tqdm
from threading import Thread

from CodeGenerator.utils import db2list, list2db


js_compile = execjs.compile("""

    // 楼下服务器地址
    const esprima = require('/export/nisl/ty/node_modules/esprima');
    const escodegen = require('/export/nisl/ty/node_modules/escodegen');
    
    // ty_eval
    // const esprima = require('/root/software/node_modules/esprima');
    // const escodegen = require('/root/software/node_modules/escodegen');

    function remove_comment(code_str) {
        let ast = esprima.parseScript(code_str);
        let new_code = escodegen.generate(ast);
        return new_code;
    }
    """)


def filter(code_str: str):
    # 规则1：有以下关键词的，直接去掉
    filter_keywords = [
        'options',
        'this.constructor',
        'Promise',
        'WScript',
        'nock',
        'timeout',
        'version',
        'arguments'
    ]

    # 规则2：有以下关键词的进行替换
    replace_keywords = {
        'console.log': 'print'
    }

    # 执行规则1
    for word in filter_keywords:
        if word in code_str:
            return False, ''

    # 执行规则2
    for key, value in replace_keywords.items():
        code_str = code_str.replace(key, value)

    return True, code_str


def uniform_format(line):
    """
    统一空格形式，
    Args:
        line ():

    Returns:

    """
    return re.sub(' +', ' ', line.strip().replace('\n', ' ').replace('\t', ' '))


def remove_comment_target(batch_data, target_data, js_compile):
    for line in tqdm(batch_data):
        try:
            target_data.append(js_compile.call('remove_comment', line))
        except:
            continue


def judge_non_english(function_str):
    return all(ord(c) < 128 for c in function_str)


def step1_merge(source_databases):
    all_data = []
    for database_path in source_databases:
        all_data += db2list(database_path)
    all_data = list(set(all_data))
    all_data = [i.strip() for i in all_data]
    return all_data


def step2_filter_keyword(lines):
    filtered_data = []
    for line in tqdm(lines):
        flag, new_line = filter(line)
        if flag:
            filtered_data.append(new_line)
    return filtered_data


def step3_filter_non_english(lines):
    all_english_data = []
    for line in tqdm(lines):
        if judge_non_english(line):
            all_english_data.append(line)
    return all_english_data


def step4_remove_comment(lines):
    removed_comment_data = []
    thread_pool = []
    n_threading = 6
    batch_num = math.ceil(len(lines) / n_threading)

    for i in range(n_threading):
        batch_data = lines[i * batch_num : (i+1) * batch_num]
        thread = Thread(target=remove_comment_target, args=(batch_data, removed_comment_data, js_compile))
        thread_pool.append(thread)
        thread.start()

    for _thread in thread_pool:
        _thread.join()

    return removed_comment_data


def step5_formatting(lines):
    formatted_data = []
    for line in tqdm(lines):
        formatted_data.append(uniform_format(line))
    formatted_data = list(set(formatted_data))
    return formatted_data


def step6_filter_length(lines):
    temp = []
    for line in tqdm(lines):
        if 50 < len(line) < 1000:
            temp.append(line)
    return temp


if __name__ == '__main__':
    source_databases = [
        '/export/nisl/qx/jsCorpusProcessing/data/db/top2000corpus-20200410.db',
        '/export/nisl/qx/jsCorpusProcessing/data/db/bottom2000corpus-20200412.db'
    ]

    # Step1:合并全部数据
    print('[Step1]正在合并所有数据...')
    all_data = step1_merge(source_databases)[:5000]
    print(f'剩余: {len(all_data)}')

    # step2:按关键词过滤
    print('[Step2]正在按关键词过滤...')
    filtered_data = step2_filter_keyword(all_data)
    print(f'剩余: {len(filtered_data)}')

    # Step3:过滤掉所有非英文数据
    print('[Step3]正在过滤所有非英文数据...')
    english_data = step3_filter_non_english(filtered_data)
    print(f'剩余: {len(english_data)}')

    # save
    print('正在保存数据...')
    list2db(english_data, '/export/nisl/ty/new_data/after03.db')

    # Step4:基于AST做移除注释和语法过滤
    print('[Step4]正在基于AST移除注释...')
    removed_comment_data = step4_remove_comment(english_data)
    print(f'剩余: {len(removed_comment_data)}')

    # step5:统一空格形式并去重
    print('[Step5]正在统一格式...')
    formatted_data = step5_formatting(removed_comment_data)
    print(f'剩余: {len(formatted_data)}')

    # save
    print('正在保存数据...')
    list2db(formatted_data, '/export/nisl/ty/new_data/after05.db')

    # step6: 按长度进行过滤
    print('[Step6]正在按长度过滤...')
    filter_length_data = step6_filter_length(formatted_data)
    print(f'剩余: {len(filter_length_data)}')

    # 补充:再过滤一次非英文数据
    print('[补充]正在过滤所有非英文数据...')
    final_data = step3_filter_non_english(filter_length_data)
    print(f'剩余: {len(final_data)}')

    # save
    print('正在保存数据...')
    list2db(final_data, '/export/nisl/ty/new_data/after07.db')
