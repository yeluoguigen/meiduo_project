from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.core.cache import cache
from apps.areas.models import Area
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE
#三级联动
class AreasView(View):
    def get(self,request):
        # 1.接受外界传入的area_id
        area_id = request.GET.get('area_id')
        #如果area_id没有就是省份
        if not area_id:
            province_list = cache.get('province_list')
            if not province_list:
                print('缓存失效了')
                try:
                    provinces = Area.objects.filter(parent__isnull=True)
                    province_list = []
                    for pro in provinces:
                        province_list.append({'id':pro.id,'name':pro.name})
                        # province_list = ({'id':pro.id,'name':pro.name}for pro in provinces)
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({'code':RETCODE.DBERR,'errmsg':'获取失败'})
                cache.set('province_list',province_list,10*60)
            return JsonResponse({'code':RETCODE.OK,'errmsg':'OK','province_list':province_list})
        else:
            sub_data = cache.get('sub_'+ area_id)
            if not sub_data:
                parent_model = Area.objects.get(id=area_id)
                subs = parent_model.subs.all()
                subs_list = []
                for sub in subs:
                    subs_list.append(({'id':sub.id,'name':sub.name}))
                sub_data = {
                    'id':parent_model.id,
                    'name':parent_model.name,
                    'subs': subs_list

                }
                cache.set('sub_'+area_id,sub_data,10*60)
            return JsonResponse({'code':RETCODE.OK,'errmsg':'OK','sub_data':sub_data})























# class AreasView(View):
#     def get(self,request):
#
#     #1.接收外界传入的area_id
#         area_id= request.GET.get('area_id')
#     #如果area_id 没有就是省份
#         if not area_id:
#             try:
#                 provinces = Area.objects.filter(parent__isnull=True)
#                 #组合前端需要的数据格式
#                 province_list= []
#                 for pro in provinces:
#                     province_list.append({'id':pro.id,'name':pro.name})
#             except Exception as e:
#                 return JsonResponse({'code':RETCODE.DBERR,'errmsg':'获取失败'})
#             return JsonResponse({'code':RETCODE.OK,'errmsg':'ok','province_list':province_list})
#
#         else:
#             #如果area_id有就是市 或者县区
#             subs = Area.objects.filter(parent_id = area_id)
#             subs_list = []
#             for sub in subs:
#                 subs_list.append({'id':sub.id,'name':sub.name})
#             sub_data = {
#                 'subs':subs_list
#             }
#             return JsonResponse({'code':RETCODE.OK,'errmsg':'OK','sub_data':sub_data})