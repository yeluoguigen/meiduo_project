import re
from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection
from apps.oauth.models import OAuthQQUser

from apps.users.models import User
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE
# 判断openid是否绑定了
from utils.secret import SecretOauth

# 判断openid是否绑定
def is_bind_openid(request,openid):
    try:
        oauth_user = OAuthQQUser.objects.get(openid=openid)
    except Exception as e:
        logger.error(e)
        # 没有绑定,重定向到绑定页面
        secret_openid = SecretOauth().dumps({'openid':openid})
        context = {
            'openid':secret_openid

        }

        return render(request,'oauth_callback.html',context)
    else:
        # 绑定了 ,保持登录状态,重定向到首页,设置cookie username
        qq_user = oauth_user.user
        login(request,qq_user)
        #         响应结果
        next = request.GET.get('state')
        print(next)

        response = redirect(next)
        # response = redirect(reverse('contents:index'))
        response.set_cookie('username',qq_user.username,max_age=3600*24*14)
        return response

# 2回调网址
class QQAuthView(View):
    def get(self,request):
        # 1获取code
        code = request.GET.get('code')

        if not code:
            return HttpResponseForbidden('缺少code')
        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state='')
        try:
    #         2使用code获取token
            token = oauth.get_access_token(code)
    #         3 使用token 获取openid'
            openid = oauth.get_open_id(token)
        except Exception as e:
            logger.error(e)
            return HttpResponseForbidden('OAuth2.0认证失败')
        else:
        #    4判断openid是否绑定了帐号
            response = is_bind_openid(request,openid)
            return response
    def post(self,request):
        # 1.接受参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code = request.POST.get('sms_code')
        openid=request.POST.get('openid')
#         2.校验--判空--正则--短信验证码
        if not all([mobile,pwd,sms_code]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return HttpResponseForbidden('请输入8-20位的密码')
#         判断短信验证码是一致
#         redis_code_client = get_redis_connection('sms_code')
#         redis_code = redis_code_client.get('sms_%s'%mobile)
#         if redis_code is None:
#             return render(request,'register.html',{'sms_code_errmsg': '无效的短信验证码'})
#         if redis_code.decode() != sms_code:
#             return render(request,'register.html',{'sms_code_errmsg': '不正确的短信验证码'})

        # 3解密--openid校验
        openid = SecretOauth().loads(openid).get('openid')

        if not openid:
            return render(request,'oauth_callback.html', {'openid_errmsg': '无效的openid'})
#         4判断用户是否存在,存在user, 不存在新建user
        try:
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            # 不存在,新建user
            user = User.objects.create(username=mobile,password=pwd,mobile=mobile)
        else:
        # 密码不正确
            if not user.check_password(pwd):
                return render(request,'oauth_callback.html',{'account_errmsg': '用户名或密码错误'})
#             5.user绑定openid
        try:
            OAuthQQUser.objects.create(openid=openid,user=user)
        except Exception as e:
            return render(request,'oauth_callback.html',{'qq_login_errmsg': 'QQ登录失败'})
#         6保持登录状态--重定向到首页---setcookie  username
        login(request,user)
        next = request.GET.get('state')
        response = redirect(next)
        response.set_cookie('username',user.username,max_age=24*14*3600)
        return response

# 1获取qq登录url
class QQAuthURLView(View):
    def get(self,request):
        next = request.GET.get('next')
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next


        )
#         获取qq登录网址
        login_url = oauth.get_qq_url()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


