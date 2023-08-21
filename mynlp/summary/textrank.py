# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..sim.bm25 import BM25


class TextRank(object):

    def __init__(self, docs):
        self.docs = docs           # 文档集合
        self.bm25 = BM25(docs)     # BM25相关度计算模型
        self.D = len(docs)        # 文档数量
        self.d = 0.85             # 阻尼系数,值越大表示随机游走的概率越大
        self.weight = []          # 两篇文档的相关性权重
        self.weight_sum = []      # 权重的归一化因子
        self.vertex = []          # 顶点权重
        self.max_iter = 200       # 迭代次数
        self.min_diff = 0.001     # 收敛判定值
        self.top = []

    # 迭代计算文档之间的权重, 直到收敛。返回关键文档
    def solve(self):
        # 构建图,初始化vertex和weight
        for cnt, doc in enumerate(self.docs):
            scores = self.bm25.simall(doc)
            self.weight.append(scores)
            self.weight_sum.append(sum(scores)-scores[cnt])
            self.vertex.append(1.0)
        # 迭代计算直到收敛
        for _ in range(self.max_iter):
            m = []
            max_diff = 0
            for i in range(self.D):
                m.append(1-self.d)
                for j in range(self.D):
                    if j == i or self.weight_sum[j] == 0:
                        continue
                    m[-1] += (self.d*self.weight[j][i]
                              / self.weight_sum[j]*self.vertex[j])
                if abs(m[-1] - self.vertex[i]) > max_diff:
                    max_diff = abs(m[-1] - self.vertex[i])
            self.vertex = m
            if max_diff <= self.min_diff:
                break
        # 返回top关键词
        self.top = list(enumerate(self.vertex))
        self.top = sorted(self.top, key=lambda x: x[1], reverse=True)

    # 返回top关键文档的索引
    def top_index(self, limit):
        return list(map(lambda x: x[0], self.top))[:limit]

    # 返回top关键文档内容
    def top(self, limit):
        return list(map(lambda x: self.docs[x[0]], self.top))


class KeywordTextRank(object):

    # 继承TextRank, 并新增构建词图的参数
    def __init__(self, docs):
        # 继承TextRank,并新增words表示词与词的邻接关系
        self.docs = docs
        self.words = {}
        self.vertex = {}
        self.d = 0.85
        self.max_iter = 200
        self.min_diff = 0.001
        self.top = []

    # 先构建词图, 然后迭代计算词之间的权重, 直到收敛。返回关键词
    def solve(self):
        # 构建词图,初始化vertex和words
        for doc in self.docs:
            que = []
            for word in doc:
                if word not in self.words:
                    self.words[word] = set()
                    self.vertex[word] = 1.0
                que.append(word)
                if len(que) > 5:
                    que.pop(0)
                for w1 in que:
                    for w2 in que:
                        if w1 == w2:
                            continue
                        self.words[w1].add(w2)
                        self.words[w2].add(w1)
        for _ in range(self.max_iter):
            m = {}
            max_diff = 0
            tmp = filter(lambda x: len(self.words[x[0]]) > 0,
                         self.vertex.items())
            tmp = sorted(tmp, key=lambda x: x[1] / len(self.words[x[0]]))
            for k, v in tmp:
                for j in self.words[k]:
                    if k == j:
                        continue
                    if j not in m:
                        m[j] = 1 - self.d
                    m[j] += (self.d / len(self.words[k]) * self.vertex[k])
            for k in self.vertex:
                if k in m and k in self.vertex:
                    if abs(m[k] - self.vertex[k]) > max_diff:
                        max_diff = abs(m[k] - self.vertex[k])
            self.vertex = m
            if max_diff <= self.min_diff:
                break
        self.top = list(self.vertex.items())
        self.top = sorted(self.top, key=lambda x: x[1], reverse=True)

    # 返回top关键词的索引
    def top_index(self, limit):
        return list(map(lambda x: x[0], self.top))[:limit]

    # 返回top关键词内容
    def top(self, limit):
        return list(map(lambda x: self.docs[x[0]], self.top))
