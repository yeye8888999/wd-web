import re

from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render
from celery_tasks.tasks import send_active_mail
# Create your views here.
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired

from Dailyfresh import settings
from apps.users.models import User


def register(request):
    """进入注册界面"""
    return render(request,'register.html')

def do_register(request):
    """响应请求"""
    return HttpResponse('注册成功，进入登陆界面')

class RegisterView(View):
    """注册视图"""
    def get(self,request):
        return render(request, 'register.html')

    def post(self,request):

        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')  # 是否勾选用户协议

        # 校验参数完整性
        if not all([username,password,password2,email]):
            return render(request,'register.html',{'message':'参数不完整'})

        if password != password2:
            return render(request,'register.html',{'message':'两次输入密码不一样'})

        if allow != 'on':
            return render(request,'register.html',{'message':'请先同意用户协议'})

        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request,'register.html',{'message':'邮箱格式不正确'})

        # 业务处理：保存注册用户到数据库表
        # create_user 是django提供的方法,
        # 注意：参数先后顺序，会自动对密码进行加密处理
        user = None
        try:
            user = User.objects.create_user(username, email, password)
            # 修改用户的激活状态为未激活
            user.is_active = False
            user.save()
        except IntegrityError:  # 数据完整性错误
            # 判断注册用户是否已经存在
            return render(request, 'register.html', {'errmsg': '用户已存在'})

        # 发送激活邮件
        token = user.generate_active_token()
        # RegisterView.send_active_email(username,email,token)
        # 使用celery调用delay方法异步发送邮件
        send_active_mail.delay(username, email, token)
        # 响应请求
        return HttpResponse("进入登陆界面")

    # todo: 发送激活邮件
    @staticmethod
    def send_active_mail(username,email,token):

        """发送激活邮件"""
        subject = "天天生鲜用户激活"  # 标题, 不能为空，否则报错
        message = ""  # 邮件正文(纯文本)
        from_email = settings.EMAIL_FROM  # 发件人
        recipient_list = [email]  # 接收人, 需要是列表
        # 邮件正文(带html样式)
        html_message = ('<h3>尊敬的%s：感谢注册天天生鲜</h3>'
                        '请点击以下链接激活您的帐号:<br/>'
                        '<a href="http://127.0.0.1:8000/users/active/%s">'
                        'http://127.0.0.1:8000/users/active/%s</a>'
                        ) % (username, token, token)
        send_mail(subject, message, from_email, recipient_list,
                  html_message=html_message)

class ActiveView(View):
    def get(self,request,token:str):
        try:
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)
            dict_data = s.loads(token)
        except SignatureExpired:
            return HttpResponse('激活链接已经失效')

        user_id = dict_data.get('confirm')
        User.objects.filter(id=user_id).update(is_active=True)
        return HttpResponse('激活成功，跳转到登陆界面')

class LoginView(View):
    def get(self,request):
        return render(request,'login.html')

    def post(self,request):
        return HttpResponse('欢迎回来')












