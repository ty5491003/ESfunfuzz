import os
import json

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

plt.rc('font',family='Times New Roman')


def to_percent(temp, position):
    return '%1.0f' % (temp) + '%'


def drawBars(coverages, fuzzer_names):

    plt.rc('font', family='SimHei', size=12)  # 设置中文显示，否则出现乱码！

    # 初始
    arguments = ["通过率", "行覆盖率", "方法覆盖率", "分支覆盖率"]
    fc = ['k', 'gainsboro', 'gainsboro', 'darkgray', 'gainsboro']
    hatch = ['', '//', 'x', '\\\\', '.']

    # 我的修改
    # arguments = ["Passing Rate", "Statement Cov", "Function Cov", "Branch Cov"]
    # fc = ['k', 'dimgray', 'grey', 'darkgray', 'lightgray', 'gainsboro']
    # hatch = ['v', 'xxx', '\\\\\\', '///', 'v', '^']
    x = list(range(len(arguments)))
    total_width, n = 0.8, 6
    width = total_width / n

    # 设置主次刻度间隔
    ymajorLocator = MultipleLocator(20)
    yminorLocator = MultipleLocator(10)

    # 设置y轴刻度值
    plt.yticks([0, 20, 40, 60, 80, 100])
    plt.ylim(0, 100)
    # 设置主次刻度线
    plt.grid(which="major", axis="y", linestyle="-")
    plt.grid(which="minor", axis="y", linestyle="--")
    # 显示主次刻度
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.gca().yaxis.set_major_locator(ymajorLocator)
    plt.gca().yaxis.set_minor_locator(yminorLocator)

    plt.xlabel("不同的评估标准")
    plt.ylabel("百分比")

    # 显示柱状图
    for i in range(len(coverages)):
        if i == len(coverages) - 3:
            # zorder越大，表示柱子越靠后，不会被虚线覆盖
            plt.bar(x, coverages[i], width=width, label=fuzzer_names[i], tick_label=arguments, fc=fc[i], zorder=2, hatch=hatch[i])
        else:
            plt.bar(x, coverages[i], width=width, label=fuzzer_names[i], fc=fc[i], zorder=2, hatch=hatch[i])
        for j in range(len(x)):
            x[j] = x[j] + width

    plt.legend(loc='upper right', fontsize=12, ncol=3)
    plt.style.use('ggplot')
    plt.show()

    # 保存为图片
    # plt.savefig('5.4.1_result.png')


def read_data(result_path) -> dict:
    with open(result_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return json.loads(content)


def extractMetrics(fuzzer, data_dir):
    # 设定覆盖率结果文件目录
    parent_dir = os.path.join(data_dir, f'{fuzzer.lower()}/{fuzzer.lower()}_report/')
    coverage_path = os.path.join(parent_dir, "coverage-summary.json")

    # 读取通过率
    passing_rates = read_data(os.path.join(data_dir, 'passing_rate.json'))
    with open(coverage_path, "r", encoding="utf-8") as f:
        content = f.read()
    coverage_message = json.loads(content)

    # 返回数据
    passing_rate = passing_rates[fuzzer]
    statement_cov = coverage_message['total']["statements"]['pct']
    function_cov = coverage_message['total']["functions"]['pct']
    branch_cov = coverage_message['total']["branches"]['pct']
    return [passing_rate, statement_cov, function_cov, branch_cov]


def plot(data_dir='Evaluation/Chapter_5_4_1/result'):
    coverages = []
    fuzzers = ["ESfunfuzz", "DIE", "Fuzzilli", "Montage", "CodeAlchemist"]
    for fuzzer in fuzzers:
        coverages.append(extractMetrics(fuzzer, data_dir))
    drawBars(coverages, fuzzers)


if __name__ == '__main__':
    plot('result')
