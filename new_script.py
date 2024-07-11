import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 定义函数，用于绘制曲线
def f(x):
    return np.sin(x) * np.exp(-x)

# 定义x轴范围
x = np.linspace(-5, 5, 100)  # 创建一个从-5到5的等间距数组，包含100个点

# 绘制曲线
plt.plot(x, f(x), label='f(x) = sin(x) * exp(-x)')

# 设置图例
plt.legend()

# 设置标题和坐标轴标签
plt.title('曲线绘制示例')
plt.xlabel('x轴')
plt.ylabel('y轴')

# 显示图表
plt.show()