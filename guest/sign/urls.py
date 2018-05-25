#url.py
from django.conf.urls import url
from sign import views_if,views_if_sec

urlpatterns = [
	#添加事件
	url(r'^add_event/',views_if.add_event,name = 'add_event'),
	#添加嘉宾
	url(r'^add_guest/',views_if.add_guest,name = 'add_guest'),
	#获取事件列表
	url(r'^get_event_list/',views_if.get_event_list,name = 'get_event_list'),
	#获取嘉宾列表
	url(r'^get_guest_list/',views_if.get_guest_list,name = 'get_guest_list'),
	#人员登录
	url(r'^user_sign/',views_if.user_sign,name = 'user_sign'),

	# 添加了auth认证
	url(r'^sec_get_event_list/', views_if_sec.get_event_list,name='get_event_list'),
	#添加了数字签名
	url(r'sec_add_event/',views_if_sec.add_event,name = 'add_event'),
	#添加aes解密
	url(r'sec_get_guest_list/',views_if_sec.get_guest_list,name = 'get_guest_list'),


]
