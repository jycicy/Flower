from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.http import JsonResponse
import re
import time
from django.conf import settings
from .common import mail_helper,string_help  # 发送验证码
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
#地址管理
import json
from django.views.decorators.http import require_http_methods
from .models import Address
from orderapp.models import Order
from django.views.decorators.csrf import csrf_exempt
import json as json_module


User = get_user_model()  # 使用自定义用户模型

# Create your views here.

# 登录
def login_view(request):
    if request.method == 'POST':
        # 检查是否是 AJAX 请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            email = request.POST.get('username')  # 用户实际输入的是邮箱
            password = request.POST.get('password')
            print("账号:", email)
            print("密码:", password)
            next_url = request.POST.get('next', '').strip()  # 添加.strip()去除空格

            try:
                # 临时解决方案：根据 username 查找（因为数据存储错误）
                user_obj = User.objects.get(username=email)
                
                # 验证密码
                password_check = user_obj.check_password(password)
                
                # 验证账户状态
                is_active = user_obj.is_active
                
                # 验证密码和账户状态
                if password_check and is_active:
                    # 直接登录用户（跳过 authenticate）
                    auth_login(request, user_obj)
                    
                    # 确保 next_url 是安全的重定向URL
                    if next_url and is_safe_url(next_url, request.get_host()):
                        return JsonResponse({'success': True, 'redirect_url': next_url})
                    else:
                        return JsonResponse({'success': True, 'redirect_url': '/index/'})  # 默认重定向到首页
                else:
                    return JsonResponse({'success': False, 'message': '用户名或密码错误'})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': '用户名或密码错误'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': '登录过程中发生错误'})
        
        # 非 AJAX 请求的处理（保持原有逻辑）
        else:
            email = request.POST.get('username')  # 用户实际输入的是邮箱
            password = request.POST.get('password')
            next_url = request.POST.get('next', '').strip()  # 添加.strip()去除空格

            try:
                # 临时解决方案：根据 username 查找（因为数据存储错误）
                user_obj = User.objects.get(username=email)
                
                # 验证密码
                password_check = user_obj.check_password(password)
                
                # 验证账户状态
                is_active = user_obj.is_active
                
                # 验证密码和账户状态
                if password_check and is_active:
                    # 直接登录用户（跳过 authenticate）
                    auth_login(request, user_obj)
                    
                    # 确保 next_url 是安全的重定向URL
                    if next_url and is_safe_url(next_url, request.get_host()):
                        return redirect(next_url)
                    else:
                        return redirect('index')  # 默认重定向到首页
                else:
                    messages.error(request, '用户名或密码错误')
            except User.DoesNotExist:
                messages.error(request, '用户名或密码错误')
            except Exception as e:
                messages.error(request, '登录过程中发生错误')
                
            return render(request, 'userapp/login.html', {
                'next': next_url,
                'username': email  # 保留邮箱以便用户修改
            })
    
    # GET 请求处理
    next_url = request.GET.get('next', '')
    return render(request, 'userapp/login.html', {'next': next_url})

    

# 添加安全检查函数
def is_safe_url(url, allowed_host):
    """
    验证重定向URL是否安全
    """
    from urllib.parse import urlparse
    if not url:
        return False
    parsed = urlparse(url)
    return not parsed.netloc or parsed.netloc == allowed_host


