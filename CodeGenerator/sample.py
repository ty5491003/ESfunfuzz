# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: sample.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/18
# @Description: 
# @Input:
# @Output:
#

import torch
from CodeGenerator.utils import text2token, segmentation


def sample_solo(model, prefix, max_gen_length, token_to_idx, idx_to_token, segment_length, embedding_level='char', new_line_number=-1, temperature=1.0, sample=False):
    """
    采样方法，给定参数，以单条的形式开始生成（续写）代码。此方法主要用来执行Fuzzing过程中的种子用例突变
    Args:
        model (torch.model): 生成模型
        prefix (str): 生成前缀
        max_gen_length (int): 生成的最大字符个数
        token_to_idx (dict): 映射词典
        idx_to_token (dict): 映射词典
        segment_length (int): prefix切分的段长度，防止GPU OOM，默认1000
        new_line_number(int): 生成的新行的数量，-1表示续写生成（不受数量限制），>0时表示生成固定的多少行
        temperature(float): 生成的多样性，越高则越多样，1.0表示不启用

    Returns:
        str, 即生成内容
    """
    with torch.no_grad():
        gen_code_list = prefix

        # 初始化隐藏状态
        hidden = model.init_hidden(1)

        # prefix可能过长，导致GPU OOM，因此需要对prefix进行分段，然后分段预测，并求得最终的hidden
        prefix_iter = segmentation(prefix, segment_length)
        for prefix in prefix_iter:
            # input_batch: (1, len(prefix))
            input_batch = text2token(prefix, token_to_idx, 1, embedding_level)
            # logit: (1, len(prefix), output_size)
            logit, hidden = model(input_batch, hidden)

        # logit_2d: (1, output_size)
        logit_2d = logit[:, -1, :]

        # prob: (1, output_size)
        prob = logit_2d.softmax(dim=1)

        # 设定采样策略
        if sample:
            topi = torch.multinomial(prob, 1)
        else:
            _, topi = prob.topk(1)

        # 生成内容添加
        gen_code_list += idx_to_token.get(int(topi[0].data))

        # 开始后续生成，在一次生成多条的情况下，采取的策略是直接生成最大长度，再cut
        end_mark_number = 0

        for _ in range(max_gen_length):
            # logit: (1, 1, output_size)
            logit, hidden = model(topi, hidden)

            # 计算temperature
            logit = logit / temperature

            # logit_2d: (1, output_size)
            logit_2d = logit[:, -1, :]
            prob = logit_2d.softmax(dim=1)
            _, topi = prob.topk(1)

            # 获取到生成内容
            new_token = idx_to_token.get(int(topi[0].data))

            # 判断是否生成结束符而终止
            if new_token == '<eos>':
                break

            # 生成内容添加
            gen_code_list += new_token

            # 判断是否达到行数上限而终止
            # 生成固定行数时，batch_size应固定为1，所以直接取idx=0时的结果即可
            if new_token == ';':
                end_mark_number += 1
                if end_mark_number == new_line_number:
                    break

        return gen_code_list


def sample_multi(model, prefix, batch_size, max_gen_length, token_to_idx, idx_to_token, segment_length, embedding_level='char', temperature=1.0):
    """
    采样方法，给定参数，即可批量开始生成（续写）代码。此方法主要用来批量从头开始生成大量数据
    Args:
        model (torch.model): 生成模型
        prefix (str): 生成前缀
        batch_size (int): 每批生成的数量
        max_gen_length (int): 生成的最大字符个数
        token_to_idx (dict): 映射词典
        idx_to_token (dict): 映射词典
        segment_length (int): prefix切分的段长度，防止GPU OOM，默认1000
        temperature(float): 生成的多样性，越高则越多样，1.0表示不启用

    Returns:
        (list)，batch_size个生成内容
    """
    with torch.no_grad():
        # gen_code_list: ['function', 'function', ...] 表示生成的数据
        gen_code_list = [prefix] * batch_size

        # 初始化隐藏状态
        hidden = model.init_hidden(batch_size)

        # prefix可能过长，导致GPU OOM，因此需要对prefix进行分段，然后分段预测，并求得最终的hidden
        prefix_iter = segmentation(prefix, segment_length)
        for prefix in prefix_iter:
            # input_batch: (batch_size, len(prefix))
            input_batch = text2token(prefix, token_to_idx, batch_size, embedding_level)
            # logit: (batch_size, len(prefix), output_size)
            logit, hidden = model(input_batch, hidden)

        # 计算temperature
        logit = logit / temperature

        # logit_2d: (batch_size, output_size)
        logit_2d = logit[:, -1, :]

        # prob: (batch_size, output_size)
        prob = logit_2d.softmax(dim=1)

        # TODO：目前采用贪心采样
        # topi: (batch_size, 1)
        _, topi = prob.topk(1)

        # 生成内容添加
        for idx in range(topi.size(0)):
            gen_code_list[idx] = gen_code_list[idx] + idx_to_token.get(int(topi[idx].data))

        for _ in range(max_gen_length):
            # logit: (batch_size, 1, output_size)
            logit, hidden = model(topi, hidden)

            # logit_2d: (batch_size, output_size)
            logit_2d = logit[:, -1, :]
            prob = logit_2d.softmax(dim=1)
            _, topi = prob.topk(1)

            # 生成内容添加
            for idx in range(topi.size(0)):
                gen_code_list[idx] = gen_code_list[idx] + idx_to_token.get(int(topi[idx].data))

        return gen_code_list
