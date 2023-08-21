# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import codecs

from .. import normal
from .. import seg
from ..classification.bayes import Bayes

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'sentiment.marshal')

'''
情感分类器,包含贝叶斯分类器对象
'''
class Sentiment(object):
    # 初始化,包含贝叶斯分类器对象
    def __init__(self):
        self.classifier = Bayes()

    # 序列化情感分类器到文件,调用贝叶斯分类器的保存方法
    def save(self, fname, iszip=True):
        self.classifier.save(fname, iszip)

    # 从文件加载情感分类器,调用贝叶斯分类器的加载方法
    def load(self, fname=data_path, iszip=True):
        self.classifier.load(fname, iszip)

    # 处理文本,进行分词和过滤停用词
    def handle(self, doc):
        words = seg.seg(doc)
        words = normal.filter_stop(words)
        return words

    # 训练情感分类器,将处理后的数据传给贝叶斯分类器进行训练
    def train(self, neg_docs, pos_docs):
        data = []
        for sent in neg_docs:
            data.append([self.handle(sent), 'neg'])
        for sent in pos_docs:
            data.append([self.handle(sent), 'pos'])
        self.classifier.train(data)

    # 对新文本进行分类,调用贝叶斯分类器的分类方法,并返回正面类别的概率
    def classify(self, sent):
        ret, prob = self.classifier.classify(self.handle(sent))
        if ret == 'pos':
            return prob
        return 1-prob


classifier = Sentiment() # 情感分类器对象
classifier.load() # 从文件加载情感分类器

# 训练情感分类器
def train(neg_file, pos_file):
    neg_docs = codecs.open(neg_file, 'r', 'utf-8').readlines()
    pos_docs = codecs.open(pos_file, 'r', 'utf-8').readlines()
    global classifier
    classifier = Sentiment()
    classifier.train(neg_docs, pos_docs)

# 序列化情感分类器到文件
def save(fname, iszip=True):
    classifier.save(fname, iszip)

# 从文件加载情感分类器
def load(fname, iszip=True):
    classifier.load(fname, iszip)

# 对文本进行情感分类
def classify(sent):
    return classifier.classify(sent)

