import os
import math
import logging
import subprocess
import tempfile
import pathlib

from tqdm import tqdm
from threading import Thread


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


def multiprocess_evaluate(lines, engine, n_threading):
    # 根据线程数来
    temp_all = []
    flag_data = []
    thread_pool = []
    batch_num = math.ceil(len(lines) / n_threading)

    for i in range(n_threading):
        temp = []
        temp_all.append(temp)
        batch_data = lines[i * batch_num: (i + 1) * batch_num]
        thread = Thread(target=execute, args=(batch_data, temp, engine))
        thread_pool.append(thread)
        thread.start()

    for _thread in thread_pool:
        _thread.join()

    for temp in temp_all:
        flag_data += temp

    return flag_data


def execute(lines, flag_data, engine):
    # 执行用例
    for line in tqdm(lines, ncols=60):

        # 写入临时文件，并使用ChakraCore引擎执行
        with tempfile.NamedTemporaryFile(prefix="ESfunfuzz_Testcase_", delete=True) as f:
            p = pathlib.Path(f.name)
            p.write_text(line, encoding='utf-8')

            cmd = ["timeout", "-s9", '10', engine, str(p)]
            pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = pro.communicate()
            returncode=pro.returncode

        # 根据执行结果判断是否通过
        if judge_pass(returncode, stdout, stderr):
            flag_data.append(True)


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


if __name__ == '__main__':
    # 参数配置
    engine = '/root/.jsvu/ChakraCoreFiles/bin/ch'
    data_dir = '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data'
    n_threading = int(os.cpu_count() / 2)
    logger_config(prefix='Eval', log_file='/root/ESfunfuzz/Evaluation/Chapter_5_3_2/log.txt')

    # 指定评估数据
    gen_files = [
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/char_10.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/char_20.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/char_30.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/char_40.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/char_50.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/bpe_10.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/bpe_20.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/bpe_30.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/bpe_40.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/bpe_50.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/word_10.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/word_20.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/word_30.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/word_40.txt',
        '/root/ESfunfuzz/Evaluation/Chapter_5_3_2/gen_data/word_50.txt'
    ]

    # 开始评估
    for file in gen_files:
        logging.info(f'正在对{file}进行统计...')

        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 执行统计
        result = multiprocess_evaluate(lines, engine, n_threading)

        # 统计结果并写入日志
        logging.info(f'共有{len(lines)}个用例，其中通过的有{len(result)}个，通过率为{len(result)/len(lines)}')
