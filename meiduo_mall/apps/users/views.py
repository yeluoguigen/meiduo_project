import json
import re
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.users.models import User, Address
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE

from utils.secret import SecretOauth

# 1.注册页面    功能
class RegisterView(View):

    def get(self,request):
        '''
        提供注册页面
        :param request:
        :return: 注册页面
        '''
        return render(request,'register.html')

    def post(self,request):
        '''
        实现用户注册
        :param request: 请求对象
        :return: 注册结果
        '''
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

    #     判断参数是否齐全
        if not all([username,password,password2,mobile,allow]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码')
        if password != password2:
            return HttpResponseForbidden('两次输入密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号码')
        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议')
    #     校验短信验证码
    #     接受前端的验证码
    #     sms_code = request.POST.get('msg_code')
    # #     校验判空,正则和后台的验证码对比
    #     redis_code_client = get_redis_connection('sms_code')
    #     redis_code = redis_code_client.get('sms_%s'%mobile)
    #     if redis_code is None:
    #         return render(request,'register.html',{'sms_code_errmsg': '无效的短信验证码'})
    #     if redis_code.decode() != sms_code:
    #         return render(request,'register.html',{'sms_code_errmsg': '不正确的短信验证码'})


    #     保存数据
        try:
            user = User.objects.create_user(username=username,password=password,mobile=mobile)
        except Exception as e:
            logger.error(e)
            return render(request,'register.html',{'register_errmsg':'注册失效'})
        login(request,user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username',user.username,max_age=3600*24*14)
        return response

# 2.判断用户名是否重复
class UsernameCountView(View):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code':RETCODE.OK,'errmsg':'ok','count':count})

# 3.判断手机号是否重复
class MobileCountView(View):
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code':RETCODE.OK,'errmsg':'ok','count':count})

# 4登录页
class LoginView(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        if not all([username,password]):
            return HttpResponseForbidden('参数不全')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码')
        user = authenticate(username = username,password = password)
        if user is None:
            return render(request,'login.html' ,{'account_errmsg': '用户名或密码错误'})
        login(request,user)
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        response.set_cookie('username',username,max_age=3600*24*15)
        return response

# 5退出登录
class LogoutView(View):
    def get(self,request):
        logout(request)
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response

# 6用户中心页
class UserInfoView(LoginRequiredMixin,View):
    '''提供个人信息界面'''
    def get(self,request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active':request.user.email_active
        }
        return render(request,'user_center_info.html',context)

# 7.增加邮箱
class EmailView(LoginRequiredMixin, View):
    def put(self, request):

        # 1.接收参数 email
        email = json.loads(request.body.decode()).get('email')

        # 2.校验邮箱 正则

        # 3. 存到该用户的email属性
        try:
            request.user.email = email
            request.user.save()

        except Exception as e:
            return JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '添加邮箱失败'})

        # 发邮件 耗时操作
        from apps.users.utils import generate_verify_email_url
        verify_url = generate_verify_email_url(request.user)
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)

        # 4. 返回前端的数据响应
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})

# 8激活邮箱
class VerifyEmailView(View):
    def get(self,request):
        # 1.接受参数
        token = request.GET.get('token')
        # 2.解密
        token_dict = SecretOauth().loads(token)
        # 3.校验userid  email
        try:
            user = User.objects.get(id=token_dict['user_id'],email=token_dict['email'])
        except Exception as e :
            return HttpResponseForbidden('无效的token')
        # 4.修改email_active
        user.email_active = True
        user.save()
        # 5.重定向到首页
        return redirect(reverse('contents:index'))

# 9.收货地址
class AddressView(LoginRequiredMixin,View):
    def get(self,request):
        addresses = Address.objects.filter(user=request.user,is_deleted=False)
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        context = {
            'default_address_id':request.user.default_address_id,
            'addresses':address_list
        }
        return render(request,'user_center_site.html',context)

#10. 新增地址
class CreateAddressView(LoginRequiredMixin,View):
    def post(self,request):
        # count = Address.objects.filter(user=request.user,is_deleted=False).count()
        count = request.user.addresses.filter(is_deleted=False).count()
        if count >= 20:
            return JsonResponse({'coed':RETCODE.THROTTLINGERR,'errmsg':'超过地址数量上限'})
        # 1.接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 1. 校验参数
        if not all([receiver,province_id,city_id,district_id,place,mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        # 保存地址信息,入库
        try:
            address=Address.objects.create(
                user= request.user,
                title=receiver,
                receiver= receiver,
                province_id=province_id,
                city_id= city_id,
                district_id=district_id,
                mobile = mobile,
                place=place,
                tel=tel,
                email=email,
            )
            # 判断用户是否有默认地址,没有就添加一个
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR,'errmsg':'新增地址失败'})
        # 4.构建前端需要的数据
        address_dict = {
            'id': address.id,
            'title': address.receiver,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
        }
        return JsonResponse({'code':RETCODE.OK,'errmsg':'新增地址成功','address':address_dict})

#11.修改地址
class UpdateAddressView(LoginRequiredMixin,View):
    def put(self,request,address_id):
        #接受参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        #校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        #判断
        try:
            address = Address.objects.get(id=address_id)
            address.user = request.user
            address.title = receiver
            address.receiver = receiver
            address.province_id = province_id
            address.city_id = city_id
            address.district_id = district_id
            address.mobile = mobile
            address.place = place
            address.tel = tel
            address.email = email
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR,'errmsg':'更新地址失败'})
        # 4 .构建前端需要的数据格式
        address = Address.objects.get(id=address_id)
        address_dict = {
            'id': address_id,
            'title': address.receiver,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'mobile': address.mobile,
            'place': address.place,
            'tel': address.tel,
            'email': address.email
        }
        #响应更新地址结果
        return JsonResponse({'code':RETCODE.OK,'errmsg':'更新地址成功','address':address_dict})
        #删除地址
    def delete(self,request,address_id):
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted=True
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR,'errmsg':'删除地址失败'})
        return JsonResponse({'code':RETCODE.OK,'errmsg':'删除地址成功'})

# 12 设置默地址
class DefaultAddressView(LoginRequiredMixin,View):
    def put(self,request,address_id):
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR,'errmsg':'设置默认地址失败'})
        return JsonResponse({'code':RETCODE.OK,'errmsg':'设置默认地址成功'})

#13 修改标题
class UpdateTitleAddressView(LoginRequiredMixin,View):
   def put(self,request,address_id):
        #接受参数
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code':RETCODE.DBERR,'errmsg':'设置地址标题失败'})
        return JsonResponse({'code':RETCODE.OK,'errmsg':'设置地址标题成功'})

#14 修改密码
class ChangePasswordView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'user_center_pass.html')
    def post(self,request):
        #接受参数
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')
        if not all([old_password,new_password,new_password2]):
            return HttpResponseForbidden('缺少必传参数')
        try:
            request.user.check_password(old_password)
        except Exception as e:
            logger.error(e)
            return render(request,'user_center_pass.html',{'origin_pwd_errmsg':'原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return HttpResponseForbidden('密码至少8位')
        if new_password != new_password2:
            return HttpResponseForbidden('两次输得密码不一致')
        # 3 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseForbidden('修改密码失败')
        #退出登录
        logout(request)
        #重定向到登录页
        response = redirect(render('users:login'))
        #清除cookie
        response.delete_cookie('username')
        return response
















