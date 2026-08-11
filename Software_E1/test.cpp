/**
 * @file    test.cpp
 * @brief   BP 神经网络 C++ 实现 — fit sin(x) (1D) & sin(x1)·cos(x2) (2D)
 * @author  张杨亦航 (2524030231)
 * @date    2026-07-08
 *
 * 河海大学智泽实验室 2026 招新考核 — Software_E1
 *
 * 权重来源: 由 test.py 训练并导出为 C 头文件。
 * 在项目目录下运行: python test.py   # 训练并生成 e1_1d_weights.npz / e1_2d_weights.npz
 * 然后运行:  python export_weights.py  # 生成 e1_1d_weights.h / e1_2d_weights.h
 *
 * 编译方法 (VS 2022 MSVC):
 *   cl /EHsc /std:c++20 /utf-8 /Fe:e1_test.exe test.cpp
 */

#include <iostream>
#include <cmath>
#include <algorithm>
const double PI = 3.14159265358979323846;

// ---- 嵌入的预训练权重 (由 export_weights.py 从 .npz 导出) ----
#include "e1_1d_weights.h"
#include "e1_2d_weights.h"

// ---- 激活函数 ----
inline double relu(double x) {
    return x > 0.0 ? x : 0.0;
}

// ---- 一维网络: 结构 [1, 32, 64, 1] ----
class NeuralNetwork1D {
private:
    // 前向传播: input 已归一化到 [0, 1]
    double forward(double x_norm) const {
        // Layer 0: input(1) → hidden1(32), w0_1d: 32×1, b0_1d: 32×1
        double h1[32];
        for (int i = 0; i < 32; ++i) {
            h1[i] = relu(w0_1d[i] * x_norm + b0_1d[i]);
        }
        // Layer 1: hidden1(32) → hidden2(64), w1_1d: 64×32, b1_1d: 64×1
        double h2[64];
        for (int i = 0; i < 64; ++i) {
            double sum = b1_1d[i];
            const double* w_row = &w1_1d[i * 32];
            for (int j = 0; j < 32; ++j) {
                sum += w_row[j] * h1[j];
            }
            h2[i] = relu(sum);
        }
        // Layer 2: hidden2(64) → output(1), w2_1d: 1×64, b2_1d: 1×1
        double sum = b2_1d[0];
        for (int j = 0; j < 64; ++j) {
            sum += w2_1d[j] * h2[j];
        }
        return sum;
    }

public:
    NeuralNetwork1D() {}

    double predict(double input_x) {
        // 归一化输入 (与训练时一致: x / (2*PI))
        double x_norm = input_x / (2.0 * PI);
        return forward(x_norm);
    }
};

// ---- 二维网络: 结构 [2, 48, 96, 48, 1] ----
class NeuralNetwork2D {
private:
    double forward(double x1_norm, double x2_norm) const {
        // Layer 0: input(2) → hidden1(48), w0: 48×2, b0: 48×1
        double h1[48];
        for (int i = 0; i < 48; ++i) {
            h1[i] = relu(w0_2d[i * 2] * x1_norm + w0_2d[i * 2 + 1] * x2_norm + b0_2d[i]);
        }
        // Layer 1: hidden1(48) → hidden2(96), w1_2d: 96×48, b1_2d: 96×1
        double h2[96];
        for (int i = 0; i < 96; ++i) {
            double sum = b1_2d[i];
            const double* w_row = &w1_2d[i * 48];
            for (int j = 0; j < 48; ++j) {
                sum += w_row[j] * h1[j];
            }
            h2[i] = relu(sum);
        }
        // Layer 2: hidden2(96) → hidden3(48), w2_2d: 48×96, b2_2d: 48×1
        double h3[48];
        for (int i = 0; i < 48; ++i) {
            double sum = b2_2d[i];
            const double* w_row = &w2_2d[i * 96];
            for (int j = 0; j < 96; ++j) {
                sum += w_row[j] * h2[j];
            }
            h3[i] = relu(sum);
        }
        // Layer 3: hidden3(48) → output(1), w3_2d: 1×48, b3_2d: 1×1
        double sum = b3_2d[0];
        for (int j = 0; j < 48; ++j) {
            sum += w3_2d[j] * h3[j];
        }
        return sum;
    }

public:
    NeuralNetwork2D() {}

    double predict(double input_x1, double input_x2) {
        double x1_norm = input_x1 / (2.0 * PI);
        double x2_norm = input_x2 / (2.0 * PI);
        return forward(x1_norm, x2_norm);
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
    t.testbench(1);

    return 0;
}
