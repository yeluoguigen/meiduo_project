
sp = {
"1":{
"channels":[
{"id":1, "name":"手机", "url":"http://shouji.jd.com/"},
{"id":2, "name":"相机", "url":"http://www.itcast.cn/"}
],
"sub_cats":[
{
"id":38,
"name":"手机通讯",
"sub_cats":[
{"id":115, "name":"手机"},
{"id":116, "name":"游戏手机"}
]
},
{
"id":39,
"name":"手机配件",
"sub_cats":[
{"id":119, "name":"手机壳"},
{"id":120, "name":"贴膜"}
]
}
]
},
"2":{
"channels":[
{"id":1, "name":"电脑", "url":"http://shouji.jd.com/"},
{"id":2, "name":"办公", "url":"http://www.itcast.cn/"}
],
"sub_cats":[
{
"id":38,
"name":"电脑配件",
"sub_cats":[
{"id":115, "name":"键盘"},
{"id":116, "name":"鼠标"}
]
},
{
"id":39,
"name":"办公文具",
"sub_cats":[
{"id":119, "name":"橡皮"},
{"id":120, "name":"桌子"}
]
}
]
},
"3":{
"channels":[
{"id":1, "name":"男装", "url":"http://shouji.jd.com/"},
{"id":2, "name":"女装", "url":"http://www.itcast.cn/"}
],
"sub_cats":[
{
"id":38,
"name":"男士上衣",
"sub_cats":[
{"id":115, "name":"西服"},
{"id":116, "name":"裤子"}
]
},
{
"id":39,
"name":"男士短袖",
"sub_cats":[
{"id":119, "name":"休闲"},
{"id":120, "name":"运动"}
]
}
]
}

}



for i in range(2):
    print(sp['1']['channels'][i]['name'],end='  ')
for j in range(2):
    print(sp['1']['sub_cats'][j]['name'])



