# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: environment_check.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2021/2/2
# @Description: 在正式地开始Fuzzing之前进行，以检查所有环境是否安装齐全
# @Input:
# @Output:
#

from CodeGenerator.conf import hparams
from Fuzzer.ast_op import js_compile
from Fuzzer.testcase import DataBase
from Fuzzer.fuzzer import Fuzzer


def check():
    # 1. 验证node以及npm包是否安装
    print("正在进行运行环境验证，请稍等...")
    try:
        code_str = "print('hello world');"
        point_indexes = js_compile.call('get_mutation_points', code_str)
        print("[1]node以及npm包安装正确.")
    except:
        print("[1]node以及npm包安装有误，请检查后重试.")
        exit()

    # 2. 验证数据库连接是否有效
    database = DataBase(hparams.seed_pool_url)
    try:
        database.test_db_connect()
        print("[2]数据库连接正确.")
    except:
        print("[2]数据库连接异常，请检查后重试.")


    # 3. 验证待测引擎是否有效
    fuzzer = Fuzzer(hparams.engines, hparams.timeout)
    print("[3]待测引擎配置正确.")

    print("所有环境检查无误，即将开始Fuzzing.")
