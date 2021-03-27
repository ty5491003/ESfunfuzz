# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: ast_op.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/31
# @Description: 
# @Input:
# @Output:
#

import execjs


js_compile = execjs.compile("""
    const esprima = require('esprima');
    const escodegen = require('escodegen');
    const estraverse = require('estraverse');
    const uglifyjs = require('uglify-es');
    
    function remove_comment(code_str) {
        let ast = esprima.parseScript(code_str);
        let new_code = escodegen.generate(ast);
        return new_code;
    }
    
    function tokenize(code) {
        return esprima.tokenize(code)
    }
    
    function get_mutation_points(code_str) {
        let points = [];
        let ast = esprima.parseScript(code_str, { loc: true });
        estraverse.traverse(ast, {
            enter(node, parent) {
                // example: var a = 1;
                if (node.type === "VariableDeclaration") {
                    points.push(node.loc['end']['column']);
    
                // example: var a = ''.split(' ');
                } else if (node.type == "MemberExpression" && node['property'] != null && node['property'].type == "Identifier") {
                    points.push(node.loc['end']['column'] + 1);
    
                // example: test();
                // } else if (parent != null && parent.type == "CallExpression" && node.type == "Identifier") {
                //    points.push(node.loc['end']['column']);
                }
            }
        });
        return points;
    }

    """)


if __name__ == '__main__':
    # 测试
    import re
    code_str = """
        var c = '';
        function test() {
            var b = '123';
            c = b.split('');
        }
    """
    code_str = re.sub(' +', ' ', code_str.strip().replace('\n', ' ').replace('\t', ' '))
    print(code_str)
    print()
    points = js_compile.call('get_mutation_points', code_str)
    for point in points:
        print(code_str[:point])
