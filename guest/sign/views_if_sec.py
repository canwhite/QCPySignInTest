#views_if_sec.py
from django.contrib import auth as django_auth
import hashlib
from django.http import JsonResponse
from sign.models import Event,Guest
from django.core.exceptions import ValidationError,ObjectDoesNotExist #格式错误,和数据不存在
from django.db.utils import IntegrityError #手机号问题
import time

#AES算法引入表头
from Crypto.Cipher import AES
import base64
import json

#=========AES 解密密算法 ======================
BS = 16
#upad匿名函数对字符串的长度还原
unpad = lambda s: s[0:-ord(s[-1])]

#base64解密
def decryptBase64(src):
    return base64.urlsafe_b64decode(src)

#AES解密
'''解析aes密文'''
def decryptAES(src,key):

    #传过来的数据先解开第一层
    src = decryptBase64(src)
    iv = b'1172311105789011'
    #key是两边约定好的
    #生命解密对象，这个时候是需要key值的
    cryptor = AES.new(key,AES.MODE_CBC,iv)
    text = cryptor.decrypt(src).decode()
    #还原字符串长度
    return unpad(text)


'''请求数据和解密'''
def aes_encryption(request):
    app_key = 'W7v4D60fds2Cmk2U'
    if request.method == 'POST':
        data = request.POST.get('data','')

    #解密
    decode = decryptAES(data,app_key)
    #转化为字典将解密后字符串通过json.loads()方法转化成字典，并将该字典做为 aes_encryption()函数的返回值。
    dict_data = json.loads(decode)
    return dict_data



#用户认证
def  user_auth(request):
    #request.META 是一个 Python 字典，包含了所有本次 HTTP 请求的 Header 信息，比如用户认证、IP 地址和用户 Agent(通常是浏览器的名称和版本号)等。
    #HTTP_AUTHORIZATION(认证)用于获取同名内容
    #得到的数据 Basic YWRtaW46YWWRtaW4xMjMONTY=
    get_http_auth = request.META.get('HTTP_AUTHORIZATION',b'')
    #通过 split()方法将其拆分成 list。拆分后的数据是这样的:['Basic', 'YWRtaW46YWRtaW4xMjM0NTY=']
    auth = get_http_auth.split()
    try:
        #取出 list 中的加密串，通过 base64 对加密串进行解码。得到的数据是:('admin', ':', 'admin123456')
        auth_parts = base64.b64decode(auth[1]).decode('iso-8859-1').partition(':')
    except IndexError:
        return "null"
    userid,password = auth_parts[0],auth_parts[2]
    user = django_auth.authenticate(username = userid,password = password)
    if user is not None and user.is_active:
        django_auth.login(request,user)
        return "success"
    else:
        return "fail"



#用户签名+时间戳

def user_sign(request):


    client_time = request.POST.get('time','')
    client_sign = request.POST.get('sign','')


    #post方法是往服务器放东西的,get是从服务器取东西的，但也可传递少量参数
    #参数不存在的情况
    if client_time == '' or client_sign == '':
        return 'sign null'

    #服务器时间
    now_time = time.time() #时间戳
    #获取拆分数组小数点前的数据
    server_time = str(now_time).split('.')[0]
    #获取时间差
    time_difference = int(server_time) - int(client_time)
    if time_difference >= 60:#看来时间戳是到秒一级的
        return 'timeout'

    #签名检查
    md5 = hashlib.md5()
    sign_str = client_time +'&Guest-Bugmaster'
    #utf-8编码
    sign_bytes_utf8 = sign_str.encode(encoding = 'utf-8')
    #把用utf-8编码过的数据，加载到md5对象上
    md5.update(sign_bytes_utf8)
    #本地得到一个sign和客户端传过来的东西做对比
    server_sign = md5.hexdigest()

    if server_sign != client_sign:
        return "sign error"
    else:
        return "sign right"





#发布会查询接口

def get_event_list(request):

    #调用认证函数
    auth_result = user_auth(request)
    #本类做些操作
    if auth_result == "null":
        return JsonResponse({'status':10011,'message':'user auth null'})
    if auth_result == "fail":
        return JsonResponse({'status':10012,'message':'user auth fail'})



    # #最原始的时候的操作
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



# 添加发布会接口
def add_event(request):


    #调用签名函数
    sign_result = user_sign(request)
    if sign_result == 'sign null':
        return JsonResponse({'status':10011,'message':'user sign null'})
    elif sign_result == 'timeout':
        return JsonResponse({'status':10012,'message':'user sign timeout'})
    elif sign_result == 'sign error':
        return JsonResponse({'status':10013,'message':'user sign error'})


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


def get_guest_list(request):

    #AES算法部分
    dict_data = aes_encryption(request)
    eid = dict_data['eid']
    name = dict_data['phone']

    if eid == '':
        return JsonResponse({'status':10021,'message':'eid cannot be empty'})

    #如果手机号为空，进行模糊查询
    if eid != '' and phone == '':
        #根据数据库数据生成数组字典
        datas = []
        results = Guest.objects.filter(event_id = eid)
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

    #如果id和手机号都不为空，这个人就是确定的
    if eid != '' and phone != '':

        guest = {}
        try:
            result = Guest.objects.get(phone = phone,event_id = eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022,'message':'query result is empty'})
        else:
            guest['realname'] = result.realname
            guest['email'] = result.email
            guest['phone'] = result.phone
            guest['sign'] = result.sign
            return JsonResponse({'status':200,'message':'success','data':guest})