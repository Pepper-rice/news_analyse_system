# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re

from . import seg as TnTseg

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'seg.marshal')
segger = TnTseg.Seg() # TnTseg模型对象,实现分词逻辑
segger.load(data_path, True) # TnTseg模型数据路径
re_zh = re.compile('([\u4E00-\u9FA5]+)') # 正则表达式,用于提取中文词
'''
中文分词,使用TnTseg统计模型（一种HMM隐马尔可夫模型）
'''
# 实现对输入句子`sent`的分词。使用正则表达式提取中文词,中文词使用`single_seg()`方法分词,非中文词直接切分。返回分词结果`words`。
def seg(sent):
    words = []
    for s in re_zh.split(sent):
        s = s.strip()
        if not s:
            continue
        if re_zh.match(s):
            words += single_seg(s)
        else:
            for word in s.split():
                word = word.strip()
                if word:
                    words.append(word)
    return words

# 训练TnTseg模型。读取训练数据,调用`segger.train()`训练模型
def train(fname):
    global segger
    segger = TnTseg.Seg()
    segger.train(fname)

# 保存TnTseg模型。调用`segger.save()`保存模型
def save(fname, iszip=True):
    segger.save(fname, iszip)

# 加载TnTseg模型。调用`segger.load()`加载模型
def load(fname, iszip=True):
    segger.load(fname, iszip)

# 使用TnTseg模型实现单个中文词的分词。调用`segger.seg()`获得分词结果
def single_seg(sent):
    return list(segger.seg(sent))
