# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: model.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/11/27
# @Description: 
# @Input:
# @Output:
#

from enum import IntEnum


import torch
from torch import nn
from torch.nn import Parameter
from typing import *


class LinearModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, device, dropout):
        super(LinearModel, self).__init__()
        self.device = device
        self.hidden_size = hidden_size
        self.i2h = nn.Linear(input_size + hidden_size, hidden_size)
        self.i2o = nn.Linear(input_size + hidden_size, output_size)
        self.o2o = nn.Linear(hidden_size + output_size, output_size)
        self.dropout = nn.Dropout(dropout)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        # input: (1, n_chars)
        # hidden: (1, hidden_size)
        input_combined = torch.cat((input, hidden), 1)  # (1, n_chars + hidden_size)
        hidden = self.i2h(input_combined)  # (1, hidden_size)
        output = self.i2o(input_combined)  # (1, n_chars)
        output_combined = torch.cat((hidden, output), 1)  # (1, hidden_size + n_chars)
        output = self.o2o(output_combined)  # (1, n_chars)
        output = self.dropout(output)
        output = self.softmax(output)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, self.hidden_size, device=self.device)


# class LSTMBased(nn.Module):
#     def __init__(self, input_size, hidden_size, output_size, device, dropout):
#         super(LSTMBased, self).__init__()
#         self.device = device
#
#         self.Ct = torch.zeros(hidden_size + input_size, 1)
#         self.ht = torch.zeros(hidden_size + input_size, 1)
#         self.Wf = torch.zeros(hidden_size + input_size, 1)
#         self.Wi = torch.zeros(hidden_size + input_size, 1)
#         self.Wc = torch.zeros(hidden_size + input_size, 1)
#         self.Wo = torch.zeros(hidden_size + input_size, 1)
#         self.bf = torch.zeros(1, 1)
#         self.bi = torch.zeros(1, 1)
#         self.bc = torch.zeros(1, 1)
#         self.bo = torch.zeros(1, 1)
#
#     def initHidden(self):
#         pass
#
#
#     def forward(self, input, hidden):
#         # input: (1, n_chars)
#         # hidden: (1, hidden_size)
#         # forget gate
#         ft = torch.sigmoid_(self.Wf * (torch.cat(hidden, input), 1) + self.bf)
#
#         # input gate
#         it = torch.sigmoid_(self.Wi * (torch.cat(hidden, input), 1) + self.bi)
#         Ct_ = torch.tanh_(self.Wc * (torch.cat(hidden, input), 1) + self.bc)
#         self.Ct = self.Ct * ft + Ct_ * it
#
#         # output gate
#         Ot = torch.sigmoid_(self.Wo * (torch.cat(hidden, input), 1) + self.bo)
#         self.ht = torch.tanh_(self.Ct) * Ot


class Dim(IntEnum):
    batch = 0
    seq = 1
    feature = 2


class NaiveLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        # input gate
        self.W_ii = Parameter(torch.Tensor(input_size, hidden_size))
        self.W_hi = Parameter(torch.Tensor(hidden_size, hidden_size))
        self.b_i = Parameter(torch.Tensor(hidden_size))
        # forget gate
        self.W_if = Parameter(torch.Tensor(input_size, hidden_size))
        self.W_hf = Parameter(torch.Tensor(hidden_size, hidden_size))
        self.b_f = Parameter(torch.Tensor(hidden_size))
        # ???
        self.W_ig = Parameter(torch.Tensor(input_size, hidden_size))
        self.W_hg = Parameter(torch.Tensor(hidden_size, hidden_size))
        self.b_g = Parameter(torch.Tensor(hidden_size))
        # output gate
        self.W_io = Parameter(torch.Tensor(input_size, hidden_size))
        self.W_ho = Parameter(torch.Tensor(hidden_size, hidden_size))
        self.b_o = Parameter(torch.Tensor(hidden_size))

        self.init_weights()

    def init_weights(self):
        for p in self.parameters():
            if p.data.ndimension() >= 2:
                nn.init.xavier_uniform_(p.data)
            else:
                nn.init.zeros_(p.data)

    def forward(self, x: torch.Tensor,
                init_states: Optional[Tuple[torch.Tensor]] = None
                ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Assumes x is of shape (batch, sequence, feature)"""
        bs, seq_sz, _ = x.size()
        hidden_seq = []

        # 正向传播时，可以指定初始状态；未指定则初始化为零向量
        if init_states is None:
            h_t = torch.zeros(self.hidden_size).to(x.device)
            c_t = torch.zeros(self.hidden_size).to(x.device)
        else:
            h_t, c_t = init_states

        # 分时间步开始前向传播
        for t in range(seq_sz):
            x_t = x[:, t, :]

            i_t = torch.sigmoid(x_t @ self.W_ii + h_t @ self.W_hi + self.b_i)
            f_t = torch.sigmoid(x_t @ self.W_if + h_t @ self.W_hf + self.b_f)
            g_t = torch.tanh(x_t @ self.W_ig + h_t @ self.W_hg + self.b_g)
            o_t = torch.sigmoid(x_t @ self.W_io + h_t @ self.W_ho + self.b_o)
            c_t = f_t * c_t + i_t * g_t
            h_t = o_t * torch.tanh(c_t)

            hidden_seq.append(h_t.unsqueeze(Dim.batch))

        hidden_seq = torch.cat(hidden_seq, dim=Dim.batch)

        # reshape from shape (sequence, batch, feature) to (batch, sequence, feature)
        hidden_seq = hidden_seq.transpose(Dim.batch, Dim.seq).contiguous()
        return hidden_seq, (h_t, c_t)


class LSTM(nn.Module):
    def __init__(self, vocab_size, output_size, embedding_size, hidden_size, n_layers, device, drop_prob=0.2):
        super(LSTM, self).__init__()

        self.output_size = output_size
        self.n_layers = n_layers
        self.hidden_dim = hidden_size

        self.embedding = nn.Embedding(vocab_size, embedding_size)
        self.lstm = nn.LSTM(embedding_size, hidden_size, n_layers, dropout=drop_prob, batch_first=True)
        self.dropout = nn.Dropout(drop_prob)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()
        self.softmax = nn.LogSoftmax(dim=1)

        self.device = device

    def forward(self, x, hidden):
        # x: (batch_size, seq_length)
        # tensor([[3., 3., 1.],
        #         [2., 0., 0.]])
        x = x.long()

        # embeds: (batch_size, seq_length, embedding_size)
        # tensor([[[ 0.2440,  1.2621,  0.7175,  0.6792,  0.4442],
        #          [ 0.2440,  1.2621,  0.7175,  0.6792,  0.4442],
        #          [-0.0389,  0.3491, -1.1765, -0.6754, -1.5067]],
        #
        #         [[-0.8609, -1.0538, -0.3753,  0.1988,  0.3225],
        #          [ 1.6748, -0.6093, -0.0239,  0.4957,  0.8354],
        #          [ 1.6748, -0.6093, -0.0239,  0.4957,  0.8354]]],
        #        grad_fn=<EmbeddingBackward>)
        embeds = self.embedding(x)

        # lstm_out: (batch_size, seq_length, hidden_size)
        # tensor([[[ 0.0992, -0.2946,  0.2154, -0.0578,  0.2079,  0.1422],
        #          [ 0.0347, -0.1038,  0.2667,  0.1911,  0.1152,  0.1457],
        #          [ 0.1058, -0.1952,  0.1584, -0.0111,  0.2224,  0.2251]],
        #
        #         [[-0.0144, -0.0722,  0.1879,  0.2138,  0.0387,  0.0720],
        #          [-0.0272, -0.1125,  0.2567,  0.3167,  0.0653,  0.1195],
        #          [ 0.0944, -0.4722,  0.3363,  0.1432,  0.2850,  0.2642]]],
        #        grad_fn=<TransposeBackward0>)
        # hidden: [h,c]  h: (n_layers, batch_size, hidden_size)
        lstm_out, hidden = self.lstm(embeds, hidden)

        # logit: (batch_size, seq_length, output_size)
        # 经过一个线性层（全连接层），将hidden_size转化为output_size(即vocab_size)
        # tensor([[ 0.1310,  0.4738,  0.0281,  0.0661],
        #         [ 0.1092,  0.5697,  0.0385,  0.1127],
        #         [ 0.2317,  0.4614,  0.1319, -0.0143],
        #
        #         [ 0.1642,  0.3453,  0.0040,  0.0160],
        #         [ 0.2786,  0.3371,  0.1383, -0.0887],
        #         [ 0.3418,  0.3324,  0.2104, -0.1396]], grad_fn=<AddmmBackward>)
        logit = self.fc(lstm_out)

        return logit, hidden

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        hidden = (weight.new(self.n_layers, batch_size, self.hidden_dim).zero_().to(self.device),
                  weight.new(self.n_layers, batch_size, self.hidden_dim).zero_().to(self.device))
        return hidden
