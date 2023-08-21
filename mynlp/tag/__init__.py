# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import codecs

from ..utils.tnt import TnT

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'tag.marshal')
tagger = TnT()
tagger.load(data_path)

# 训练TnT模型。读取训练数据,格式为`word/tag`,按行读取,构建数据集`data`。然后调用TnT模型的`train()`方法训练模型
def train(fname):
    fr = codecs.open(fname, 'r', 'utf-8')
    data = []
    for i in fr:
        line = i.strip()
        if not line:
            continue
        tmp = map(lambda x: x.split('/'), line.split())
        data.append(tmp)
    fr.close()
    global tagger
    tagger = TnT()
    tagger.train(data)

# 保存TnT模型。调用TnT模型的`save()`方法保存模型
def save(fname, iszip=True):
    tagger.save(fname, iszip)

# 加载TnT模型。调用TnT模型的`load()`方法加载模型
def load(fname, iszip=True):
    tagger.load(fname, iszip)

# 词性标注,返回词和词性的列表。调用TnT模型的`tag()`方法进行标注
def tag_all(words):
    return tagger.tag(words)

# simply词性标注,返回词性列表。调用`tag_all()`并只返回词性结果
def tag(words):
    return map(lambda x: x[1], tag_all(words))
