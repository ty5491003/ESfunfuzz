import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(
            rect.get_x() +
            rect.get_width() /
            2. -
            0.1,
            1.03 *
            height,
            '%s' %
            int(height))


def extractMetrics(type, result):
    # 对Bug统计情况画图
    ESfunfuzz_number = {"Confirmed Bug": result['ESfunfuzz'][1], "Fixed Bug": result['ESfunfuzz'][0]}
    ESfunfuzz = ESfunfuzz_number[type]
    Fuzzilli_number = {"Confirmed Bug": result['Fuzzilli'][1], "Fixed Bug": result['Fuzzilli'][0]}
    Fuzzilli = Fuzzilli_number[type]
    CodeAlchemist_number = {"Confirmed Bug": result['CodeAlchemist'][1], "Fixed Bug": result['CodeAlchemist'][0]}
    CodeAlchemist = CodeAlchemist_number[type]
    RegExp_Engine_number = {"Confirmed Bug": result['Montage'][1], "Fixed Bug": result['Montage'][0]}
    RegExp_Engine = RegExp_Engine_number[type]
    Strict_Mode_number = {"Confirmed Bug": result['DIE'][1], "Fixed Bug": result['DIE'][0]}
    Strict_Mode = Strict_Mode_number[type]

    return [ESfunfuzz, Fuzzilli, CodeAlchemist, RegExp_Engine, Strict_Mode]


def drawBars(result):
    plt.rc('font', family='SimHei', size=12)  # 设置中文显示，否则出现乱码！

    arguments = ["ESfunfuzz", "Fuzzilli", "CodeAlchemist", "Montage", "DIE"]
    Confirmed = extractMetrics("Confirmed Bug", result)
    Fixed = extractMetrics("Fixed Bug", result)
    types = [Confirmed, Fixed]
    types_names = ["已提交", "已确认"]
    fc = ['k', 'darkgray', 'grey', 'darkgray', 'lightgray', 'gainsboro']

    x = list(range(len(Confirmed)))
    total_width, n = 2, 6
    width = total_width / n

    # 设置主次刻度间隔，及刻度线
    ymajorLocator = MultipleLocator(4)
    yminorLocator = MultipleLocator(2)
    plt.grid(which="major", axis="y", linestyle="-")
    plt.grid(which="minor", axis="y", linestyle="--")

    # 设置y轴刻度值
    plt.yticks([0, 4, 8, 12])
    plt.ylim(0, 12)

    # 显示主次刻度
    plt.gca().yaxis.set_major_locator(ymajorLocator)
    plt.gca().yaxis.set_minor_locator(yminorLocator)

    plt.xticks(rotation=10)
    plt.xlabel('检测工具')
    plt.ylabel('缺陷数量')
    # 显示柱状图
    for i in range(len(types)):
        if i == len(types) - 3:
            # zorder越大，表示柱子越靠后，不会被虚线覆盖
            _a = plt.bar(x, types[i], width=width, label=types_names[i], tick_label=arguments, fc=fc[i], zorder=2)
            autolabel(_a)
        else:
            _b = plt.bar(x, types[i], width=width, label=types_names[i], tick_label=arguments, fc=fc[i], zorder=2)
            autolabel(_b)
        for j in range(len(x)):
            x[j] = x[j] + width

    # 设置图例位于右上角
    plt.legend(loc='upper right', fontsize=12, ncol=1)

    plt.show()
    plt.style.use('ggplot')


def plot():
    result = {'ESfunfuzz': [7, 8],
              'Fuzzilli': [8, 10],
              'CodeAlchemist': [2, 2],
              'Montage': [0, 2],
              'DIE': [5, 6]}
    drawBars(result)


if __name__ == "__main__":
    plot()
