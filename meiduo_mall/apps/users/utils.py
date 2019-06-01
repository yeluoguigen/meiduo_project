import re

from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from utils.secret import SecretOauth
from .models import User


# 激活的链接
def generate_verify_email_url(user):
    # 1.userid email
    data_dict = {'user_id':user.id,'email':user.email}
    # 2.加密
    secret_data = SecretOauth().dumps(data_dict)
    # 3.拼接连接
    verify_url = settings.EMAIL_ACTIVE_URL + '?token=' + secret_data
    # 4. 返回去
    return verify_url




# 封装 校验多用户名的方法
def get_user_by_account(account):
    '''
    根据account查询用户
    :param account: 用户名或手机号
    :return: user
    '''
    try:
        if re.match('^1[3-9]\d{9}$', account):
#             手机号登录
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

# 自定义用户认证后后端
class UsernameMobileAuthBackend(ModelBackend):
    # 重写弗雷的认证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        重写认证方法,实行多帐号登录
        :param request:
        :param username: 用户名
        :param password: 密码
        :param kwargs:
        :return:
        '''
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user




