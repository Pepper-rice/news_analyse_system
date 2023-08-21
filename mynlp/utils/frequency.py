# -*- coding: utf-8 -*-

from . import good_turing
# 基类,实现了概率分布的基本接口。包含样本总数`total`、不存在样本概率`none`和样本-频率映射`d`。实现了查询样本频率和频率的接口
class BaseProb(object):

    def __init__(self):
        self.d = {}
        self.total = 0.0
        self.none = 0

    def exists(self, key):
        return key in self.d

    def getsum(self):
        return self.total

    def get(self, key):
        if not self.exists(key):
            return False, self.none
        return True, self.d[key]

    def freq(self, key):
        return float(self.get(key)[1])/self.total

    def samples(self):
        return self.d.keys()

# 普通概率模型。通过`add()`方法增加样本频率,总样本数增加,没有见过的样本概率为0
class NormalProb(BaseProb):

    def add(self, key, value):
        if not self.exists(key):
            self.d[key] = 0
        self.d[key] += value
        self.total += value

# Add-One概率模型。通过`add()`增加样本频率时,总样本数和每个样本的频率都加1。没有见过的样本初始化频率为1。这可以避免频率为0的问题
class AddOneProb(BaseProb):

    def __init__(self):
        self.d = {}
        self.total = 0.0
        self.none = 1

    def add(self, key, value):
        self.total += value
        if not self.exists(key):
            self.d[key] = 1
            self.total += 1
        self.d[key] += value

# Good-Turing 概率模型。通过`good_turing`模块实现Good-Turing平滑,得到样本-频率映射`d`和不存在样本概率`none`。这可以通过近似的方法给低频样本分配更高的频率
class GoodTuringProb(BaseProb):

    def __init__(self):
        self.d = {}
        self.total = 0.0
        self.handled = False

    def add(self, key, value):
        if not self.exists(key):
            self.d[key] = 0
        self.d[key] += value

    def get(self, key):
        if not self.handled:
            self.handled = True
            tmp, self.d = good_turing.main(self.d)
            self.none = tmp
            self.total = sum(self.d.values())+0.0
        if not self.exists(key):
            return False, self.none
        return True, self.d[key]
