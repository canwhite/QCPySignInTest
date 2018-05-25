from django.contrib import admin
from sign.models import Event,Guest



# Register your models here.

#希望在admin里显示更多表数据
class  EventAdmin(admin.ModelAdmin):
	"""docstring for  EventAdmin"""
	list_display = ['name','status','start_time','id']
	#搜索栏
	search_fields = ['name']
	#过滤器
	list_filter = ['status']



class GuestAdmin(admin.ModelAdmin):
	"""docstring for GuestAdmin"""
	list_display = ['realname','phone','email','sign','create_time','event']

	#搜索栏
	search_fields = ['realname','phone']
	#过滤器
	list_filter = ['sign']
		







# 用EventAdmin选项，注册Event模块
# 用GuestAdmin选项，注册Guest模块

admin.site.register(Event,EventAdmin)
admin.site.register(Guest,GuestAdmin)


