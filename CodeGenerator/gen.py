# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: gen.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/11/27
# @Description: 
# @Input:
# @Output:
#


import os
import torch
from tqdm import trange


from CodeGenerator.conf import hparams
from CodeGenerator.model import LSTM
from CodeGenerator.utils import load_json, cut
from CodeGenerator.sample import sample_multi


device = torch.device(f"cuda:{hparams.gpu}" if torch.cuda.is_available() else "cpu")


if __name__ == '__main__':
    # 读取工作路径和训练词汇表
    print("正在恢复词汇表和模型，请稍等...")
    workspace_path = os.path.dirname(hparams.gen_model)
    token_to_idx = load_json(os.path.join(workspace_path, 'token_to_idx.json'))
    idx_to_token = load_json(os.path.join(workspace_path, 'idx_to_token.json'), transfer=True)

    # 恢复模型（注意load方法没有device参数）
    model = torch.load(hparams.gen_model).to(device)
    model.device = device

    # 批量生成
    import time
    start_time = time.time()
    print("开始生成: ")
    with open(os.path.join(workspace_path, hparams.gen_file), 'a+', encoding='utf-8') as f:

        n_batches = int(hparams.gen_number / hparams.gen_batch_size)

        for _ in trange(n_batches):
            gen_code_list = sample_multi(model,
                                         prefix=hparams.prefix,
                                         batch_size=hparams.gen_batch_size,
                                         max_gen_length=hparams.max_gen_length,
                                         token_to_idx=token_to_idx,
                                         idx_to_token=idx_to_token,
                                         segment_length=hparams.segment_length,
                                         temperature=hparams.temperature)
            gen_code_list = [cut(code) for code in gen_code_list]

            f.write('\n'.join(gen_code_list) + '\n')

    print(f'生成{hparams.gen_number}条用例总共花费{int(time.time() - start_time)}秒')

