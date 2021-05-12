# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: train.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/3
# @Description: 
# @Input:
# @Output:
#

import os
import torch
import torch.nn as nn


from CodeGenerator.model import LSTM
from tqdm import tqdm


from CodeGenerator.preprocess import preprocessor
from CodeGenerator.conf import hparams
from CodeGenerator.utils import *


device = torch.device(f"cuda:{hparams.gpu}" if torch.cuda.is_available() else "cpu")


if __name__ == '__main__':

    # 在工作目录下保存配置文件和词汇表
    workspace_path = os.path.join('CodeGenerator/workspace', hparams.workspace)
    save_json(hparams.__dict__, os.path.join(workspace_path, 'hparams.json'))
    save_json(preprocessor.token_to_idx, os.path.join(workspace_path, 'token_to_idx.json'))
    save_json(preprocessor.idx_to_token, os.path.join(workspace_path, 'idx_to_token.json'))

    token_to_idx = preprocessor.token_to_idx
    vocab_size = len(token_to_idx)
    assert vocab_size == preprocessor.token_number

    # 模型声明
    model = LSTM(vocab_size,
                 vocab_size,  # output_size即vocab_size
                 hparams.embedding_size,
                 hparams.hidden_size,
                 hparams.n_layers,
                 device,
                 hparams.dropout)

    model = model.to(device)

    # 定义损失函数和优化器
    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=hparams.lr)

    # 模型训练
    print()
    print("模型训练中，请耐心等待...")
    all_losses = []
    for e in tqdm(range(1, hparams.epoch + 1)):

        data_iter = get_batch_iter(preprocessor, hparams.batch_size)
        total_loss = 0
        n_batches = 0

        # batch iter
        for idx, (input_batch, target_batch) in enumerate(data_iter):
            # input_batch: (batch_size, seq_length)
            # target_batch: (batch_size, seq_length)，与input错1位
            curr_batch_size = input_batch.size(0)

            hidden = model.init_hidden(curr_batch_size)
            model.zero_grad()

            # logit: (batch_size, seq_length, hidden_size)
            logit, _ = model(input_batch, hidden)

            # 计算temperature
            logit = logit / hparams.temperature

            # 维度削减，便于使用CrossEntropyLoss计算损失（其只接受二维）
            # logit_2d: (seq_length * batch_size, hidden_size)
            logit_2d = logit.contiguous().view(-1, logit.size(2))

            # 将target_batch压缩成一维，以便计算损失
            # target_batch: (batch_size * seq_length)
            target_batch = target_batch.contiguous().view(-1)
            loss = loss_function(logit_2d, target_batch)

            total_loss += loss
            loss.backward()

            # 梯度裁剪&层归一化
            nn.utils.clip_grad_norm_(model.parameters(), hparams.grad_clip)

            # 优化参数
            optimizer.step()
            n_batches += 1

        all_losses.append(total_loss/n_batches)

        print(f"第{e}个epoch的loss为: {total_loss/n_batches}")

        # 每隔一定的epoch保存一次模型
        if e % hparams.save_every_epoch == 0:
            torch.save(model, os.path.join(workspace_path, f'model_{e}.ckpt'))

    # 绘制loss图像
    import matplotlib.pyplot as plt
    from matplotlib.pyplot import savefig

    plt.figure()
    plt.plot(all_losses)
    savefig(os.path.join(workspace_path, 'loss.jpg'))
