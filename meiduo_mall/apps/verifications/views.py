# 第一遍
import random

from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha.captcha import captcha
from meiduo_mall.settings.dev import logger



class ImageCodeView(View):
    def get(self,request,uuid):
        '''

        :param request: 请求对象
        :param uuid: 唯一表示图形验证码所属于的用户
        :return: image/jpg
        '''
        text,image = captcha.generate_captcha()
        redis_client = get_redis_connection('verify_image_code')
        redis_client.setex('img_%s'%uuid,300, text)
        return HttpResponse(image,content_type='image/jpeg')


class SMSCodeView(View):
    def get(self,request,mobile):
        '''

        :param request:
        :param mobile:
        :return: JSON
        '''
        # uuid = request.GET.get('image_code_id')
        # image_code = request.GET.get('image_code')
        # try:
        #     img_redis_client = get_redis_connection('verify_image_code')
        #     redis_img_code = img_redis_client.get('img_%s'%uuid)
        #
        #     if not redis_img_code:
        #         return JsonResponse({'code':4001,'errmsg':'图形验证码失效了'})
        #     if redis_img_code.decode().lower() != image_code.lower():
        #         return JsonResponse({'code':4001,'errmsg':'图形验证码错误'})

        #     img_redis_client.delete('img_%s'%uuid)
        # except Exception as e:
        #     logger.error(e)
            # 避免频繁发短信
        # sms_redis_client = get_redis_connection('sms_code')
            # 取出redis保存发短信的标识
        # send_flag = sms_redis_client.get('send_flag_%s' % mobile)
        # if  send_flag:
        #     return JsonResponse({'code':'4002','errmsg':'发送短信太频繁了'})




        sms_code = '%06d' %random.randint(0,999999)


        try:
            sms_redis_client = get_redis_connection('sms_code')
            p1 = sms_redis_client.pipeline()
            p1.setex('sms_%s' % mobile,300,sms_code)
            p1.setex('send_flag_%s'% mobile,300,1)
            p1.execute()

        except Exception as e:
            logger.error(e)


            # 荣联云发短信
        # CCP().send_template_sms('13914070562',[sms_code,5],1)
        print(sms_code)
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code)
        return JsonResponse({'code':'0','errmsg':'发送短信成功'})





























