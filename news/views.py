from pydantic import JsonError
from .models import *
import json
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from pyecharts import options as opts
from pyecharts.charts import Map, Grid, Bar, Line, Pie, WordCloud
from pyecharts.faker import Faker
from pyecharts.commons.utils import JsCode
from pyecharts.options.charts_options import MapItem
from datetime import datetime, time
from django.core.paginator import Paginator
from django.db.models import Q
import simplejson
from mynlp import NLP
from jieba import analyse
from pyecharts.globals import SymbolType


def to_dict(l, exclude=tuple()):
    # 将数据库模型 变为 字典数据 的工具类函数
    def transform(v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return v

    def _todict(obj):
        j = {
            k: transform(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_") and k not in exclude
        }
        return j

    return [_todict(i) for i in l]

'''
def get_list(request):：定义了一个名为get_list的视图函数，接收一个名为request的对象，该对象包含了HTTP请求的相关信息。
body = request.json：从HTTP请求中获取请求体，并将其解析为Python对象，存储在body变量中。
pagesize = body.get("pagesize", 10)：从body中获取pagesize参数的值，如果没有传递该参数，则使用默认值10。
page = body.get("page", 1)：从body中获取page参数的值，如果没有传递该参数，则使用默认值1。
query = {...}：创建一个名为query的字典，该字典用于存储过滤条件。该字典的键是去掉首字符后的参数名，值是参数值。这里使用了一个字典推导式来构造query字典，只有以"_"开头的参数才会被视为过滤条件。
q = Q(**query)：使用query字典构造一个Q对象，用于构建查询过滤条件。
objs = News.objects.filter(q).order_by("-id")：使用filter()方法过滤News模型对象，只保留符合q条件的对象，并按照id字段进行降序排列。
paginator = Paginator(objs, pagesize)：创建一个Paginator对象，用于对查询结果进行分页处理。
pg = paginator.page(page)：获取指定页数的分页对象。
result = to_dict(pg.object_list)：将分页对象的结果序列化为字典，存储在result变量中。
return JsonResponse({"total": paginator.count, "result": result})：使用JsonResponse类构造一个JSON响应，包含了查询结果的总数和当前页的数据。
'''
def get_list(request):
    # 文本列表
    body = request.json
    pagesize = body.get("pagesize", 10)
    page = body.get("page", 1)
    query = {
        k[1:]: v
        for k, v in body.items()
        if k.startswith("_") and (v != "" and v is not None)
    }
    #这里的query是一个字典，存储了过滤条件。
    #**query是Python中的一种特殊语法，用于将一个字典解包成一组关键字参数。
    #这里使用了**运算符将query字典解包，将其中的键值对作为Q()的关键字参数传入，从而构造出一个Q查询对象。
    #这个Q对象用于过滤数据库中的News模型对象，仅保留符合过滤条件的对象
    q = Q(**query)
    #这行代码实际上对应的是一条SQL语句，ORM框架会将其翻译成相应的SQL语句并执行。
    #这段代码中的News是一个Django模型，它映射了数据库中的一个表。
    #objects是一个Django自动生成的管理器，它提供了各种数据库操作方法，如filter()和order_by()等。
    #这里的filter()方法使用了q条件，以过滤符合条件的News模型对象
    #order_by()方法按照id字段进行降序排列查询结果。
    #最终的查询结果objs包含了所有符合条件的News模型对象。
    objs = News.objects.filter(q).order_by("-id")
    paginator = Paginator(objs, pagesize)
    pg = paginator.page(page)
    result = to_dict(pg.object_list)
    return JsonResponse({"total": paginator.count, "result": result})


def get_detail(request):
    body = request.json
    id = body.get("id")
    o = News.objects.get(pk=id)
    # 点击率+1
    o.view_count += 1
    o.save()
    return JsonResponse(to_dict([o])[0])


def sentiment(request):
    # 情感分析
    data = request.json
    text = data.get("text")
    try:
        prob = [round(i, 2) for i in News.sentiment(text)]
    except:
        prob = [0.5, 0.5]

    return JsonResponse(prob, safe=False)


def pie(request):
    # 文本的正负面概率占比饼图
    data = request.json
    text = data.get("text")
    try:
        prob = [round(i, 2) for i in News.sentiment(text)]
    except:
        prob = [0.5, 0.5]
    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(["正面指数", "负面指数"], prob)],
            radius=["50%", "70%"],
            label_opts=opts.LabelOpts(formatter="{b}: {d}%"),
        )
        .set_colors(["green", "red"])
        .set_global_opts(
            title_opts=opts.TitleOpts("文本情感分析结果", pos_left="center", pos_bottom=0),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return HttpResponse(c.dump_options(), content_type="aplication/json")


def keywords(request):
    # 文本的关键词分析
    data = request.json
    text = data.get("text")
    keywords = analyse.extract_tags(text, withWeight=True, topK=100)
    c = (
        WordCloud()
        .add("", keywords, word_size_range=[20, 100])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="关键词云图", pos_left="center", pos_bottom=0)
        )
    )
    return HttpResponse(c.dump_options(), content_type="aplication/json")


def summary(request):
    # 文本的摘要
    data = request.json
    text = data.get("text")
    return JsonResponse(NLP(text).summary(), safe=False)


def tag(request):
    # 文本的词性分析
    data = request.json
    text = data.get("text")
    result = list(NLP(text).tags)
    return JsonResponse(result, safe=False)

