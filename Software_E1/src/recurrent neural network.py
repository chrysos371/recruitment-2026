"""
循环神经网络案例
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
    all_words = []
    unique_words = []
    #遍历所有文本，将每个词分别存入列表中
    for line in open(file_name, 'r',encoding='utf-8'):
        #使用jieba对中文进行分词
        words = jieba.lcut(line)
        #将每个词都存到这个列表里
        all_words.append(words)
        for word in words:
            #去重
            if word not in unique_words:
                unique_words.append(word)
    word_count = len(unique_words)
    #构建一个字典，形成每个词对应的索引
    word_to_index = {word: idx for idx,word in enumerate(unique_words)}
    #构建由每个词的索引构成的列表
    corpus_idx = []
    for words in all_words:
        temp = []
        #获取每一行的词的索引
        for word in words:
            temp.append(word_to_index[word])
        #在每一行每个索引之间加空格隔开
        temp.append(word_to_index[' '])
        #获取每个词对应的索引
        corpus_idx.append(temp)
    return corpus_idx, word_count, word_to_index, unique_words
class lyricsdataset(torch.utils.data.Dataset):
    def __init__(self, corpus_idx, num_chars):
        self.corpus_idx = corpus_idx
        self.num_chars = num_chars
        self.word_count = len(corpus_idx)
        self.valid_count = max(len(corpus_idx) - self.num_chars - 1, 1)
    def __len__(self):
        return self.valid_count
    def __getitem__(self, idx):
        # 修正起始索引，只防越界
        start = min(max(idx, 0), len(self.corpus_idx) - 1)
        # 直接截取，不管长度够不够
        x = self.corpus_idx[start: start + self.num_chars]
        y = self.corpus_idx[start + 1: start + 1 + self.num_chars]
        # 转成long型返回（不用手动填充）
        return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)
class TextGenerator(nn.Module):
    def __init__(self,word_count):
        super(TextGenerator, self).__init__()
        self.ebd = nn.Embedding(num_embeddings=word_count, embedding_dim=128)
        self.rnn = nn.RNN(input_size=128, hidden_size=128, num_layers=1, batch_first=True)
        self.out = nn.Linear(in_features=128, out_features=word_count)
    def forward(self,inputs,hidden):
        embled = self.ebd(inputs)
        output, hidden = self.rnn(embled.transpose(0,1),hidden)
        output = self.out(output.reshape((-1,output.shape[-1])))
        return output,hidden
    def init_hidden(self):
        return torch.zeros(1,1,128)
def train():
    corpus_idx, word_count, word_to_index, unique_words = create_wordlist()
    lyrics = lyricsdataset(corpus_idx,8)
    model = TextGenerator(word_count)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(),lr=0.001)
    epochs = 10
    for epoch in range(epochs):
        lyrics_dataloader = DataLoader(
            lyrics,
            batch_size=1,  # 可以改成更大的batch_size，比如2/4
            shuffle=True,
            collate_fn=collate_fn  # 关键：添加自定义拼接函数
        )
        start = time.time()
        iter_num = 0
        total_loss = 0.0
        for x,y in lyrics_dataloader:
            hidden = model.init_hidden(bs = 1)
            output, hidden = model(x,hidden)
            y = torch.transpose(y,0,1).contiguous().view(-1)
            loss = criterion(output,y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            iter_num += 1
            total_loss += loss.item()
        print('epoch %3s loss: %.5f time %.2f'%(epoch+1,total_loss/iter_num,time.time()-start))
    torch.save(model.state_dict(),'lyrics.pth'% epoch)
def predict(start_word,sentence_length):
    index_to_word,word_to_index,word_count,_ = create_wordlist()
    model = TextGenerator(word_count)
    model.load_state_dict(torch.load('lyrics.pth'))
    hidden = model.init_hidden()
    word_idx = word_to_index[start_word]
    generate_sentence = [word_idx]
    for _ in range(sentence_length):
        output, hidden = model(torch.tensor([[word_idx]]),hidden)
        word_idx = torch.argmax(output)
        generate_sentence.append(word_idx)
    for idx in generate_sentence:
        print(index_to_word[idx],end=' ')
if __name__ == '__main__':
    train()
