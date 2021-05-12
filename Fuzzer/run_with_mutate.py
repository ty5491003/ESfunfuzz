import re
from time import time

from CaseMutator.mutator import Mutator
from Fuzzer.utils import seconds_to_date
from Fuzzer.fuzzer import Fuzzer, Result
from Fuzzer.testcase import DataBase
from CodeGenerator.conf import hparams


if __name__ == '__main__':
    # 环境检查
    from Fuzzer.environment_check import check
    check()

    # 设置计数器
    seed_count = 0
    total_count = 0
    new_seed_count = 0
    filtered_case_count = 0

    # 构建Fuzzer
    fuzzer = Fuzzer(hparams.engines, hparams.timeout)
    mutator = Mutator()
    start_time = time()

    # 创建数据库连接
    database = DataBase(hparams.seed_pool_url)
    print('-' * 40)

    while True:
        try:
            # step1: 从种子数据库中随机选择一个种子，并将其用例包装为可以突变的形式
            seed_testcase = database.get_a_record_randomly()
            seed_count += 1

            code_str = seed_testcase.testcase
            code_str = 'var NISLFuzzingFunc = function() {' + code_str + '}; NISLFuzzingFunc();'

            # step2: 对种子进行定向突变
            mutated_testcases = mutator.mutate(code_str)

            # step3: 开始
            for testcase in mutated_testcases:
                total_count += 1

                # 对new_testcase格式化
                testcase = re.sub(' +', ' ', testcase.strip().replace('\n', ' ').replace('\t', ' '))

                # 对新生成的用例执行fuzzing
                new_fuzzing_result = fuzzer.run_testcase_multi_threads(testcase)
                new_fuzzing_testcase = Result.result_map_to_testcase(new_fuzzing_result, hparams.timeout, seed_testcase.id)
                new_fuzzing_testcase.remark = 'mutated'  # remark中加上更多信息，便于回溯

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

                # 每fuzzing 100个新用例，则打印一次当前的情况汇总
                if total_count % 100 == 0:
                    this_time = time()
                    seconds = int(this_time-start_time) + 1
                    print(f'Fuzzing已持续:                 {seconds_to_date(seconds)}')
                    print(f'已Fuzzing种子用例:              {seed_count}')
                    print(f'已Fuzzing新生成用例:            {total_count}')
                    print(f'新生成的种子用例数量:            {new_seed_count}')
                    print(f'被过滤的用例数量:               {filtered_case_count}')
                    print(f'Fuzzing的速度为:               {format(total_count/seconds, ".2f")}个/秒')
                    print('-' * 40)

        except Exception:
            pass