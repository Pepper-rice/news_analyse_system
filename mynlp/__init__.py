# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import normal
from . import seg
from . import tag
from . import sentiment
from .sim import bm25
from .summary import textrank
from .summary import words_merge


class NLP(object):

    def __init__(self, doc):
        self.doc = doc
        self.bm25 = bm25.BM25(doc)

    # 返回对输入文本进行分词处理后的结果
    @property
    def words(self):
        return seg.seg(self.doc)

    # 返回对输入文本进行句子分割后的结果
    @property
    def sentences(self):
        return normal.get_sentences(self.doc)

    # 返回对输入文本进行句子分割后的结果
    @property
    def han(self):
        return normal.zh2hans(self.doc)

    # 返回对输入文本进行中文简繁转换后的结果
    @property
    def pinyin(self):
        return normal.get_pinyin(self.doc)

    # 返回对输入文本进行拼音转换后的结果
    @property
    def sentiments(self):
        return sentiment.classify(self.doc)

    # 对输入文本进行词性标注并返回每个词和对应标签的zip对象
    @property
    def tags(self):
        words = self.words
        tags = tag.tag(words)
        return zip(words, tags)

    # 返回bm25模型中计算的词频信息
    @property
    def tf(self):
        return self.bm25.f

    # 返回bm25模型中计算的逆文档频率信息
    @property
    def idf(self):
        return self.bm25.idf

    # 调用bm25对象的simall方法，计算输入文本与初始化时传入的文本之间的相似度，并返回相似度结果
    def sim(self, doc):
        return self.bm25.simall(doc)

    # 定义了一个summary方法，接受一个可选参数limit，用于指定摘要的句子数量，默认为5。
    # 将文本分割为句子，并对每个句子进行分词和去停用词处理，然后将处理后的结果添加到doc列表中。
    # 创建一个textrank.TextRank对象，传入doc进行初始化。
    # 调用solve方法计算句子之间的权重。
    # 创建一个空列表ret，用于存储摘要句子。
    # 根据权重返回前limit个具有高权重的句子，并将其添加到ret中。
    # 返回摘要句子列表ret。
    def summary(self, limit=5):
        doc = []
        sents = self.sentences
        for sent in sents:
            words = seg.seg(sent)
            words = normal.filter_stop(words)
            doc.append(words)
        rank = textrank.TextRank(doc)
        rank.solve()
        ret = []
        for index in rank.top_index(limit):
            ret.append(sents[index])
        return ret

    # 定义了一个keywords方法，接受两个可选参数：limit用于指定关键词的数量，默认为5；merge用于指定是否合并关键词，默认为False。
    # 将文本分割为句子，并对每个句子进行分词和去停用词处理，然后将处理后的结果添加到doc列表中。
    # 创建一个textrank.KeywordTextRank对象，传入doc进行初始化。
    # 调用solve方法计算关键词权重。
    # 创建一个空列表ret，用于存储关键词。
    # 根据权重返回前limit个具有高权重的关键词，并将其添加到ret中。
    # 如果merge参数为True，则使用words_merge.SimpleMerge类将关键词与原始文本进行合并，并返回合并后的结果。
    # 否则，直接返回关键词列表ret。
    def keywords(self, limit=5, merge=False):
        doc = []
        sents = self.sentences
        for sent in sents:
            words = seg.seg(sent)
            words = normal.filter_stop(words)
            doc.append(words)
        rank = textrank.KeywordTextRank(doc)
        rank.solve()
        ret = []
        for w in rank.top_index(limit):
            ret.append(w)
        if merge:
            wm = words_merge.SimpleMerge(self.doc, ret)
            return wm.merge()
        return ret
