from django.db import models
# django 全套的认证 user  1.自动生成 2. 自动加密密码 3. 自动校验
# 想使用 django自带的User 自定义
# 1.导包
from django.contrib.auth.models import AbstractUser
from utils.models import BaseModel

# 2.继承
class User(AbstractUser):
    # 新增 手机号属性
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    # 新增邮箱激活
    email_active = models.BooleanField(default=False,verbose_name='邮箱验证状态')
    # 新增默认地址字段
    default_address = models.ForeignKey('Address',related_name='users',null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

#3 用户地址模型
class Address(BaseModel):
    # 用户地址
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses',
                                 verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses',
                                 verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']