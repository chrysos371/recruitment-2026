#include <iostream>
#include <cmath>
const double PI = 3.14159265358979323846;

// 一维输入的神经网络实现
class NeuralNetwork1D {
private:
    // 此处定义神经网络参数

public:
    NeuralNetwork1D() {
        // 初始化网络参数
    }

    double predict(double input_x) {
        // 实现神经网络前向传播
        return 0.0;  // 返回预测值
    }

};

// 二维输入的神经网络实现
class NeuralNetwork2D {
private:
    // 此处定义神经网络参数

public:
    NeuralNetwork2D() {
        // 初始化网络参数
    }

    double predict(double input_x1, double input_x2) {
        // 实现神经网络前向传播
        return 0.0;  // 返回预测值
    }

};

// 不要改动此类
class Test {
private:
    NeuralNetwork1D net1;
    NeuralNetwork2D net2;
public:
    double output_y(double input_x) {
        return net1.predict(input_x);
    }

    double output_y(double input_x1, double input_x2) {
        return net2.predict(input_x1, input_x2);
    }

    void testbench(int num) {
        double sum_error = 0.0;
        double average_error = 0.0;

        if (num == 0) {
            const int total = 500;
            for (int i = 0; i < total; i++) {
                double x = 1.0 * i / total * 2 * PI;
                double y = output_y(x);

                sum_error += std::abs(std::sin(x) - y);
            }
            average_error = sum_error / total;
        }
        else {
            const int total = 20;
            for (int i = 0; i < total; i++) {
                for (int j = 0; j < total; j++) {
                    double x1 = 1.0 * i / total * 2 * PI;
                    double x2 = 1.0 * j / total * 2 * PI;
                    double y = output_y(x1, x2);
                    double true_y = std::sin(x1) * std::cos(x2);

                    sum_error += std::abs(true_y - y);
                }
            }
            average_error = sum_error / (total * total);
        }


        std::cout << (num ? "The 2D is " : "The 1D is ");
        if (average_error <= 1e-2)
            std::cout << "Success! Average: " << average_error << std::endl;
        else
            std::cout << "Failure! Average: " << average_error << std::endl;
    }

};

int main()
{
    Test t;
    t.testbench(0);   // 参数为0或1，参数为0的时候输入1维度，参数为1的时候输入二维

    return 0;
}