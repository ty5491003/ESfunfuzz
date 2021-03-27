# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: chakra_testsuite_process.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/22
# @Description: 
# @Input:
# @Output:
#
import os
import re

from uuid import uuid4
from tqdm import tqdm

from Fuzzer.ast_op import js_compile
from Fuzzer.utils import get_file_abspath_list_from_dir, read_file, write_file
from Fuzzer.fuzzer import Fuzzer

engines = [
    "/export/nisl/yhy/javascriptFuzzingOther/engines/chakra/version_9e2f198_12_26_latest/out/Release/ch"
    , "/export/nisl/yhy/javascriptFuzzingOther/engines/spiderMonkey/gecko-dev-201255a/js/src/build_OPT.OBJ/dist/bin/js"
    , "/export/nisl/yhy/javascriptFuzzingOther/engines/javascriptCore/webkit-d940b47/webkit/WebKitBuild/Release/bin/jsc"
    , "/export/nisl/yhy/javascriptFuzzingOther/engines/v8/version-e39c701/release/d8"
]
timeout = 15


if __name__ == '__main__':
    # 读取所有JS文件
    source_dir = '/export/nisl/ty/data/ChakraCore-master/test'
    js_file_list = get_file_abspath_list_from_dir(source_dir, True, 'js')
    total_count = len(js_file_list)
    pass_count = 0
    remove_comment_error_count = 0
    no_pass_list = []

    target_dir = 'SeedPreprocess/chakra_seeds'
    os.makedirs(target_dir)

    fuzzer = Fuzzer(engines, timeout)

    for file in tqdm(js_file_list):
        try:
            code_str = read_file(file)
            # step1.消除个性化的地方，比如处理WScript.Echo
            code_str = code_str.replace('WScript.Echo', 'print')
        except:
            no_pass_list.append(file)
            continue

        # step2.通用性过滤
        fuzzing_result = fuzzer.run_testcase_multi_threads(code_str)

        # 假如通过，则写入到target_dir中
        if fuzzing_result.is_all_pass():
            id = str(uuid4()).replace('-', '')[:16]
            file_name = os.path.join(target_dir, f'original_{id}.js')

            # step3.基于AST做移除注释和语法过滤
            try:
                code_str = js_compile.call('remove_comment', code_str)
            except:
                remove_comment_error_count += 1
                continue
            # step4.统一空格形式后去重，并按长度进行过滤
            code_str = re.sub(' +', ' ', code_str.strip().replace('\n', ' ').replace('\t', ' '))
            if 0 < len(code_str) < 100000:
                continue

            # 写入文件
            write_file(file_name, code_str)
            pass_count += 1

        else:
            no_pass_list.append(file)

    print(f'总共有{total_count}个js文件，其中有{pass_count}个通过，有{remove_comment_error_count}个移除注释失败')

    # 将未通过的保存下
    with open('SeedPreprocess/no_pass_file_after_replace_echo.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(no_pass_list))
