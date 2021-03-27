# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: preprocess.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/11/27
# @Description:
# @Input:
# @Output:
#
import os
import logging
import math
import sentencepiece as spm
from threading import Thread

from tqdm import tqdm
from collections import Counter

from CodeGenerator.conf import hparams
from CodeGenerator.db_operation import DBOperation
from CodeGenerator.utils import get_files_from_dir, logger_config
from Fuzzer.ast_op import js_compile

# 创建本次训练的工作目录
if not os.path.exists('CodeGenerator/workspace'):
    os.mkdir('CodeGenerator/workspace')
workspace_path = os.path.join('CodeGenerator/workspace', hparams.workspace)
if not os.path.exists(workspace_path):
    os.mkdir(workspace_path)
else:
    raise FileExistsError("指定的工作路径已存在，请重新输入")

log_file = os.path.join(workspace_path, 'log.txt')
logger_config(prefix='train', log_file=log_file)
logging.info(f"本次执行的工作路径为: {workspace_path}")


class Preprocessor:
    def __init__(self, hparams):
        self.hparams = hparams
        self.data_path = hparams.data_path
        self.data_number = hparams.data_number
        self.max_length = hparams.max_length
        self.split_length = hparams.split_length
        self.embedding_level = hparams.embedding_level

        # 读取并预处理
        train_data = self.read_data(self.data_path)
        self.init_data_number = len(train_data)
        train_data = self.preprocess(train_data)
        self.train_data = train_data

        # 分词并创建词典
        self.token_to_idx, self.idx_to_token, self.token_number = self.statistic(train_data, hparams.vocab_size)

    @staticmethod
    def read_data(data_path):
        functions = []
        data_format = os.path.splitext(data_path)[1]

        # 从数据库中读
        if data_format == '.db':
            db_operation = DBOperation(data_path, 'corpus')
            functions = db_operation.query_all(["Content"])
            # 去除元组包裹
            functions = [i[0] for i in functions]

        # 从txt文件中读
        elif data_format == '.txt':

            # 若指定数据路径是目录，则读取该目录中全部文件的数据
            if os.path.isdir(data_path):
                file_list = get_files_from_dir(data_path)
                for file in file_list:
                    with open(file, 'r', encoding='utf-8') as f:
                        functions += f.readlines()

            # 若指定数据路径是文件，则读取该文件中全部数据
            else:
                with open(data_path, 'r', encoding='utf-8') as f:
                    functions += f.readlines()

        else:
            # 抛出异常
            raise ValueError("指定的训练数据文件data_path有误，请检查后重新输入，目前只接受db或者txt(dir)")

        return functions

    def preprocess(self, train_data):
        # 长度过滤、限制数量、数据切分、tokenize
        train_data = self.limit_max_length(train_data, self.max_length)
        train_data = self.limit_numbers(train_data, self.data_number)
        train_data = self.data_split(train_data, self.split_length)
        train_data = self.tokenize(train_data, self.embedding_level)

        return train_data

    @staticmethod
    def limit_max_length(train_data, max_length):
        # -1表示不使用长度过滤
        if max_length == -1:
            logging.info('不启用长度过滤.')
            return train_data
        logging.info('正在进行长度过滤...')
        return [i for i in tqdm(train_data) if len(i) <= max_length - 1]  # -1 for <eos>

    @staticmethod
    def limit_numbers(train_data, data_number):
        # -1表示不使用数量过滤
        if data_number == -1:
            logging.info('不启用数量过滤.')
            return train_data
        logging.info('正在进行数量过滤...')
        return train_data[:data_number]

    @staticmethod
    def data_split(train_data, split_length):
        # -1表示不使用切分
        if split_length == -1:
            logging.info('不启用数据切分.')
            return train_data

        def split(text, length):
            if len(text) <= length:
                return [text]

            count = math.ceil(len(text) / length)
            split_data = []
            for i in range(count):
                if i != count - 1:
                    split_data.append(text[i * length: (i + 1) * length])
                else:
                    split_data.append(text[i * length:])
            return split_data

        # 将每条数据按固定的段长度进行切分
        logging.info('正在进行数据切分...')
        split_data = []
        for line in tqdm(train_data):
            split_data += split(line, split_length)
        return split_data

    @staticmethod
    def tokenize(train_data, embedding_level):
        logging.info(f'正在进行tokenize...')

        def char_tokenize(code):
            return list(code)

        def multiprocess_word_tokenize(train_data):
            tokenized_data = []
            threading_pool = []
            n_threading = int(os.cpu_count() / 2)
            batch_num = math.ceil(len(train_data) / n_threading)
            logging.info(f'当前使用{n_threading}个线程.')

            for i in range(n_threading):
                batch_data = train_data[i * batch_num: (i + 1) * batch_num]
                thread = Thread(target=word_tokenize, args=(batch_data, tokenized_data, js_compile))
                threading_pool.append(thread)
                thread.start()

            for _thread in threading_pool:
                _thread.join()

            return tokenized_data

        def word_tokenize(batch_data, tokenized_data, js_compile):
            special_type = ['Keyword', 'Numeric']
            for code in tqdm(batch_data, ncols=80):
                tokenized_line = []
                result = js_compile.call('tokenize', code)
                for token in result:
                    type = token.get('type')
                    value = token.get('value')
                    if type in special_type:
                        tokenized_line.append(value)
                        tokenized_line.append('▁')
                    else:
                        tokenized_line.append(value)

                tokenized_data.append(tokenized_line)

            return tokenized_data

        def bpe_tokenize(code, sp):
            return sp.encode(code, out_type='str')

        tokenized_data = []
        if embedding_level == 'char':
            for line in tqdm(train_data):
                tokenized_data.append(char_tokenize(line))

        elif embedding_level == 'word':
            tokenized_data = multiprocess_word_tokenize(train_data)

        elif embedding_level == 'bpe':
            # 读取预训练好的bpe模型
            bpe_model_path = '/root/ESfunfuzz/src/CodeGenerator/workspace/bpe_model/bpe_500_vocab.model'
            if not os.path.exists(bpe_model_path): raise FileNotFoundError('未检索到bpe分词模型，请重试.')
            sp = spm.SentencePieceProcessor()
            sp.Load(model_file=bpe_model_path)

            for line in tqdm(train_data):
                tokenized_data.append(bpe_tokenize(line, sp))
        else:
            raise ValueError('指定的编码级别有误，请检查后重试，目前仅接受char/word/bpe')

        return tokenized_data


    def statistic(self, train_data, vocab_size):
        # 首先申明
        token_to_idx = {}
        max_length_actual = 0

        # add <eos> & <pad> & <sos> & <unk>
        # 特殊标志并不需要在数据中加上，只需要在训练之前的text2token阶段添加和替换即可
        # 特殊标志并不需要全部使用，但为了以防万一，在词汇表中先加上会更鲁棒
        token_to_idx['<eos>'] = len(token_to_idx)
        token_to_idx['<pad>'] = len(token_to_idx)
        token_to_idx['<sos>'] = len(token_to_idx)
        token_to_idx['<unk>'] = len(token_to_idx)

        counter = Counter()
        for tokenized_line in train_data:
            counter.update(tokenized_line)
            max_length_actual = max(max_length_actual, len(tokenized_line))

        # 根据vocab_size保留一定词，-1表示所有词都保留
        if vocab_size == -1:
            most_common_token = counter.most_common(len(counter))
        else:
            most_common_token = counter.most_common(vocab_size - 4)
        for idx, item in enumerate(most_common_token, start=len(token_to_idx)):
            token_to_idx[item[0]] = idx

        idx_to_token = {v: k for k, v in token_to_idx.items()}

        # 打印统计信息
        logging.info("训练集信息统计:")
        logging.info(f"训练数据来自于: {self.data_path}")
        logging.info(f"初始的训练数据条数: {self.init_data_number}")
        logging.info(f"最终使用的切分后的训练数据条数: {len(train_data)}")
        logging.info(f"训练数据的最大token长度: {max_length_actual}")
        logging.info(f"训练数据词汇表总个数: {len(token_to_idx)}")

        return token_to_idx, idx_to_token, len(token_to_idx)


# 数据预处理
logging.info("正在进行数据预处理，请稍等...")
preprocessor = Preprocessor(hparams)
