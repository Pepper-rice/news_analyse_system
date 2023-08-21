from re import U
import simplejson
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from index.utils import success, error
from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse

# 用户登录装饰器，用于限制必须登录的情况
def login_required(func):
    @wraps(func)
    def wrap(request: HttpRequest, *args, **kwargs):
        # 如果用户已登陆，允许访问
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return error(code=401)

    return wrap


# 用户登录视图
def login_view(request: HttpRequest):
    data = simplejson.loads(request.body)
    user = authenticate(
        request, username=data.get("username"), password=data.get("password")
    )
    if user:
        # 账号密码成功，进入主页面
        return success(data=user.id)
    return error("帐号或密码错误")

'''
@login_required：这是一个装饰器，用于保护视图函数，确保只有登录的用户才能访问该视图。如果用户未经过身份验证（未登录），则装饰器将重定向到登录页面。
def get_user_view(request: HttpRequest):：定义了一个名为get_user_view的视图函数，接收一个名为request的HttpRequest对象，该对象包含了HTTP请求的相关信息。
id_ = request.headers.get("access-token")：从HTTP请求头中获取名为access-token的值，并将其存储在id_变量中。
user = User.objects.filter(id=id_).first()：从数据库中查询User模型对象，以获取与id_匹配的用户，如果找到则将其赋值给user变量。
if user:：如果找到了用户，则执行以下代码块。
return success(data={"name": user.username, "role": [], "isSuperuser": user.is_superuser})：返回一个成功的HTTP响应，并将用户信息以JSON格式作为响应数据返回。在此响应中，用户信息包括用户名、角色和是否是超级用户。
'''
@login_required
def get_user_view(request: HttpRequest):
    id_ = request.headers.get("access-token")
    user = User.objects.filter(id=id_).first()
    if user:
        return success(
            data={"name": user.username, "role": [], "isSuperuser": user.is_superuser}
        )


# 用户注册视图
def signup(request):
    data = simplejson.loads(request.body)
    if not all((data.get("username"), data.get("password"), data.get("password2"))):
        return error("信息不全")
    if data.get("password") != data.get("password2"):
        return error("二次密码不一致")
    if User.objects.filter(username=data.get("username")).exists():
        return error("帐号已存在")
    user = User.objects.create_user(
        username=data.get("username"), password=data.get("password"), is_staff=True
    )  # , is_superuser=True
    # 注册新用户
    user.save()
    return success(data=user.id)


# 工具函数
def to_dict(l):
    def _todict(obj):
        j = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return j

    return [_todict(i) for i in l]
