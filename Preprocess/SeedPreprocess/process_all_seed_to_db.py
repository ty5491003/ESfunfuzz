# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: process_all_seed_to_db.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/30
# @Description: 
# @Input:
# @Output:
#
from tqdm import tqdm
from Fuzzer.utils import get_file_abspath_list_from_dir, read_file, write_file, get_id, round_up
from Fuzzer.fuzzer import Fuzzer, Result
from Fuzzer.testcase import DataBase

from CodeGenerator.conf import hparams


if __name__ == '__main__':
    task_path_list = ['Seeds/chakra_seeds',
                      'Seeds/hermes_seeds',
                      'Seeds/jerryscript_seeds',
                      'Seeds/rhino_seeds',
                      'Seeds/Test262_seeds']

    # 构建Fuzzer，建立数据库连接
    fuzzer = Fuzzer(hparams.engines, hparams.timeout)
    database = DataBase(hparams.seed_pool_url)

    for task_path in task_path_list:
        _from = task_path.split('/')[1]

        file_list = get_file_abspath_list_from_dir(task_path, False)

        for file in tqdm(file_list):

            code_str = read_file(file)

            fuzzing_result = fuzzer.run_testcase_multi_threads(code_str)
            fuzzing_testcase = Result.result_map_to_testcase(fuzzing_result, hparams.timeout, 0)
            fuzzing_testcase.remark = _from
            database.add(fuzzing_testcase)