# 注册
def register_view(request):
    if request.method == 'POST':
        email_address = request.POST.get('username')  # 实际是邮箱地址
        vcode = request.POST.get('vcode')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # 获取会话中的验证码信息
        session_username = request.session.get('mail')
        session_code = request.session.get('mail_code')
        session_code_time = request.session.get('mail_code_time')

        # 验证邮箱
        if not email_address:
            return JsonResponse({'ok': 0, 'msg': '请输入邮箱'})

        # 验证邮箱与验证码匹配
        if not session_username or session_username != email_address:
            return JsonResponse({'ok': 0, 'msg': '该账户没有获取验证码'})

        # 验证验证码
        if not session_code or session_code != vcode:
            return JsonResponse({'ok': 0, 'msg': '验证码错误'})

        # 验证验证码未过期
        if time.time() > session_code_time + settings.VCODE_EXPIRE:
            return JsonResponse({'ok': 0, 'msg': '验证码失效，请重新获取'})

        # 验证密码
        if not password or not password2:
            return JsonResponse({'ok': 0, 'msg': '密码不能为空!'})

        if password != password2:
            return JsonResponse({'ok': 0, 'msg': '请确保两次密码输入一致!'})

        # 验证邮箱是否已存在（检查 username 字段，因为目前邮箱存储在这里）
        if User.objects.filter(username=email_address).exists():
            return JsonResponse({'ok': 0, 'msg': '该邮箱已被注册!'})

        # 创建用户（使用 create_user，同时设置 username 和 email）
        user = User.objects.create_user(
            username=email_address,           # username 字段存储完整邮箱
            email=email_address,              # email 字段也存储完整邮箱
            password=password
        )
        print(user)
        # 清除会话中的验证码信息
        request.session.pop('mail', None)
        request.session.pop('mail_code', None)
        request.session.pop('mail_code_time', None)

        # 使用绝对路径
        return JsonResponse({'ok': 1, 'msg': '注册成功', 'redirect_url': '/user/login/'})

    return render(request, 'userapp/register.html')
    

# 发送邮件验证码
def send_mail_vcode(request):
    username = request.POST.get('username')

    # 验证邮箱格式
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, username):
        return JsonResponse({'msg': '邮箱格式不正确，请输入有效的邮箱地址'})

    # 获取当前时间
    now_time = time.time()
    mail_code_time = request.session.get('mail_code_time')

    # 检查发送间隔
    # if mail_code_time and now_time < mail_code_time + settings.MAIL_INTEREAL:
    #     return JsonResponse({'msg': f'{settings.MAIL_INTEREAL}秒内，不能重复发送邮件'})

    # 生成验证码并发送邮件
    code = mail_helper.send_vcode(
        settings.MAIL_SMTP_SERVER,
        settings.MAIL_FROM_ADDR,
        settings.MAIL_PASSWORD,
        username
    )
    resp = {'msg': '验证码已发送，请查阅'}

    # 存储验证码和发送时间
    request.session['mail_code'] = code
    request.session['mail'] = username
    request.session['mail_code_time'] = time.time()

    return JsonResponse(resp)


# 登出
def logout_view(request):
    # 调用 logout() 方法登出用户
    logout(request)
    # 登出后重定向到登录页面或首页
    return redirect('index')  # 假设 'login' 是登录页面的 URL 名称


# 用户资料
def profile_view(request):
    if request.method == 'POST':
        # 获取用户输入的昵称
        nickname = request.POST.get('nickname')
        
        # 获取当前登录用户
        user = request.user

        # 更新用户昵称
        if nickname:
            user.nickname = nickname
        
        # 处理头像上传
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            
            # 删除旧头像文件（如果存在）
            if user.avatar:
                if default_storage.exists(user.avatar.name):
                    default_storage.delete(user.avatar.name)
            
            # 保存新头像
            # 生成文件名：使用用户ID和时间戳确保唯一性
            file_extension = os.path.splitext(avatar.name)[1]
            file_name = f"avatars/user_{user.id}_{int(time.time())}{file_extension}"
            
            # 保存文件
            path = default_storage.save(file_name, ContentFile(avatar.read()))
            user.avatar = path

        # 保存用户信息
        user.save()

        # 返回成功消息
        return JsonResponse({'msg': '修改成功'})
        
    else:
        # 如果是 GET 请求，从数据库获取最新的用户信息并渲染个人资料页面
        user = request.user
        # 刷新用户数据以确保获取最新信息
        user.refresh_from_db()

        # 计算订单数量
        orders_pending = Order.objects.filter(user=request.user, status=Order.PENDING).order_by('-created_at')
        orders_paid = Order.objects.filter(user=request.user, status=Order.PAID).order_by('-created_at')
        orders_shipped = Order.objects.filter(user=request.user, status=Order.SHIPPED).order_by('-created_at')
        orders_completed = Order.objects.filter(user=request.user, status=Order.COMPLETED).order_by('-created_at')
        
        orders_pending_count = orders_pending.count()
        orders_paid_count = orders_paid.count()
        orders_shipped_count = orders_shipped.count()
        orders_completed_count = orders_completed.count()

        context = {
            'user': user,
            'orders_pending_count': orders_pending_count,
            'orders_paid_count': orders_paid_count,
            'orders_shipped_count': orders_shipped_count,
            'orders_completed_count': orders_completed_count,
        }

        return render(request, 'userapp/profile.html', context)


