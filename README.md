# API-Fuzzing

## 安装

```bash
sudo apt update
sudo apt install nodejs npm
npm install esprima@4.0.1 escodegen@2.0.0 estraverse@5.2.0 uglify-es@3.3.9
git clone https://github.com/ty5491003/API-Fuzzing.git
cd API-Fuzzing
pip install -r requirements.txt
```



## 使用

在 `API-Fuzzing/CodeGenerator/conf.py` 中配置各种超参数和部分工具的路径；

```bash
# 1.进入主目录并设置PYTHONPATH环境变量
cd API-Fuzzing
export PYTHONPATH=".:$PYTHONPATH"

# 2.训练生成模型（需提前准备好训练数据）
python CodeGenerator/train.py --workspace=12_18_test --save_every_epoch=10 --batch_size=32 --embedding_size=32 --data_number=10000 --max_length=2000 --gpu=0 --epoch=50 --n_layers=2 --data_path=../../data/top2000FinalCorpus.db

# 3.开始Fuzzing（需提前准备好种子文件）
python Fuzzer/run.py --gpu=0 --gen_model=CodeGenerator/workspace/12_18_test/model_50.ckpt
```



## 可疑用例分析系统

为了提高分析可疑用例的效率专门开发的一个Web系统，源码地址：https://github.com/ty5491003/bug-parser



## Bug List

#### Bug汇总PPT

【腾讯文档】API-Fuzzing-Bug汇总
https://docs.qq.com/slide/DTGx5UUlyaU95R1hv

#### ChakraCore

| No.  |   Version   |                             Link                             |                Contributor                |    State    |   Description    |
| :--: | :---------: | :----------------------------------------------------------: | :---------------------------------------: | :---------: | :--------------: |
|  1   |  v1.11.12   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6546) | [Yang Tian](https://github.com/ty5491003) | 复现&未修复 | 重声明变量未报错 |
|  2   | v1.11.12/24 | [#issue](https://github.com/chakra-core/ChakraCore/issues/6550) | [Yang Tian](https://github.com/ty5491003) | 复现&已修复 |   this++未报错   |
|  3   |  V1.11.24   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6553) | [Yang Tian](https://github.com/ty5491003) | 复现&未修复 |   if(1)未报错    |
|  6   |   9e2f198   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6567) |   [Wen Yi](https://github.com/YiWen-y)    | **新发现&已修复** | 重定义TypeError异常 |
|  7   |   9e2f198   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6569) |   [Wen Yi](https://github.com/YiWen-y)    | 复现&未修复 |RegExp.prototype.toString实现错误|
| 9 | 1_11_latest | [#issue](https://github.com/microsoft/ChakraCore/issues/6503) | [Yang Tian](https://github.com/ty5491003) | 复现&未修复 |%TypedArray%.prototype.sort实现错误|
| 14 | 1_11_latest | None | [Wen Yi](https://github.com/YiWen-y) | 复现&未修复 |Proxy对象拦截defineProperty实现错误|
| 16 | 1_11_latest | None | [Wen Yi](https://github.com/YiWen-y) | 复现&未修复 |RegExp.prototype[Symbol.match]与String.prototype.match不关联|
| 17 | 1_11_latest | [#issue](https://github.com/chakra-core/ChakraCore/issues/6582) | [Wen Yi](https://github.com/YiWen-y) | **新发现&已修复** |调用Array.prototype.push时不使用自定义的set方法|
| 20 | 1_11_latest | [#issue](https://github.com/chakra-core/ChakraCore/issues/6589) | [Wen Yi](https://github.com/YiWen-y) | 引擎特性 |原型链与对象不匹配未报错|
| 21 | 1_11_latest | [#issue](https://github.com/chakra-core/ChakraCore/issues/6590) | [Wen Yi](https://github.com/YiWen-y) | 新发现&未修复 |const声明常量后可修改|
| 24 | V1.11.19 | [#issue](https://github.com/chakra-core/ChakraCore/issues/6503) | [Haobin-Lee](https://github.com/Haobin-Lee) | 复现&已修复 |%Typed%|

#### JavaScriptCore

| No.  |                           Version                            |                           Link                            |                Contributor                |  State   |   Description    |
| :--: | :----------------------------------------------------------: | :-------------------------------------------------------: | :---------------------------------------: | :------: | :--------------: |
|  4   | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220142) | [Yang Tian](https://github.com/ty5491003) | 复现&未修复 | 重声明变量未报错 |
| 8 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | None | [Yang Tian](https://github.com/ty5491003) | 复现&已修复 | 对freezed对象修改length未报错 |
| 10 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | None | [Yang Tian](https://github.com/ty5491003) | 复现&已修复 | 同5（需要在JSC新版本验证） |
| 11 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220506) | [Wen Yi](https://github.com/YiWen-y) | 复现&已修复 | for...of...语法错误未报错 |
| 12 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220574) | [Wen Yi](https://github.com/YiWen-y) | 待确认 | 已有属性重赋值不调用set方法 |
| 13 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220507) | [Wen Yi](https://github.com/YiWen-y) | 复现&已修复 | %TypedArray%.prototype.sort实现错误 |
| 15 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | None | [Wen Yi](https://github.com/YiWen-y) | 复现&未修复 | Proxy对象拦截defineProperty实现错误 |
| 18 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220842) | [Wen Yi](https://github.com/YiWen-y) | 复现&未修复 | x与this.x指向不同 |
| 22 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=221177) | [Wen Yi](https://github.com/YiWen-y) | **新发现&未修复** | Array.prototype.push实现异常 |
| 23 | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=221176) | [Jinqiu Wang](https://github.com/qiudaoyuyesok) | 复现&未修复 | 重定义属性时未更新属性 |

#### V8

| No.  | Version |                             Link                             |             Contributor              | State  |            Description             |
| :--: | :-----: | :----------------------------------------------------------: | :----------------------------------: | :----: | :--------------------------------: |
|  5   | d891c59 | [#report](https://bugs.chromium.org/p/v8/issues/detail?id=11294) | [Wen Yi](https://github.com/YiWen-y) | 待确认 | %TypedArray%.prototype.set实现错误 |
|  19  | e39c701 | [#report](https://bugs.chromium.org/p/v8/issues/detail?id=11359) | [Wen Yi](https://github.com/YiWen-y) | 待确认 |            new实现异常             |

