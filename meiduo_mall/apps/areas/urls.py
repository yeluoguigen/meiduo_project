from django.conf.urls import url

from apps.areas import views

urlpatterns = [
    # 注册
    url(r'^areas/$', views.AreasView.as_view(), name="area"),


]