from django.conf.urls import url

from apps.users import views

urlpatterns = [
    # 1.注册页面
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 2.判断用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view(), name='count'),
    # 3. 判断手机号是否重
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view(), name='mobile'),
    # 4. 登录页面
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 5.退出
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # 6.用户中心
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    # 7.增加 邮箱
    url(r'^emails/$', views.EmailView.as_view(), name='email'),
    # 8. 激活邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view(), name='verifyemail'),
    # 9.收货地址
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
    # 10. 新增地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name='createaddress'),

    #11 修改地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateAddressView.as_view(), name='updateaddress'),

    #12 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name="defaultaddress"),

    #13 修改标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(), name="defaultaddress"),

    #14 修改密码
    url(r'^password/$', views.ChangePasswordView.as_view(), name="password"),

]