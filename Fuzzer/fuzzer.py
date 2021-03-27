# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: fuzzer.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/18
# @Description: 
# @Input:
# @Output:
#


import tempfile
import logging
import pathlib
import subprocess
import gc
import traceback
import sys

from time import time
from threading import Thread

from Fuzzer.result import Result, Output


class Fuzzer:
    def __init__(self, engines, timeout):
        self.engines = engines
        self.timeout = timeout
        self.check_engine_exist()

    @staticmethod
    def run_test_case(testbed: str, testcase: pathlib.Path, timeout, index=0):
        cmd = ["timeout", "-s9", str(timeout), testbed, testcase]

        start_time = time()
        pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = pro.communicate()
        end_time = time()
        duration_ms = int(round((end_time - start_time) * 1000))

        return Output(
            id_db=index,
            testbed=testbed,
            returncode=pro.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms)

    def check_engine_exist(self):
        """
        检查配置文件中指定的所有引擎是否都存在且可以正常运行
        Raises:
            LookupError: 提示有问题的引擎
        """
        with tempfile.NamedTemporaryFile(prefix="jerryTescase_", delete=True) as f:
            p = pathlib.Path(f.name)
            p.write_text("var a = 1;", encoding='utf-8')

            for engine in self.engines:
                result = self.run_test_case(testbed=engine, testcase=p, timeout=self.timeout)
                if not result.returncode == 0:
                    raise LookupError(f"Enigine ERROR: {engine}\n")

    def run_testcase_multi_threads(self, testcase: str):
        result = Result(testcase=testcase)

        with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_",
                                         suffix=".js",
                                         delete=True) as f:
            testcase_path = pathlib.Path(f.name)
            testcase_path.write_text(testcase, encoding='utf-8')

            counter = -1
            threads_pool = []

            for engine in self.engines:
                counter += 1
                tmp = ThreadLock(engine, testcase_path, counter, self.timeout)
                threads_pool.append(tmp)
                tmp.start()
            index = 0
            for thread in threads_pool:
                index -= 1
                thread.join()
                if thread.returncode:
                    gc.collect()
                elif thread.output is not None:
                    thread.output.id = index
                    result.add_output(thread.output)
        return result


class ThreadLock(Thread):
    def __init__(self, engine, testcase_path, counter, timeout):
        super().__init__()
        self.output = None
        self.engine = engine
        self.testcase_path = testcase_path
        self.counter = counter
        self.returncode = None
        self.timeout = timeout

    def run(self):
        try:
            self.output = Fuzzer.run_test_case(
                self.engine, self.testcase_path, timeout=self.timeout, index=self.counter)
        except Exception:
            self.returncode = 1
            logging.exception(traceback.format_exception(*sys.exc_info()))
            return
