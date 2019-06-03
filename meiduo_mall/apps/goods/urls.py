from django.conf.urls import url

from . import views

urlpatterns = [
    # 注册
    url(r'^good$', views.GoodView.as_view(), name="good"),


]