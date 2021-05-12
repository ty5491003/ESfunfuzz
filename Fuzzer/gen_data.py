import os
import re
import torch
import random
import tempfile
import pathlib
import subprocess


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
from CodeGenerator.utils import list_insert_db


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


def execute(testcase, engine):
    def judge_pass(returncode, stdout, stderr) -> bool:
        if returncode == -9:
            return False

        # 若returncode为负，且不为-9，则判断为crash
        if returncode < 0:
            return False

        # 接下来是returncode>=0的情况，先针对chakra这个特例来进行判断：
        if stderr != '':
            return False
        else:
            return True

    # 写入临时文件，并使用ChakraCore引擎执行
    with tempfile.NamedTemporaryFile(prefix="ESfunfuzz_Testcase_", delete=True) as f:
        p = pathlib.Path(f.name)
        p.write_text(testcase, encoding='utf-8')

        cmd = ["timeout", "-s9", '10', engine, str(p)]
        pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = pro.communicate()
        returncode=pro.returncode

    # 根据执行结果判断是否通过
    return judge_pass(returncode, stdout, stderr)


if __name__ == '__main__':
    # 环境检查
    from Fuzzer.environment_check import check
    check()

    # 读取工作路径和训练词汇表
    print("正在恢复词汇表和模型，请稍等...")
    workspace_path = os.path.dirname(hparams.gen_model)
    token_to_idx = load_json(os.path.join(workspace_path, 'token_to_idx.json'))
    idx_to_token = load_json(os.path.join(workspace_path, 'idx_to_token.json'), transfer=True)

    # 恢复模型（注意load方法没有device参数）
    model = torch.load(hparams.gen_model, map_location=f'cuda:{hparams.gpu}').to(device)
    model.device = device

    # 设置计数器
    total_count = 0
    pass_count = 0
    no_pass_count = 0
    engine = '/root/.jsvu/ChakraCoreFiles/bin/ch'
    pass_testcases = []
    no_pass_testcases = []
    pass_db = '/root/ESfunfuzz/Data/pass.db'
    no_pass_db = '/root/ESfunfuzz/Data/no_pass.db'

    # 创建数据库连接
    database = DataBase(hparams.seed_pool_url)

    while True:
        # step1: 从种子数据库中随机选择一个种子，并读取其结果
        seed_testcase = database.get_a_record_randomly()
        code_str = seed_testcase.testcase

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
                                   token_to_idx=token_to_idx,
                                   idx_to_token=idx_to_token,
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

            # 根据用例是否通过的结果，将其写入不同的数据库
            if execute(new_testcase, engine):
                pass_count += 1
                pass_testcases.append(new_testcase)
                if len(pass_testcases) == 100:
                    list_insert_db(pass_testcases, pass_db)
                    pass_testcases = []

            else:
                no_pass_count += 1
                no_pass_testcases.append(new_testcase)
                if len(no_pass_testcases) == 100:
                    list_insert_db(no_pass_testcases, no_pass_db)
                    no_pass_testcases = []

            # 打印生成的信息
            if total_count % 200 == 0:
                print(f'当前已生成{total_count}条用例：')
