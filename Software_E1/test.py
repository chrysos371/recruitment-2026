"""
Software_E1 — BP 神经网络手写实现
===================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

纯 NumPy 实现多层感知机, 不使用任何深度学习框架。
拟合: sin(x) (一维) 和 sin(x1)·cos(x2) (二维)
要求: MAE ≤ 0.01
"""

import math
import numpy as np


# ================================================================
#  激活函数
# ================================================================

def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)


def relu_derivative(x: np.ndarray) -> np.ndarray:
    return (x > 0).astype(np.float64)


# ================================================================
#  Mini-Batch SGD 训练器
# ================================================================

class MLPTrainer:
    """手动实现的全连接网络训练器 (纯 NumPy)"""

    def __init__(self, layer_sizes: list[int], learning_rate: float = 0.01):
        self.layer_sizes = layer_sizes
        self.lr = learning_rate
        self.weights = []
        self.biases = []

        # Xavier 初始化: 对单输入 (fan_in=1) 比 He 更温和, 避免权重爆炸
        rng = np.random.default_rng(42)
        for i in range(len(layer_sizes) - 1):
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            # Xavier uniform 的变体, 限制初始权重大小
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            self.weights.append(rng.uniform(-limit, limit,
                                           (layer_sizes[i + 1], layer_sizes[i])))
            self.biases.append(np.zeros((layer_sizes[i + 1], 1)))

        # 缓存前向传播中间值 (用于反向传播)
        self.z_cache = []   # 激活前 (wx + b)
        self.a_cache = []   # 激活后

    def forward(self, x: np.ndarray) -> np.ndarray:
        """前向传播, 返回输出并缓存中间值。x shape: (n_features, batch_size)"""
        self.z_cache = []
        self.a_cache = [x]

        a = x
        for i in range(len(self.weights)):
            z = np.dot(self.weights[i], a) + self.biases[i]
            self.z_cache.append(z)
            if i == len(self.weights) - 1:
                a = z  # 输出层无激活
            else:
                a = relu(z)
            self.a_cache.append(a)

        return a

    def backward(self, y_true: np.ndarray) -> None:
        """反向传播, 计算梯度并更新参数。y_true shape: (n_outputs, batch_size)"""
        batch_size = y_true.shape[1]
        y_pred = self.a_cache[-1]

        # 输出层梯度: dL/dz = 2*(y_pred - y_true) / batch_size
        delta = np.clip(2.0 * (y_pred - y_true) / batch_size, -10.0, 10.0)

        for i in range(len(self.weights) - 1, -1, -1):
            a_prev = self.a_cache[i]  # 前一层的激活输出

            # 权重和偏置梯度
            dW = np.dot(delta, a_prev.T)
            db = np.sum(delta, axis=1, keepdims=True)

            # 梯度裁剪 (防止爆炸)
            dW = np.clip(dW, -1.0, 1.0)
            db = np.clip(db, -1.0, 1.0)

            # 更新参数 (SGD)
            self.weights[i] -= self.lr * dW
            self.biases[i] -= self.lr * db

            # 向上一层传播 (隐藏层需乘激活函数导数)
            if i > 0:
                delta = np.dot(self.weights[i].T, delta) * relu_derivative(self.z_cache[i - 1])
                delta = np.clip(delta, -10.0, 10.0)

    def train(self, X: np.ndarray, Y: np.ndarray, epochs: int,
              batch_size: int = 64, verbose: bool = False) -> list[float]:
        """训练网络。X/Y shape: (n_samples, n_features) 和 (n_samples, n_outputs)"""
        n_samples = X.shape[0]
        losses = []

        for epoch in range(epochs):
            # 打乱数据
            perm = np.random.permutation(n_samples)
            X_shuffled = X[perm]
            Y_shuffled = Y[perm]

            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n_samples, batch_size):
                end = min(start + batch_size, n_samples)
                x_batch = X_shuffled[start:end].T   # (features, batch)
                y_batch = Y_shuffled[start:end].T   # (outputs, batch)

                y_pred = self.forward(x_batch)
                self.backward(y_batch)

                batch_loss = np.mean((y_pred - y_batch) ** 2)
                epoch_loss += batch_loss
                n_batches += 1

            avg_loss = epoch_loss / n_batches
            losses.append(avg_loss)

            if verbose and epoch % 500 == 0:
                print(f"  epoch {epoch:4d}/{epochs}  loss={avg_loss:.8f}")

        return losses

    def predict(self, x: np.ndarray) -> np.ndarray:
        """单样本预测。x shape: (n_features, 1), 返回标量。"""
        y = self.forward(x)
        return y[0, 0]


