# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: result.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/18
# @Description: 
# @Input:
# @Output:
#

import sys
import time
import pathlib
import subprocess
import tempfile

from Fuzzer.testcase import Testcase, FilteredTestcase


class Output:
    def __init__(self,
                 id_db: int,
                 testbed: str,
                 returncode: int,
                 stdout: str,
                 stderr: str,
                 duration_ms: int):
        self.id = id_db
        self.testbed = testbed
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.engine_name = self.get_engine_name_from_testbed()
        self.output_class = self.get_output_class()

    def get_output_class(self) -> str:
        """
        对该Output实例按照returncode进行一个分类，主要的类别有：
        (1)timeout: returncode为-9，说明用例执行时间超时，被系统kill
        (2)crash: returncode<0且不为-9，认定为crash
        (3)runtime_error: 用例执行错误，通常是指5类运行时异常
        (4)pass: 用例正常执行
        注意：chakraCore无论测试用例是否有语法错误，returncode都等于0，所以需要结合stderr进行特殊判断

        Returns:
            上述四种类型之一
        """
        if self.returncode == -9:
            return "timeout"

        # 若returncode为负，且不为-9，则判断为crash
        if self.returncode < 0:
            return "crash"

        # 接下来是returncode>=0的情况，先针对chakra这个特例来进行判断：
        if 'chakra' in self.engine_name:
            if self.stderr != '':
                return 'runtime_error'
            else:
                return 'pass'

        # 对其余三个引擎进行判断
        if self.returncode == 0:
            return 'pass'
        else:
            return 'runtime_error'

    def get_engine_name_from_testbed(self):
        """
        注意控制引擎名称，必须是 chakra/spidermonkey/jsc/v8，后续会有根据这个名称来判断的情况
        """
        if 'engines' in self.testbed:
            return self.testbed.split('engines')[1].split('/')[1]
        elif 'jsvu' in self.testbed:
            temp_name = self.testbed.split('jsvu')[1].split('/')[1]
            if 'ch' in temp_name:
                return 'chakra'
            elif 'sm' in temp_name:
                return 'spidermonkey'
            else:
                return temp_name  # jsc和v8可以直接返回

    def get_state_code(self) -> str:
        """
        获取一次引擎执行的Output的状态，总共有9类：
        1：正常执行——pass；
        2：超时——timeout；
        3：运行时异常——SyntaxError
        4：运行时异常——RangeError
        5：运行时异常——ReferenceError
        6：运行时异常——TypeError
        7：运行时异常——URIError
        8：可能存在的其他类型的异常
        9：崩溃——crash

        Returns: 字符串数字表示的状态，比如 '1' 或者 '3'
        """
        # 对runtime_error做更细化的判断
        if self.output_class == 'runtime_error':

            # 提取到error_info（因为不同引擎的error_info是由不同位置输出的）
            if self.engine_name.lower() == 'chakra' or self.engine_name.lower() == 'spidermonkey':
                error_info = self.stderr
            else:
                error_info = self.stdout

            # 在error_info中找关键词来判断具体类型
            errortype_index_dict = {}
            errortype_index_dict['SyntaxError'] = error_info.find('SyntaxError')
            errortype_index_dict['RangeError'] = error_info.find('RangeError')
            errortype_index_dict['ReferenceError'] = error_info.find('ReferenceError')
            errortype_index_dict['TypeError'] = error_info.find('TypeError')
            errortype_index_dict['URIError'] = error_info.find('URIError')

            # 判断是否全是其他异常，返回8
            temp = set(errortype_index_dict.values())
            if len(temp) == 1 and temp.pop() == -1:
                return '8'

            # 判断其他几类
            temp = [i for i in temp if i != -1]
            first_index = min(temp)
            error_type = None

            for type, index in errortype_index_dict.items():
                if index == first_index:
                    error_type = type
                    break

            if error_type == 'SyntaxError':
                return '3'
            elif error_type == 'RangeError':
                return '4'
            elif error_type == 'ReferenceError':
                return '5'
            elif error_type == 'TypeError':
                return '6'
            elif error_type == 'URIError':
                return '7'
            else:
                return '8'

        # 其他三类直接判断
        else:
            type_map = {'pass': '1', 'timeout': '2', 'crash': '9'}
            return type_map[self.output_class]

    def serialize(self):
        return {"id": self.id,
                "testbed": self.testbed,
                "returncode": self.returncode,
                "stdout": self.stdout,
                "stderr": self.stderr,
                "duration_ms": self.duration_ms,
                "output_class": self.output_class,
                "engine_name": self.engine_name}

    def serialize_simple(self):
        return {"engine_name": self.engine_name,
                "returncode": self.returncode,
                "stdout": self.stdout,
                "stderr": self.stderr,
                "duration_ms": self.duration_ms,
                "output_class": self.output_class}


