# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs

from ..utils.trie import Trie


class PinYin(object):
    # 负责初始化, 构建Trie树
    def __init__(self, fname):
        self.handle = Trie()
        fr = codecs.open(fname, 'r', 'utf-8')
        for line in fr:
            words = line.split()
            self.handle.insert(words[0], words[1:])
        fr.close()

    # 负责实现具体的转换逻辑
    def get(self, text):
        ret = []
        for i in self.handle.translate(text):
            if isinstance(i, list) or isinstance(i, tuple):
                ret = ret + i
            else:
                ret.append(i)
        return ret
