import json
import matplotlib.pyplot as plt


def read_data(result_path='Evaluation/Chapter_5_3_2/evaluate_result.json') -> dict:
    with open(result_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return json.loads(content)


def plot():
    # 读取数据
    data = read_data()

    x = data['Epoch']
    y = data['Char编码']
    y2 = data['BPE编码']
    y3 = data['Word编码']

    plt.figure(figsize=(10, 6))  # 设置画布的尺寸

    # 设置中文字体
    plt.rc('font', family='SimHei', size=15)  # 设置中文显示，否则出现乱码！

    # 设置标题和轴标签
    # plt.title('生成用例通过率随训练次数变化图', fontsize=20)  # 标题，并设定字号大小
    plt.xlabel('模型迭代次数Epoch', fontsize=15)  # 设置x轴，并设定字号大小
    plt.ylabel('通过率（%）', fontsize=15)  # 设置y轴，并设定字号大小

    # color：颜色，linewidth：线宽，linestyle：线条类型，label：图例，marker：数据点的类型
    plt.plot(data['Epoch'], data['Char编码'], color="dimgray", linewidth=2, linestyle='-', label='Char编码', marker='o')
    plt.plot(data['Epoch'], data['Word编码'], color="dimgray", linewidth=1, linestyle='dashed', label='BPE编码', marker='+')
    plt.plot(data['Epoch'], data['BPE编码'], color="dimgray", linewidth=1.5, linestyle='dotted', label='Word编码', marker='*')

    # 加上数值标记
    for x_, y_ in zip(x, y):
        plt.text(x_, y_, y_, ha='left', va='bottom')
    for x_, y_ in zip(x, y2):
        plt.text(x_, y_, y_, ha='left', va='bottom')
    for x_, y_ in zip(x, y3):
        plt.text(x_, y_, y_, ha='left', va='bottom')

    # 画网格线
    # plt.grid(which='minor', c='lightgrey')

    # 图例展示
    plt.legend(loc='upper left', fontsize=15, ncol=1)
    plt.show()  # 显示图像


if __name__ == '__main__':
    plot()
