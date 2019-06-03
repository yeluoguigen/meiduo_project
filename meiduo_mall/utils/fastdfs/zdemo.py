#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from fdfs_client.client import Fdfs_client
client = Fdfs_client('client.conf')
ret = client.upload_by_filename('/home/python/Desktop/1.jpg')
print(ret)