class Result:
    """
    这个是差分测试是的result类型，区别于ResultClass，ResultClass是运行时候保存执行结果的类型
    """

    def __init__(self, testcase: str):
        self.testcase = testcase
        self.outputs = []

    def add_output(self, output: Output):
        self.outputs.append(output)

    def write2file(self):
        pass

    def serialize(self):
        return {"testcase": self.testcase, "outputs": [e.serialize_simple() for e in self.outputs]}

    def is_suspicious(self) -> bool:
        """
        判断当前result实例是否可疑，即判断是否有执行不一致的用例；
        根据每个output中的output_class来判断
        注意：
        需要对v8引擎的特殊情况进行处理
        v8引擎对于未执行的语句不会抛出任何异常，所以大概率会出现v8报pass而其余引擎报runtime_error的情况，引起误报

        Returns:
            布尔值，表示是否是可疑用例：假如是，返回True；不是则返回False
        """
        engine_class_pair = {}
        for output in self.outputs:
            engine_class_pair[output.engine_name.lower()] = output.output_class

        # 遇到v8为pass，其余引擎为runtime_error的情况，直接返回False，认为是不可疑的
        pass_count = 0
        runtime_error = 0
        for output_class in engine_class_pair.values():
            if output_class == 'pass':
                pass_count += 1
            if output_class == 'runtime_error':
                runtime_error += 1
        if runtime_error == len(engine_class_pair) - 1 and engine_class_pair.get('v8') == 'pass':
            return False

        return len(set(engine_class_pair.values())) != 1

    def is_all_pass(self) -> bool:
        """
        判断当前result中所有引擎执行结果是否全部是'pass'
        Returns:
            布尔值，表示是否全部通过：假如是，返回True；不是则返回False
        """
        class_result = set([output.output_class for output in self.outputs])
        return len(class_result) == 1 and class_result.pop() == 'pass'

    @staticmethod
    def compare_results(old_result, new_result) -> bool:
        """
        比较新用例和种子用例的result是否发生变化

        Args:
            old_result (Result): 种子用例的result
            new_result (Result): 新用例的result

        Returns:
            布尔值，表示是否发生变化：假如变化了返回True，没变化返回False
        """
        # 抽取出新旧两个 {engine_name: output_class} 的信息
        old_dict = {output.engine_name: output.output_class for output in old_result.outputs}
        new_dict = {output.engine_name: output.output_class for output in new_result.outputs}

        # 假如引擎对应的类别发生了改变，那么结果一定是变化了
        if old_dict != new_dict:
            return True

        # TODO：引擎对应的类别没有改变，则需要再判断其内容
        else:
            return False

    @staticmethod
    def is_syntax_correct(testcase, uglifyjs_path):
        """
        使用uglifyjs工具执行用例语法正确性的检查
        Args:
            testcase (str): 测试用例代码
            uglifyjs_path (str): uglifyjs二进制文件的路径，默认为'uglifyjs'

        Returns:
            bool：语法检查通过则返回True，不通过返回False
        """
        with tempfile.NamedTemporaryFile(prefix="syntax_check_tempfile_", delete=True) as f:
            p = pathlib.Path(f.name)
            p.write_text(testcase, encoding='utf-8')

            cmd = [uglifyjs_path, p, '-b']

            if 'win' in sys.platform:
                p = subprocess.run(cmd, shell=True,
                                   stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True,
                                   encoding='utf-8')
            else:
                p = subprocess.run(cmd,
                                   stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True,
                                   encoding='utf-8')

        return p.returncode == 0

    @staticmethod
    def is_semantic_correct(result):
        """
        对新生成用例的Fuzzing结果中的语义正确的情况进行判断
        语义正确：只要超过一半的引擎执行结果是'pass'，则认为该用例是语义正确的
        Args:
            result (Result): 新生成用例的Fuzzing结果

        Returns:
            bool，语义正确返回True；语义错误返回False
        """
        # 读取每个引擎的执行结果的类别
        class_result = [output.output_class for output in result.outputs]
        return class_result.count('pass') > (len(class_result) / 2)

    @staticmethod
    def result_map_to_testcase(result, timeout, parent_id):
        """
        将Result对象实例转化为对应的Testcase类的对象实例
        Args:
            result ():
            timeout ():
            parent_id ():

        Returns:

        """
        # 主要是从result中提取出状态码
        state_code = ''
        for output in result.outputs:
            state_code += output.get_state_code()

        return Testcase(state_code=state_code,
                        testcase=result.testcase,
                        timeout=timeout,
                        parent_id=parent_id,
                        date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    @staticmethod
    def testcase_transform_to_filtered_testcase(testcase):
        return FilteredTestcase(state_code=testcase.state_code,
                                testcase=testcase.testcase,
                                timeout=testcase.timeout,
                                parent_id=testcase.parent_id,
                                date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                remark=testcase.remark)