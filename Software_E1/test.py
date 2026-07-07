import math
import os
import numpy as np


# 一维输入的神经网络实现
class NeuralNetwork1D:
    def __init__(self):
        

    def predict(self, input_x: float) -> float:
        



# 二维输入的神经网络实现
class NeuralNetwork2D:
    def __init__(self):
       

    def predict(self, input_x1: float, input_x2: float) -> float:
       

# 不要改动此类
class Test:
    def __init__(self):
        self.net1 = NeuralNetwork1D()
        self.net2 = NeuralNetwork2D()

    def output_y(self, input_x: float) -> float:
        return self.net1.predict(input_x)

    def output_y(self, input_x1: float, input_x2: float) -> float:
        return self.net2.predict(input_x1, input_x2)

    def testbench(self, num: int):
        sum_error = 0.0
        average_error = 0.0

        if num == 0:
            total = 500
            for i in range(total):
                x = 1.0 * i / total * 2 * math.pi
                y = self.output_y(x)
                sum_error += abs(math.sin(x) - y)
            average_error = sum_error / total
        else:
            total = 20
            for i in range(total):
                for j in range(total):
                    x1 = 1.0 * i / total * 2 * math.pi
                    x2 = 1.0 * j / total * 2 * math.pi
                    y = self.output_y(x1, x2)
                    true_y = math.sin(x1) * math.cos(x2)
                    sum_error += abs(true_y - y)
            average_error = sum_error / (total * total)

        label = "The 2D is " if num else "The 1D is "
        if average_error <= 1e-2:
            print(f"{label}Success! Average: {average_error}")
        else:
            print(f"{label}Failure! Average: {average_error}")


if __name__ == "__main__":
    t = Test()
    t.testbench(0)  # 参数为0或1，参数为0的时候输入1维度，参数为1的时候输入二维
