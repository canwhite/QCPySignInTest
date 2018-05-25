from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
#把数据和视图联系到一起
from sign.models import Event,Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




# Create your views here.
def index(request):
	# return HttpResponse("hello django!")
	return render(request,"index.html")



def login_action(request):
	if request.method == 'POST':
		username = request.POST.get('username','')
		password = request.POST.get('password','')
		#这里判断一下账号和密码
		user = auth.authenticate(username = username,password = password)
		if user is not None:
			auth.login(request,user) #登陆

			response =  HttpResponseRedirect('/event_manage/')
			#添加浏览器cookie，上传到服务器
			#response.set_cookie('user',username,3600)
			request.session['user'] = username  #将session信息记录到浏览器
			return response

		else:
			return render(request,'index.html',{'error':'username or password error'})


@login_required
def event_manage(request):

	#读取浏览器cookie，从服务器下载
	#得到数据
	event_list = Event.objects.all()
	#username = request.COOKIES.get('user',"")
	username = request.session.get('user','')
	return render(request,"event_manage.html",{"user":username,"events":event_list})



#发布会名称搜索
@login_required
def search_name(request):
	username = request.session.get('user','')
	#获取写进text的name字段
	search_name = request.GET.get("name","")
	#通过name字段得到搜索出来的数据
	event_list = Event.objects.filter(name__contains = search_name)
	return render(request,'event_manage.html',{'user':username,'events':event_list})

	

# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()         # 获取Guest全部数据对象
    paginator = Paginator(guest_list, 2)     # 把查询出来的所有嘉宾列表guest_list放到Paginator类中，划分每页显示2条数据
    page = request.GET.get('page')           # 通过GET请求得到当前要现实第几页的数据
    try:
        contacts = paginator.page(page)      # 获取第page页的数据
    except PageNotAnInteger:
        contacts = paginator.page(1)         # 如果page不是整数，取第一页面数据
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)        # 如果page不在范围内，取最后一页面数据
    return render(request, "guest_manage.html", {"user": username, "guests": contacts})        # 将得到的某一页数据返回至嘉宾管理页面上




#签到页面
@login_required
def sign_index(request,event_id):

	event = get_object_or_404(Event,id = event_id)
	return render(request,'sign_index.html',{'event':event})
	

#签到动作

@login_required

def sign_index_action(request,event_id):


	event = get_object_or_404(Event,id = event_id)
	phone = request.POST.get('phone','')
	print(phone)

	#先判断用户的手机号是否存在
	result = Guest.objects.filter(phone = phone)
	if not result:
		return render(request,'sign_index.html',{'event':event,'hint':'event id or phone error.'})

	#主要是通过id判断人是否存在
	result = Guest.objects.get(phone = phone,event_id = event_id)
	if not result:
		return render(request,'sign_index.html',{'event':event,'hint':'event id or phone error'})


	#判断是否已经登陆

	result = Guest.objects.get(phone = phone,event_id = event_id)
	#如果已经登陆了
	if result.sign:
		return render(request,'sign_index.html',{'event':event,'hint':'user has sign in.'})
	else:
		#如果还没有登录，更新登录状态
		Guest.objects.filter(phone = phone,event_id = event_id).update(sign = '1')
		return render(request,'sign_index.html',{'event':event,'hint':'sign in success!','guest':result})


#退出登录
@login_required
def logout(request):
	#退出登录
	auth.logout(request)
	response = HttpResponseRedirect('/index/')
	return response

	
	
















	