# ================================================================
#  一维输入的神经网络实现
# ================================================================

class NeuralNetwork1D:
    def __init__(self):
        # 网络: 1 → 32 → 64 → 1, ReLU 隐藏层, 输出无激活
        self.net = MLPTrainer([1, 32, 64, 1], learning_rate=0.001)

        # 生成训练数据: sin(x) on [0, 2π]
        # 输入归一化到 [0, 1] 帮助收敛
        n_samples = 2000
        X_raw = np.linspace(0, 2 * math.pi, n_samples).reshape(-1, 1).astype(np.float64)
        X_train = X_raw / (2 * math.pi)
        Y_train = np.sin(X_raw).astype(np.float64)

        # 训练
        self.net.train(X_train, Y_train, epochs=8000, batch_size=64)

    def predict(self, input_x: float) -> float:
        # 归一化输入 (与训练时一致)
        x_norm = input_x / (2 * math.pi)
        x = np.array([[x_norm]], dtype=np.float64).T  # (1, 1)
        return float(self.net.predict(x))


# ================================================================
#  二维输入的神经网络实现
# ================================================================

class NeuralNetwork2D:
    def __init__(self):
        # 网络: 2 → 48 → 96 → 48 → 1, ReLU 隐藏层, 输出无激活
        self.net = MLPTrainer([2, 48, 96, 48, 1], learning_rate=0.0015)

        # 生成训练数据: sin(x1)·cos(x2) on [0, 2π]²
        # 输入归一化到 [0, 1] 帮助收敛
        n = 80
        x1_vals = np.linspace(0, 2 * math.pi, n)
        x2_vals = np.linspace(0, 2 * math.pi, n)
        X1_raw, X2_raw = np.meshgrid(x1_vals, x2_vals)
        X_train = np.column_stack([X1_raw.ravel() / (2 * math.pi),
                                    X2_raw.ravel() / (2 * math.pi)]).astype(np.float64)
        Y_train = (np.sin(X1_raw) * np.cos(X2_raw)).ravel().reshape(-1, 1).astype(np.float64)

        # 训练
        self.net.train(X_train, Y_train, epochs=25000, batch_size=128)

    def predict(self, input_x1: float, input_x2: float) -> float:
        # 归一化输入 (与训练时一致)
        x = np.array([[input_x1 / (2 * math.pi)],
                      [input_x2 / (2 * math.pi)]], dtype=np.float64)  # (2, 1)
        return float(self.net.predict(x))


# ================================================================
#  不要改动此类
# ================================================================

class Test:
    def __init__(self):
        self.net1 = NeuralNetwork1D()
        self.net2 = NeuralNetwork2D()

    def output_y(self, input_x: float, input_x2: float = None) -> float:
        """统一入口: 1 参数走 1D 网络, 2 参数走 2D 网络。
           Python 不支持 C++ 式的方法重载, 用默认参数实现。"""
        if input_x2 is None:
            return self.net1.predict(input_x)
        return self.net2.predict(input_x, input_x2)

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
    t.testbench(0)  # 参数为0: 一维 sin(x)
    t.testbench(1)  # 参数为1: 二维 sin(x1)·cos(x2)
