# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: filter.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/26
# @Description: 
# @Input:
# @Output:
#


class Filter:
    def __init__(self):
        pass

    @staticmethod
    def special_case_filtering(result) -> bool:
        """
        对fuzzing结果的几种特殊情况进行过滤
        Args:
            Result (Fuzzer.Result): Fuzzing结果

        Returns:
            bool，不属于特殊情况则返回True（即本次结果有效，不会被过滤）；否则返回False
        """
        engine_output_pair = {}
        for output in result.outputs:
            engine_output_pair[output.engine_name.lower()] = output

        # 误报1: v8和jsc的version
        if engine_output_pair['v8'].output_class == 'pass' and \
            'version is not defined' in engine_output_pair['spidermonkey'].stderr and \
            "'version' is not defined" in engine_output_pair['chakra'].stderr and \
            engine_output_pair['javascriptcore'].output_class == 'pass':
            return False

        # 误报2: sm的this.options
        if 'TypeError: Cannot read property' in engine_output_pair['v8'].stdout and \
            engine_output_pair['spidermonkey'].output_class == 'pass' and \
            'TypeError: Unable to get property' in engine_output_pair['chakra'].stderr and \
            'Exception: TypeError: undefined is not an object' in engine_output_pair['javascriptcore'].stdout and \
            'this.options' in result.testcase:
            return False

        # 误报3:

        # 误报4: JSC没有console.log
        if engine_output_pair['v8'].output_class == 'pass' and \
            engine_output_pair['spidermonkey'].output_class == 'pass' and \
            engine_output_pair['chakra'].output_class == 'pass' and \
            "Exception: TypeError: undefined is not an object (evaluating 'console.log')" in engine_output_pair['javascriptcore'].stdout:
            return False

        # 误报5: SM的new Promise
        if engine_output_pair['v8'].output_class == 'pass' and \
            'Unhandled rejection:' in engine_output_pair['spidermonkey'].stderr and \
            engine_output_pair['chakra'].output_class == 'pass' and \
            engine_output_pair['javascriptcore'].output_class == 'pass' and \
            'Promise' in result.testcase:
            return False

        # 误报8: JSC 1/$ 不报错
        if 'ReferenceError: $ is not defined' in engine_output_pair['v8'].stdout and \
            'ReferenceError: $ is not defined' in engine_output_pair['spidermonkey'].stderr and \
            "ReferenceError: '$' is not defined" in engine_output_pair['chakra'].stderr and \
            engine_output_pair['javascriptcore'].output_class == 'pass':
            return False

        # 误报9: V8和chakra对语法不报错
        if engine_output_pair['v8'].output_class == 'pass' and \
            'ReferenceError: invalid assignment left-hand side' in engine_output_pair['spidermonkey'].stderr and \
            engine_output_pair['chakra'].output_class == 'pass' and \
            'SyntaxError: Left side of assignmen' in engine_output_pair['javascriptcore'].stdout:
            return False

        # 误报10: 由cut引起的for (;;)
        if result.testcase == 'for (;;) ' or result.testcase == 'while (true) ':
            return False

        # bug1: CC变量重申明不报错
        if 'has already been declared' in engine_output_pair['v8'].stdout and \
            'SyntaxError: redeclaration of function' in engine_output_pair['spidermonkey'].stderr and \
            engine_output_pair['chakra'].output_class == 'pass' and \
            'SyntaxError: Cannot declare a var variable that shadows a let/const/class variable' in engine_output_pair['javascriptcore'].stdout:
            return False

        # bug2: 最新版已修复，不用过滤

        # bug3: CC不正确结束未抛语法错误
        if 'SyntaxError: Unexpected end of input' in engine_output_pair['v8'].stdout and \
            'SyntaxError: expected expression, got end of script' in engine_output_pair['spidermonkey'].stderr and \
            engine_output_pair['chakra'].output_class == 'pass' and \
            'SyntaxError: Unexpected end of script' in engine_output_pair['javascriptcore'].stdout:
            return False

        # bug4: JSC变量重申明不报错
        if 'has already been declared' in engine_output_pair['v8'].stdout and \
            'SyntaxError: redeclaration of function' in engine_output_pair['spidermonkey'].stderr and \
            engine_output_pair['chakra'].output_class == 'pass' and \
            engine_output_pair['javascriptcore'].output_class == 'pass':
            return False

        return True
