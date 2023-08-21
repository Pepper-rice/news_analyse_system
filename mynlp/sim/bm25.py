# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

'''
BM25相关度评分算法
'''
class BM25(object):
    # 初始化BM25模型。传入文档集合`docs`, 统计各个词的文档频数`df`和单词频数`f`, 计算文档平均长度`avgdl`和idf值`idf`
    def __init__(self, docs):
        self.D = len(docs)
        self.avgdl = sum([len(doc)+0.0 for doc in docs]) / self.D
        self.docs = docs
        self.f = []
        self.df = {}
        self.idf = {}
        self.k1 = 1.5
        self.b = 0.75
        self.init()

    # 初始化BM25模型的参数。统计各个词的`df`和`f`, 计算`idf`
    def init(self):
        for doc in self.docs:
            tmp = {}
            for word in doc:
                if not word in tmp:
                    tmp[word] = 0
                tmp[word] += 1
            self.f.append(tmp)
            for k, v in tmp.items():
                if k not in self.df:
                    self.df[k] = 0
                self.df[k] += 1
        for k, v in self.df.items():
            self.idf[k] = math.log(self.D-v+0.5)-math.log(v+0.5)

    # 计算doc和index索引对应的文档的BM25相关度评分。根据idf、f、df、avgdl和BM25的k1、b参数计算得分
    def sim(self, doc, index):
        score = 0
        for word in doc:
            if word not in self.f[index]:
                continue
            d = len(self.docs[index])
            score += (self.idf[word]*self.f[index][word]*(self.k1+1)
                      / (self.f[index][word]+self.k1*(1-self.b+self.b*d
                                                      / self.avgdl)))
        return score

    # 计算doc和所有文档的BM25相关度评分
    def simall(self, doc):
        scores = []
        for index in range(self.D):
            score = self.sim(doc, index)
            scores.append(score)
        return scores
