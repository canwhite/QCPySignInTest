#view_if.py
from django.http import JsonResponse
from sign.models import Event,Guest
from django.core.exceptions import ValidationError,ObjectDoesNotExist #格式错误,和数据不存在
from django.db.utils import IntegrityError #手机号问题
import time





# 添加发布会接口
def add_event(request):
    eid = request.POST.get('eid','')                 # 发布会id
    name = request.POST.get('name','')               # 发布会标题
    limit = request.POST.get('limit','')             # 限制人数
    status = request.POST.get('status','')           # 状态
    address = request.POST.get('address','')         # 地址
    start_time = request.POST.get('start_time','')   # 发布会时间

    if eid =='' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status':10021,'message':'parameter error'})

    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status':10022,'message':'event id already exists'})

    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status':10023,'message':'event name already exists'})

    if status == '':
        status = 1

    try:
        Event.objects.create(id=eid,name=name,limit=limit,address=address,status=int(status),start_time=start_time)
    except ValidationError:#格式错误
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status':10024,'message':error})

    return JsonResponse({'status':200,'message':'add event success'})
#发布会查询接口

def get_event_list(request):

    eid = request.GET.get('eid','') #发布会id
    name = request.GET.get('name','') #发布会名称

    if eid == '' and name == '':
        return JsonResponse({'status':10021,'message':'parameter error'})

    if eid != '':
        #字典里边嵌入字典
        event = {}
        try:
            result = Event.objects.get(id =eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022,'message':'query result is empty'})
        else:
            #这个是给后边的结果赋值
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time

            return JsonResponse({'status':200,'message':'success','data':event})

    if name != '':
        #python传递数组字典
        datas  = []
        results  = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)

            return JsonResponse({'status':200,'message':'success','data':datas})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})


#添加嘉宾接口
def add_guest(request):
    eid = request.POST.get('eid','')#关联发布会id
    realname = request.POST.get('realname','') #姓名
    phone = request.POST.get('phone','')#手机号
    email = request.POST.get('email','')#邮箱
    #判断参数是否存在
    if eid == '' or realname == '' or phone == '':
        return JsonResponse({'status':10021,'message':'parameter error'})

    #判断是不是链接好了发布会的
    result = Event.objects.filter(id = eid)
    if not result:
        return JsonResponse({'status':10022,'message':'event id null'})


    #看下发布会的状态
    result = Event.objects.get(id = eid).status
    if not result:
        return JsonResponse({'status':10023,'message':'event status is not available'})


    #发布会限制人数
    event_limit = Event.objects.get(id = eid).limit   #发布会限制人数
    #发布会已添加的嘉宾数
    guest_limit = len(Guest.objects.filter(event_id = eid))

    if guest_limit >= event_limit:
        return JsonResponse({'status':'10024','message':'event number is full'})




    #发布会时间
    event_time = Event.objects.get(id = eid).start_time
    #将发布会时间转为字符串，以点分开，取元组第一个,得到点以前的数据
    etime = str(event_time).split('.')[0]

    #将时间字符串转换成指定格式strptime()
    timeArray = time.strptime(etime,'%Y-%m-%d %H:%M:%S')

    #将开始时间转化为指定秒数mktime()
    e_time = int(time.mktime(timeArray))


    #当前时间，这个就是以秒数做单位的
    now_time = str(time.time())

    #去掉后边的小数点部分
    ntime = now_time.split('.')[0]

    #转化成整数
    n_time = int(ntime)


    if n_time >= e_time:
        return JsonResponse({'status':10025,'message':'event has started','ntime':ntime,'e_time':e_time})


    try:
        #将上边的数据都比对完了之后
        Guest.objects.create(realname = realname,phone = int(phone),email = email,sign = 0,event_id = int(eid))
    except IntegrityError:
        return JsonResponse({'status':10026,'message':'the event guest phone number repeat'})


    return JsonResponse({'status':200,'message':'add guest success'})


#嘉宾查询接口
def get_guest_list(request):

    eid = request.GET.get('eid','')#关联发布会id
    phone = request.GET.get('phone','')#嘉宾手机号
    #如果发布会id为空
    if eid == '':
        return JsonResponse({'status':10021,'message':'eid can not be empty'})
    #如果发布会id存在，手机为空,看能不能通过一个参数获取数据
    if eid != '' and phone == '':
        datas = []
        '''模糊查询'''
        results = Guest.objects.filter(event_id = eid)
        #如果列表存在
        if results:
            for r in results:
                guest = {}

                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign

                datas.append(guest)
            return JsonResponse({'status':200,'message':'success','data':datas})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})
    '''如果eid和phone都不为空'''
    if eid != '' and phone !='':
        '''精确查询'''
        guest = {}

        try:
            result = Guest.objects.get(phone = phone,event_id = eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022,'message':'query result is empty'})
        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status':200, 'message':'success', 'data':guest})



def user_sign(request):
    #嘉宾签到接口
    eid = request.POST.get('eid','')#发布会id
    phone = request.POST.get('phone','')#嘉宾手机号
    if eid == '' or phone == '':
        return JsonResponse({'status':10021,'message':'parameter error'})
    #根据发布会id找发布会，找到的发布会时唯一的
    result = Event.objects.filter(id = eid)
    #如果对应的发布会不存在
    if not result:
        return JsonResponse({'status':10022,'message':'event id null'})
    #如果发布会存在再判断状态
    result = Event.objects.filter(id = eid).status
    if not result:
        return JsonResponse({'status':10023,'message':'event status is not available'})


    #开始时间转化为时间戳
    event_time = Event.objects.get(id = eid).start_time
    #将当前时间.前的部分转化成字符串
    etime = str(event_time).split('.')[0]
    #将字符串转化为标准时间
    timeArray = time.strptime(etime,'%Y-%m-%d %H:%M:%S')
    #再将标准时间转化为时间戳
    e_time = int(time.mktime(timeArray))


    #当前时间转化为时间戳
    #获得当前时间,这个时间直接就是时间戳，并转化为字符串
    now_time = str(time.time())
    ntime = now_time.split('.')[0]
    n_time = int(ntime)

    #如果当前时间大于等于发布会开始时间
    if n_time >= e_time:
        return JsonResponse({'status':10024,'message':'event has started'})


    #通过手机号去获取用户,手机号和用户是对应的，如果用户不存在，手机号就不存在
    result = Guest.objects.filter(phone = phone)
    if not result:
        return JsonResponse({'status':10025,'message':'user phone null'})

    #这里可以得到用户
    result = Guest.objects.filter(event_id = eid, phone = phone)
    if not result:
        return JsonResponse({'status':10026,'message':'user did not participate in the conference'})


    result = Guest.objects.filter(event_id = eid,phone = phone).sign
    if result:
        return JsonResponse({'status':10027,'message':'user has sign in'})
    else:
        Guest.objects.filter(event_id = eid,phone = phone).update(sign = '1')
        return JsonResponse({'status':200,'message':'sign success'})





















