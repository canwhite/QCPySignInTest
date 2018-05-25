"""guest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from sign import views  #导入sign应用views文件
from django.conf.urls import url,include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',views.index),
    url(r'^index/$',views.index),#添加index/路径配置
    url(r'^accounts/login/$',views.index),
    url(r'^login_action/$',views.login_action),#这个是表单提交路径
    url(r'^event_manage/$',views.event_manage),
    url(r'^search_name/$',views.search_name),
    url(r'^guest_manage/$',views.guest_manage),
    url(r'^sign_index/(?P<event_id>[0-9]+)/$',views.sign_index),
    url(r'^sign_index_action/(?P<event_id>[0-9]+)/$',views.sign_index_action),
    url(r'^logout/$',views.logout),
    url(r'^api/',include('sign.urls',namespace = 'sign'))

]
