from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class GoodView(View):
   def get(self):
       return HttpResponse('测试商品应用流程')