# 获取城市数据
def get_city_data(request):
    """
    获取城市数据
    """
    try:
        # 读取城市数据文件
        city_file_path = os.path.join(settings.BASE_DIR, 'api', 'address', 'citys.json')
        with open(city_file_path, 'r', encoding='utf-8') as f:
            city_data = json.load(f)
        return JsonResponse({'provinces': city_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 地址列表
@login_required
def address_list(request):
    """获取用户地址列表"""
    addresses = Address.objects.filter(user=request.user)
    addresses_data = []
    for addr in addresses:
        addresses_data.append({
            'id': addr.id,
            'receiver_name': addr.receiver_name,
            'receiver_phone': addr.receiver_phone,
            'province': addr.province,
            'city': addr.city,
            'district': addr.district,
            'detail_address': addr.detail_address,
            'is_default': addr.is_default
        })
    return JsonResponse({'addresses': addresses_data})



# 添加新地址
@login_required
def add_address(request):
    """添加新地址"""
    if request.method == 'POST':
        data = json.loads(request.body)
        # 如果设置为默认地址，需要先将其他地址设为非默认
        if data.get('is_default'):
            Address.objects.filter(user=request.user).update(is_default=False)
        
        address = Address.objects.create(
            user=request.user,
            receiver_name=data['receiver_name'],
            receiver_phone=data['receiver_phone'],
            province=data['province'],
            city=data['city'],
            district=data['district'],
            detail_address=data['detail_address'],
            is_default=data.get('is_default', False)
        )
        return JsonResponse({'success': True, 'message': '地址添加成功'})



# 更新地址
@login_required
def update_address(request, address_id):
    """更新地址"""
    if request.method == 'POST':
        try:
            address = Address.objects.get(id=address_id, user=request.user)
            data = json.loads(request.body)
            
            # 如果设置为默认地址，需要先将其他地址设为非默认
            if data.get('is_default'):
                Address.objects.filter(user=request.user).update(is_default=False)
            
            address.receiver_name = data['receiver_name']
            address.receiver_phone = data['receiver_phone']
            address.province = data['province']
            address.city = data['city']
            address.district = data['district']
            address.detail_address = data['detail_address']
            address.is_default = data.get('is_default', False)
            address.save()
            
            return JsonResponse({'success': True, 'message': '地址更新成功'})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': '地址不存在'})


# 删除地址
@login_required
def delete_address(request, address_id):
    """删除地址"""
    if request.method == 'POST':
        try:
            address = Address.objects.get(id=address_id, user=request.user)
            address.delete()
            return JsonResponse({'success': True, 'message': '地址删除成功'})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': '地址不存在'})



# 设置默认地址
@login_required
def set_default_address(request, address_id):
    """设置默认地址"""
    if request.method == 'POST':
        # 将用户的所有地址设为非默认
        Address.objects.filter(user=request.user).update(is_default=False)
        
        # 将指定地址设为默认
        try:
            address = Address.objects.get(id=address_id, user=request.user)
            address.is_default = True
            address.save()
            return JsonResponse({'success': True, 'message': '默认地址设置成功'})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': '地址不存在'})