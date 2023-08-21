# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import gzip
import marshal
from math import log, exp

from ..utils.frequency import AddOneProb

'''
朴素贝叶斯分类器
'''
class Bayes(object):

    def __init__(self): # 初始化贝叶斯分类器
        self.d = {} # 类别字典,键是类别,值是词频统计
        self.total = 0 # 总词数

    # 将贝叶斯分类器对象序列化到文件
    def save(self, fname, iszip=True):
        d = {}
        d['total'] = self.total
        d['d'] = {}
        for k, v in self.d.items():
            d['d'][k] = v.__dict__
        # 如果是python3,文件名加.3后缀
        if sys.version_info[0] == 3:
            fname = fname + '.3'
        # 如果不压缩,使用marshal序列化并存储到文件
        if not iszip:
            marshal.dump(d, open(fname, 'wb'))
        # 如果压缩,使用gzip压缩后序列化并存储到文件
        else:
            f = gzip.open(fname, 'wb')
            f.write(marshal.dumps(d))
            f.close()

    # 从文件中反序列化并加载贝叶斯分类器对象
    def load(self, fname, iszip=True):
        # 如果是python3,文件名加.3后缀
        if sys.version_info[0] == 3:
            fname = fname + '.3'
        # 如果不压缩,使用marshal反序列化并从文件加载
        if not iszip:
            d = marshal.load(open(fname, 'rb'))
        # 如果压缩,使用gzip解压后反序列化并从文件加载
        else:
            try:
                f = gzip.open(fname, 'rb')
                d = marshal.loads(f.read())
            except IOError:
                f = open(fname, 'rb')
                d = marshal.loads(f.read())
            f.close()
        self.total = d['total']
        self.d = {}
        for k, v in d['d'].items():
            self.d[k] = AddOneProb()
            self.d[k].__dict__ = v

    # 训练贝叶斯分类器
    def train(self, data):
        for d in data: # 遍历训练数据
            c = d[1] # 获取样本类别
            # 如果类别不存在,初始化AddOneProb对象
            if c not in self.d:
                self.d[c] = AddOneProb()
            # 遍历样本中的词,并统计词频
            for word in d[0]:
                self.d[c].add(word, 1)
        # 计算总词数
        self.total = sum(map(lambda x: self.d[x].getsum(), self.d.keys()))

    # 分类新样本
    def classify(self, x):
        # 计算每个类别的log似然度
        tmp = {}
        for k in self.d:
            tmp[k] = log(self.d[k].getsum()) - log(self.total)
            for word in x:
                tmp[k] += log(self.d[k].freq(word))
        # 找出log似然度最大的类别和对应的概率
        ret, prob = 0, 0
        for k in self.d:
            now = 0
            try:
                for otherk in self.d:
                    now += exp(tmp[otherk]-tmp[k])
                now = 1/now
            except OverflowError:
                now = 0
            if now > prob:
                ret, prob = k, now
        return (ret, prob)
