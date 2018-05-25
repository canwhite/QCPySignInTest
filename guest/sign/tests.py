from django.test import TestCase
# Create your tests here.
from sign.models import Event,Guest
#导入client
from django.test import Client
from django.contrib.auth.models import User
from datetime import datetime
import requests





class ModelTest(TestCase):
	"""docstring for ModelTest"""
	#初始化数据
	def setUp(self):
		Event.objects.create(id = 1,name = 'oneplus 3 event', status = True,limit = 2000,address = "shenzhen",start_time = '2016-08-31 02:18:22')
		Guest.objects.create(id = 1,event_id = 1,realname = 'alen',phone = '13633715705',email = 'alen@mail.com',sign = False)


	def test_event_models(self):
		result = Event.objects.get(name = 'oneplus 3 event')
		#判断相等
		self.assertEqual(result.address,"shenzhen")
		#判断是否有效
		self.assertTrue(result.status)

	def test_guest_models(self):

		result = Guest.objects.get(phone = '13633715705')
		self.assertEqual(result.realname,'alen')
		self.assertFalse(result.sign)


'''编写登陆用的测试用例'''
class IndexPageTest(TestCase):

	def test_index_page_renders_index_template(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'index.html')



'''编写登录动作的测试用例'''
class LoginActionTest(TestCase):
	"""初始化数据"""
	def setUp(self):
		User.objects.create_user('admin','admin@mail.com','admin123456')
		#这个是测试里边的一个类，用于请求数据做对比
		self.c = Client()
	def test_login_action_username_password_null(self):
		'''用户密码为空'''
		test_data = {'username':'','password':''}
		#用空的用户和密码来请求结果
		response = self.c.post('/login_action/',data = test_data)
		self.assertEqual(response.status_code,200)
		#assertIn()断言在返回的HTML中包含错误提示
		self.assertIn(b'username or password eror!',response.content )
	def test_login_action_username_password_error():
		'''用户名，密码错误'''
		#这个是请求参数
		test_data = {'username':'abc','password':'123'}
		#路由地址和参数一起发出请求
		response = self.c.post('/login_action/',data = test_data)
		self.assertEqual(response.status_code,200)
		#断言在HTML中包含错误提示
		self.assertIn(b'username or password error!',response.content)

	def test_login_action_success(self):
		'''登录成功'''
		test_data = {'username':'admin','password':'admin123456'}
		response = self.c.post('login_action',data = test_data)
		self.assertEqual(response.status_code,302)






























