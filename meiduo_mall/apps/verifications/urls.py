from django.conf.urls import url
from . import views


urlpatterns = [
    # 注册
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view(), name="img_code"),

    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),

]