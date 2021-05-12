# ESfunfuzz：JS引擎的一致性缺陷检测系统

## 安装

**注意：ESfunfuzz需要一台安装了 Docker 的 Ubuntu18.04 服务器，并要求内存不小于16G。**

---

**Step1.下载镜像压缩文件**

为了便于使用，ESfunfuzz的源代码以及所需的所有相关环境依赖已配置在了Docker容器中。你首先需要下载此镜像压缩文件（即 `ty_esfunfuzz_3.0.tar.gz`），并上传到你的服务器。

---

**Step2.将压缩文件恢复成镜像**

进入你的服务器中该文件的同级目录中，执行以下命令恢复镜像：

```bash
gunzip -c ty_esfunfuzz_3.0.tar.gz | docker load
```

---

**Step3.为Docker添加GPU支持（可选）**

ESfunfuzz可以通过调用GPU来加速程序执行，但你必须先为Docker添加GPU支持。配置方法请参考[此处](https://github.com/NWU-NISL-Fuzzing/COMFORT/tree/main/artifact_evaluation#p1---preliminary-configure-the-gpu-running-environment-on-the-host-machine-optional-)。如果这对你来说很困难，你**可以选择跳过此步骤**。

> 注意：NISL的26/87/113服务器已经添加了GPU支持，可跳过此步骤；

---

**Step4.启动该镜像对应的容器**

启动支持GPU的容器（要求必须执行了Step3）：

```bash
docker run -it --name ESfunfuzz -p 3821:3821 --gpus all ty_esfunfuzz:2.0 
```

或者，启动CPU的容器（通用）：

```bash
docker run -it --name ESfunfuzz -p 3821:3821 ty_esfunfuzz:2.0
```

---

**Step5.进入容器**

```bash
docker attach ESfunfuzz
```

进入该容器后即可开始使用。



## 使用

按照以下说明即可开始使用ESfunfuzz。注意：ESfunfuzz会自动判断是否启用GPU支持，所以GPU版本与CPU版本的运行命令完全一致。

---

**ES标准解析（可选）**

执行以下命令以进行ES标准的解析过程，即从标准中提取出有效的语义信息并写入文件。

```bash
cd /root/ESfunfuzz/CaseMutator/StandardParser/src/main
node parsing.js
```

---

**模型训练（可选）**

```bash
cd ~/ESfunfuzz
python CodeGenerator/train.py --workspace=test --save_every_epoch=10 --batch_size=32 --embedding_size=32 --gpu=0 --epoch=50 --n_layers=2 --data_path=/root/ESfunfuzz/Data/after07.db
```

训练过程可以调整更多参数，详情参考 `/root/ESfunfuzz/CodeGenerator/conf.py` 配置文件。开始后可以通过按 `Ctrl+c` 提前终止。 

---

**执行生成式Fuzzing**

```bash
cd ~/ESfunfuzz
python Fuzzer/run.py
```

生成式Fuzzing过程可以调整更多参数，详情参考 `/root/ESfunfuzz/CodeGenerator/conf.py` 配置文件。 执行结果实例如下，可以通过按 `Ctrl+c` 提前终止。

```txt
正在进行运行环境验证，请稍等...
[1]node以及npm包安装正确.
[2]数据库连接正确.
[3]待测引擎配置正确.
所有环境检查无误，即将开始Fuzzing.
正在恢复词汇表和模型，请稍等...
词汇表和模型已恢复，开始Fuzzing.
----------------------------------------
Fuzzing已持续:                 00时00分02秒
已Fuzzing种子用例:              1
已Fuzzing新生成用例:            3
新生成用例中语法正确的用例及占比:  2(66.67%)
新生成的种子用例数量:            0
被过滤的用例数量:               0
Fuzzing的速度为:               1.50个/秒
----------------------------------------
Fuzzing已持续:                 00时01分36秒
已Fuzzing种子用例:              30
已Fuzzing新生成用例:            110
新生成用例中语法正确的用例及占比:  73(66.36%)
新生成的种子用例数量:            0
被过滤的用例数量:               6
Fuzzing的速度为:               1.15个/秒
----------------------------------------
...
```

---

**执行突变式Fuzzing**

```bash
cd ~/ESfunfuzz
python Fuzzer/run_with_mutate.py
```

 执行结果与上述类似，可以通过按 `Ctrl+c` 提前终止。

---

**启动Jupyter Notebook（可选）**

```bash
jupyter notebook --port=3821 --notebook-dir=~/ESfunfuzz
```

启动后，可以使用浏览器访问 `本机ip:3821` 访问部署好的Jupyter演示笔记，比如 `10.15.0.88:3821` （注意ip需要换成你本机的），访问密码为 `nisl8830` ；



## 项目结构

此处对项目整体组织结构进行描述（仅目录和极个别重要文件）

```txt
.
├── CaseMutator：用例突变模块
│   ├── APIs：ES标准解析模块需要的文件
│   ├── StandardParser：ES标准解析模块
├── CodeGenerator：代码生成模块
│   ├── train.py：生成模型训练程序入口
├── Data：相关数据 
├── Evaluation：评估模块
│   ├── Chapter_5_3_2：论文章节5.3.2的数据及评估
│   ├── Chapter_5_4_1
│   ├── Chapter_5_4_2
│   └── Chapter_5_5
├── Fuzzer：模糊测试模块
│   ├── run.py：生成式Fuzzing程序入口
│   ├── run_with_mutate.py：突变式Fuzzing程序入口
├── Images：图片
├── Preprocess：数据预处理模块
│   ├── CorpusPreprocess：模型训练数据预处理
│   └── SeedPreprocess：种子数据预处理
├── README.md：项目说明文件
├── main.ipynb：Jupyter Notebook演示入口文件
├── requirements.txt：Python第三方库依赖
```





## 缺陷列表

#### Bug汇总PPT

缺陷结果汇总，在线PPT：https://docs.qq.com/slide/DTGx5UUlyaU95R1hv

#### ChakraCore

| No.  |   Version   |                             Link                             |                 Contributor                 |       State       |                         Description                          |
| :--: | :---------: | :----------------------------------------------------------: | :-----------------------------------------: | :---------------: | :----------------------------------------------------------: |
|  1   |  v1.11.12   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6546) |  [Yang Tian](https://github.com/ty5491003)  |    复现&未修复    |                       重声明变量未报错                       |
|  2   | v1.11.12/24 | [#issue](https://github.com/chakra-core/ChakraCore/issues/6550) |  [Yang Tian](https://github.com/ty5491003)  |    复现&已修复    |                         this++未报错                         |
|  3   |  V1.11.24   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6553) |  [Yang Tian](https://github.com/ty5491003)  |    复现&未修复    |                         if(1)未报错                          |
|  6   |   9e2f198   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6567) |    [Wen Yi](https://github.com/YiWen-y)     | **新发现&已修复** |                     重定义TypeError异常                      |
|  7   |   9e2f198   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6569) |    [Wen Yi](https://github.com/YiWen-y)     |    复现&未修复    |              RegExp.prototype.toString实现错误               |
|  9   | 1_11_latest | [#issue](https://github.com/microsoft/ChakraCore/issues/6503) |  [Yang Tian](https://github.com/ty5491003)  |    复现&未修复    |             %TypedArray%.prototype.sort实现错误              |
|  14  | 1_11_latest |                             None                             |    [Wen Yi](https://github.com/YiWen-y)     |    复现&未修复    |             Proxy对象拦截defineProperty实现错误              |
|  16  | 1_11_latest |                             None                             |    [Wen Yi](https://github.com/YiWen-y)     |    复现&未修复    | RegExp.prototype[Symbol.match]与String.prototype.match不关联 |
|  17  | 1_11_latest | [#issue](https://github.com/chakra-core/ChakraCore/issues/6582) |    [Wen Yi](https://github.com/YiWen-y)     | **新发现&已修复** |       调用Array.prototype.push时不使用自定义的set方法        |
|  20  | 1_11_latest | [#issue](https://github.com/chakra-core/ChakraCore/issues/6589) |    [Wen Yi](https://github.com/YiWen-y)     |     引擎特性      |                   原型链与对象不匹配未报错                   |
|  21  | 1_11_latest | [#issue](https://github.com/chakra-core/ChakraCore/issues/6590) |    [Wen Yi](https://github.com/YiWen-y)     |   新发现&未修复   |                    const声明常量后可修改                     |
|  24  |  V1.11.19   | [#issue](https://github.com/chakra-core/ChakraCore/issues/6503) | [Haobin-Lee](https://github.com/Haobin-Lee) |    复现&已修复    |                           %Typed%                            |

#### JavaScriptCore

| No.  |                           Version                            |                           Link                            |                   Contributor                   |       State       |             Description             |
| :--: | :----------------------------------------------------------: | :-------------------------------------------------------: | :---------------------------------------------: | :---------------: | :---------------------------------: |
|  4   | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220142) |    [Yang Tian](https://github.com/ty5491003)    |    复现&未修复    |          重声明变量未报错           |
|  8   | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) |                           None                            |    [Yang Tian](https://github.com/ty5491003)    |    复现&已修复    |    对freezed对象修改length未报错    |
|  10  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) |                           None                            |    [Yang Tian](https://github.com/ty5491003)    |    复现&已修复    |     同5（需要在JSC新版本验证）      |
|  11  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220506) |      [Wen Yi](https://github.com/YiWen-y)       |    复现&已修复    |      for...of...语法错误未报错      |
|  12  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220574) |      [Wen Yi](https://github.com/YiWen-y)       |      待确认       |     已有属性重赋值不调用set方法     |
|  13  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220507) |      [Wen Yi](https://github.com/YiWen-y)       |    复现&已修复    | %TypedArray%.prototype.sort实现错误 |
|  15  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) |                           None                            |      [Wen Yi](https://github.com/YiWen-y)       |    复现&未修复    | Proxy对象拦截defineProperty实现错误 |
|  18  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=220842) |      [Wen Yi](https://github.com/YiWen-y)       |    复现&未修复    |          x与this.x指向不同          |
|  22  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=221177) |      [Wen Yi](https://github.com/YiWen-y)       | **新发现&未修复** |    Array.prototype.push实现异常     |
|  23  | [d940b47](https://github.com/WebKit/WebKit-http/commit/d940b477848884f63752d25491d9dd0b9d3ccb2d) | [#report](https://bugs.webkit.org/show_bug.cgi?id=221176) | [Jinqiu Wang](https://github.com/qiudaoyuyesok) |    复现&未修复    |       重定义属性时未更新属性        |

#### V8

| No.  | Version |                             Link                             |             Contributor              | State  |            Description             |
| :--: | :-----: | :----------------------------------------------------------: | :----------------------------------: | :----: | :--------------------------------: |
|  5   | d891c59 | [#report](https://bugs.chromium.org/p/v8/issues/detail?id=11294) | [Wen Yi](https://github.com/YiWen-y) | 待确认 | %TypedArray%.prototype.set实现错误 |
|  19  | e39c701 | [#report](https://bugs.chromium.org/p/v8/issues/detail?id=11359) | [Wen Yi](https://github.com/YiWen-y) | 待确认 |            new实现异常             |



## 可疑用例分析系统

为了提高分析可疑用例的效率专门开发的一个Web系统，源码地址：https://github.com/ty5491003/bug-parser