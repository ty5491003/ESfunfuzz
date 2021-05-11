# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: conf.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/11/27
# @Description: 
# @Input:
# @Output:
#

import argparse


class Hparams:
    parser = argparse.ArgumentParser()

    # 工作路径
    parser.add_argument('--workspace', default='default', type=str, help="本次文件路径")

    # 训练数据相关
    parser.add_argument('--data_path', default='/root/ESfunfuzz/data/after07.db', type=str)
    parser.add_argument('--data_number', default=-1, type=int, help="训练数据数量")
    parser.add_argument('--max_length', default=-1, type=int, help="训练数据最大字符长度，-1表示不限制")
    parser.add_argument('--split_length', default=-1, type=int, help="训练数据最大字符长度，-1表示不限制")
    parser.add_argument('--embedding_level', default='char', type=str, help="训练数据的编码级别，char/word/bpe")
    parser.add_argument('--vocab_size', default=-1, type=int, help="词汇表数量，排名靠后的词将被替换为<unk>，-1表示不限制")

    # 模型相关
    parser.add_argument('--batch_size', default=32, type=int)
    parser.add_argument('--embedding_size', default=32, type=int, help="词嵌入维度")
    parser.add_argument('--n_layers', default=2, type=int)
    parser.add_argument('--hidden_size', default=512, type=int, help="每个隐藏层的神经元个数")
    parser.add_argument('--dropout', default=0.2, type=float)
    parser.add_argument('--lr', default=0.001, type=float, help="学习率")
    parser.add_argument('--grad_clip', default=0.1, type=float, help="梯度裁剪值")
    parser.add_argument('--temperature', default=1.0, type=float)

    # 模型训练相关
    parser.add_argument('--epoch', default=50, type=int)
    parser.add_argument('--gpu', default=1, type=int, help="使用的GPU编号(默认1号)")
    parser.add_argument('--save_every_epoch', default=10, type=int, help="每隔多少epoch保存一次模型")

    # 代码生成相关
    parser.add_argument('--gen_model', default='CodeGenerator/workspace/char/model_40.ckpt', type=str, help="生成所使用的模型")
    parser.add_argument('--gen_file', default='gen.txt', type=str, help="保存生成数据的文件名（仅需要指定名称即可）")
    parser.add_argument('--prefix', default='function', type=str, help="生成数据的前缀")
    parser.add_argument('--gen_number', default=64, type=int, help="生成数据的数量")
    parser.add_argument('--gen_batch_size', default=64, type=int, help="生成数据时，一个batch的数量")
    parser.add_argument('--max_gen_length', default=2000, type=int, help="生成数据的最大字符长度")
    parser.add_argument('--segment_length', default=1000, type=int, help="prefix分段的段长度，避免GPU OOM")
    parser.add_argument('--sample', default=False, type=bool, help="True表示按概率采样，False表示贪心采样")

    # Fuzzing相关
    # 注意这里4个引擎的先后顺序不能变化，必须是：chakra、SpiderMonkey、jsc、v8
    # 并且引擎地址必须是绝对地址（也不能使用 '~'）
    parser.add_argument('--engines', default=[
        "/root/.jsvu/ch",
        "/root/.jsvu/sm",
        "/root/.jsvu/jsc",
        "/root/.jsvu/v8"
    ], type=list, help="待测引擎列表")
    parser.add_argument('--timeout', default=15, type=int, help="用例执行的最大时间")
    parser.add_argument('--new_line_number', default=-1, type=int, help="变异时生成的新行的个数，要求为-1或者大于0")
    parser.add_argument('--seed_pool_url', default='sqlite:////root/ESfunfuzz/Data/ty_fuzzing_data.db', type=str, help="指定本次Fuzzing的种子池的数据库url")


hparams = Hparams().parser.parse_known_args()[0]
