from django.conf.urls import url

from . import views

urlpatterns = [
    # 注册
    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name="qqlogin"),
    url(r'^oauth_callback$', views.QQAuthView.as_view(), name='qqauth'),

]