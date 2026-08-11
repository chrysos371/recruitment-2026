"""
循环神经网络案例 — 歌词生成
======================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

修复说明:
  - corpus_idx 扁平化为单一序列 (修复 list-of-lists 当作 flat 序列的 bug)
  - init_hidden 支持 bs 参数
  - 修复 train/predict 中的类型和解包错误
  - 修复模型保存路径格式字符串问题
  - 新增 collate_fn 处理不等长序列
"""
import torch
import re
import jieba
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import time


def create_wordlist():
    #导入数据集
    file_name = 'jaychou_lyrics.txt'
    #将每个词存入列表中
    unique_words = [' ']  # 预置空格/分隔符
    #构建由每个词的索引构成的扁平序列
    corpus_idx = []
    #遍历所有文本，将每个词分别存入列表中
    for line in open(file_name, 'r', encoding='utf-8'):
        #使用jieba对中文进行分词
        words = jieba.lcut(line)
        for word in words:
            #去重
            if word not in unique_words:
                unique_words.append(word)
            # 将每个词的索引加入扁平序列
            corpus_idx.append(unique_words.index(word))
        # 行间加空格分隔
        corpus_idx.append(0)  # ' ' 索引为 0
    word_count = len(unique_words)
    #构建一个字典，形成每个词对应的索引
    word_to_index = {word: idx for idx, word in enumerate(unique_words)}
    index_to_word = {idx: word for word, idx in word_to_index.items()}
    return corpus_idx, word_count, word_to_index, index_to_word


def collate_fn(batch):
    """自定义 collate: 对不等长序列做 padding"""
    x_list, y_list = zip(*batch)
    # 找到最大长度
    max_len = max(len(x) for x in x_list)
    # padding 到相同长度
    x_padded = torch.zeros(len(x_list), max_len, dtype=torch.long)
    y_padded = torch.zeros(len(y_list), max_len, dtype=torch.long)
    for i, (x, y) in enumerate(zip(x_list, y_list)):
        x_padded[i, :len(x)] = x
        y_padded[i, :len(y)] = y
    return x_padded, y_padded


class lyricsdataset(torch.utils.data.Dataset):
    def __init__(self, corpus_idx, num_chars):
        # corpus_idx 是扁平的一维列表
        self.corpus_idx = corpus_idx
        self.num_chars = num_chars
        self.word_count = len(set(corpus_idx))
        self.valid_count = max(len(corpus_idx) - self.num_chars - 1, 1)

    def __len__(self):
        return self.valid_count

    def __getitem__(self, idx):
        # 确保索引不越界
        start = min(max(idx, 0), len(self.corpus_idx) - self.num_chars - 1)
        x = self.corpus_idx[start: start + self.num_chars]
        y = self.corpus_idx[start + 1: start + 1 + self.num_chars]
        return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)


class TextGenerator(nn.Module):
    def __init__(self, word_count):
        super(TextGenerator, self).__init__()
        self.ebd = nn.Embedding(num_embeddings=word_count, embedding_dim=128)
        self.rnn = nn.RNN(input_size=128, hidden_size=128, num_layers=1, batch_first=True)
        self.out = nn.Linear(in_features=128, out_features=word_count)

    def forward(self, inputs, hidden):
        embled = self.ebd(inputs)
        output, hidden = self.rnn(embled, hidden)
        output = self.out(output.reshape((-1, output.shape[-1])))
        return output, hidden

    def init_hidden(self, bs=1):
        return torch.zeros(1, bs, 128)


def train():
    corpus_idx, word_count, word_to_index, index_to_word = create_wordlist()
    lyrics = lyricsdataset(corpus_idx, 8)
    model = TextGenerator(word_count)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    epochs = 10
    for epoch in range(epochs):
        lyrics_dataloader = DataLoader(
            lyrics,
            batch_size=1,
            shuffle=True,
            collate_fn=collate_fn
        )
        start = time.time()
        iter_num = 0
        total_loss = 0.0
        for x, y in lyrics_dataloader:
            bs = x.size(0)
            hidden = model.init_hidden(bs=bs)
            output, hidden = model(x, hidden)
            y = y.view(-1)
            loss = criterion(output, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            iter_num += 1
            total_loss += loss.item()
        print('epoch %3s loss: %.5f time %.2f' % (epoch + 1, total_loss / iter_num, time.time() - start))
    torch.save(model.state_dict(), 'lyrics.pth')


def predict(start_word, sentence_length):
    corpus_idx, word_count, word_to_index, index_to_word = create_wordlist()
    model = TextGenerator(word_count)
    model.load_state_dict(torch.load('lyrics.pth'))
    hidden = model.init_hidden(bs=1)
    if start_word not in word_to_index:
        print(f"词 '{start_word}' 不在词典中")
        return
    word_idx = word_to_index[start_word]
    generate_sentence = [word_idx]
    for _ in range(sentence_length):
        output, hidden = model(torch.tensor([[word_idx]]), hidden)
        word_idx = torch.argmax(output).item()
        generate_sentence.append(word_idx)
    for idx in generate_sentence:
        if idx in index_to_word:
            print(index_to_word[idx], end=' ')
    print()


if __name__ == '__main__':
    train()
