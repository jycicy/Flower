from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from userapp.models import Address
from .models import Order, OrderItem
from goodsapp.models import Goods
from django.utils import timezone
from django.contrib import messages
from .utils import create_alipay_payment, get_alipay # 导入支付宝支付工具函数

from django.http import HttpResponse


# Create your views here.

@login_required
def index(request):
    # 获取订单ID参数（如果有的话）
    order_id = request.GET.get('order_id')
    order = None
    order_items = []
    
    # 如果有订单ID，获取订单信息和订单项
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            # 获取订单项，包含商品信息
            order_items = OrderItem.objects.filter(order=order).select_related('product')
        except Order.DoesNotExist:
            pass
    
    address = Address.objects.filter(user=request.user)
    address_data = []
    for addr in address:
        address_data.append({
            'id': addr.id,
            'receiver_name': addr.receiver_name,
            'receiver_phone': addr.receiver_phone,
            'province': addr.province,
            'city': addr.city,
            'district': addr.district,
            'detail_address': addr.detail_address,
            'is_default': addr.is_default
        })

    return render(request, 'orderapp/index.html', {
        'address': address_data,
        'order': order,
        'order_items': order_items 
    })



@login_required
def order_create(request):
    if request.method == 'POST':
        try:
            # 解析请求数据
            data = json.loads(request.body)
            
            # 检查是单个商品购买还是购物车结算
            items = data.get('items')
            
            # 创建订单号
            order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}{request.user.id}"
            
            # 获取用户默认地址
            default_address = Address.objects.filter(user=request.user, is_default=True).first()
            if not default_address:
                # 如果没有默认地址，使用第一个地址
                default_address = Address.objects.filter(user=request.user).first()
            
            # 初始化总金额
            total_amount = 0
            
            # 创建订单（状态为待付款，地址信息使用默认地址）
            if default_address:
                order = Order.objects.create(
                    order_number=order_number,
                    user=request.user,
                    receiver_name=default_address.receiver_name,
                    receiver_phone=default_address.receiver_phone,
                    province=default_address.province,
                    city=default_address.city,
                    district=default_address.district,
                    detail_address=default_address.detail_address,
                    total_amount=0,  # 先设置为0，后面计算
                    status=Order.PENDING  # 待付款状态
                )
            else:
                # 如果用户没有任何地址
                order = Order.objects.create(
                    order_number=order_number,
                    user=request.user,
                    receiver_name='',
                    receiver_phone='',
                    province='',
                    city='',
                    district='',
                    detail_address='',
                    total_amount=0,  # 先设置为0，后面计算
                    status=Order.PENDING  # 待付款状态
                )
            
            # 处理购物车结算
            if items:
                # 购物车结算逻辑
                for item_data in items:
                    item_id = item_data.get('item_id')
                    quantity = item_data.get('quantity', 1)
                    package = item_data.get('package', '无礼盒')
                    
                    # 从购物车项中获取商品信息
                    from cartapp.models import CartItem, Cart
                    try:
                        # 先获取用户的购物车
                        user_cart = Cart.objects.get(user=request.user)
                        # 通过购物车和ID查询购物车项
                        cart_item = CartItem.objects.get(id=item_id, cart=user_cart)
                        goods = cart_item.product
                        price = float(goods.price)
                        
                        # 计算包装价格
                        package_price = 0
                        if '¥10' in package:
                            package_price = 10
                        elif '¥29' in package:
                            package_price = 29
                        
                        # 计算单项总金额
                        item_total = quantity * (price + package_price)
                        total_amount += item_total
                        
                        # 创建订单项
                        OrderItem.objects.create(
                            order=order,
                            product=goods,
                            quantity=quantity,
                            price=price,
                            package=package
                        )
                        
                        # 删除购物车中的商品
                        cart_item.delete()
                        
                    except (CartItem.DoesNotExist, Cart.DoesNotExist):
                        # 如果购物车项或购物车不存在，继续处理其他项
                        continue
                        
            else:
                # 单个商品购买逻辑（保持原有逻辑）
                goods_id = data.get('goods_id')
                quantity = data.get('quantity', 1)
                package = data.get('package', '无礼盒')
                package_price = float(data.get('package_price', 0))
                
                # 获取商品对象
                goods = Goods.objects.get(id=goods_id)
                
                # 计算总金额
                total_amount = quantity * (float(goods.price) + package_price)
                
                # 创建订单项
                OrderItem.objects.create(
                    order=order,
                    product=goods,
                    quantity=quantity,
                    price=goods.price,
                    package=package
                )
            
            # 更新订单总金额
            order.total_amount = total_amount
            order.save()
            
            return JsonResponse({
                'success': True, 
                'order_id': order.id,
                'order_number': order.order_number
            })
            
        except Goods.DoesNotExist:
            return JsonResponse({'success': False, 'error': '商品不存在'})
        except Exception as e:
            # 删除已创建的订单（如果出错）
            if 'order' in locals():
                order.delete()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '无效的请求方法'})

# 订单确认
@login_required
def order_confirm(request, order_id):
    """
    订单确认页面 - 用户选择地址并确认订单
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # 确保订单状态是待付款
    if order.status != Order.PENDING:
        messages.error(request, '订单状态不正确')
        return redirect('orderapp:index')
    
    # 获取用户的所有地址
    addresses = Address.objects.filter(user=request.user)
    
    context = {
        'order': order,
        'addresses': addresses
    }
    
    return render(request, 'orderapp/confirm.html', context)


# 更新订单地址信息
@login_required
def order_update_address(request, order_id):
    """
    更新订单地址信息
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            address_id = data.get('address_id')
            
            # 获取订单和地址
            order = get_object_or_404(Order, id=order_id, user=request.user)
            address = get_object_or_404(Address, id=address_id, user=request.user)
            
            # 更新订单地址信息
            order.receiver_name = address.receiver_name
            order.receiver_phone = address.receiver_phone
            order.province = address.province
            order.city = address.city
            order.district = address.district
            order.detail_address = address.detail_address
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': '地址更新成功',
                'full_address': order.get_full_address()
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '无效的请求方法'})


# 配置日志
logger = logging.getLogger(__name__)

# 提交订单跳转付款
@login_required
def order_submit(request):
    """
    提交订单并跳转到支付宝付款页面
    """
    if request.method == 'POST':
        try:
            logger.info("开始处理订单提交请求")
            data = json.loads(request.body)
            order_id = data.get('order_id')
            logger.info(f"订单ID: {order_id}")
            
            # 获取订单
            order = get_object_or_404(Order, id=order_id, user=request.user)
            logger.info(f"订单信息: {order.order_number}, 金额: {order.total_amount}")
            
            # 确保订单状态是待付款
            if order.status != Order.PENDING:
                logger.warning(f"订单状态不正确: {order.status}")
                return JsonResponse({'success': False, 'error': '订单状态不正确'})
            
            # 生成支付宝支付链接
            logger.info("开始生成支付宝支付链接")
            pay_url = create_alipay_payment(order)
            logger.info(f"支付链接生成成功: {pay_url}")
            
            return JsonResponse({
                'success': True, 
                'message': '订单提交成功',
                'pay_url': pay_url,
                'order_id': order.id
            })
            
        except Exception as e:
            logger.error(f"订单提交失败: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'订单提交失败: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': '无效的请求方法'})



# 检查订单支付状态
def check_order_payment_status(order_number):
    """
    检查订单支付状态
    """
    try:
        order = Order.objects.get(order_number=order_number)
        return order.status
    except Order.DoesNotExist:
        return None


# 支付宝同步回调
@csrf_exempt
def alipay_return(request):
    """
    支付宝同步回调 - 用户支付后跳转页面
    """
    logger.info("收到支付宝同步回调请求")
    logger.info(f"完整请求路径: {request.get_full_path()}")
    logger.info(f"GET数据: {dict(request.GET)}")
    logger.info(f"POST数据: {dict(request.POST)}")
    logger.info(f"请求方法: {request.method}")
    
    try:
        # 处理参数
        if request.method == 'GET' and request.GET:
            data = request.GET.dict()
        elif request.method == 'POST' and request.POST:
            data = request.POST.dict()
        else:
            data = {}
            
        signature = data.pop("sign", None)
        
        logger.info(f"提取的签名: {signature}")
        logger.info(f"待验证数据: {data}")
        
        if not signature:
            logger.error("缺少签名参数")
            return render(request, 'orderapp/payment_fail.html', {'error': '缺少签名参数'})
        
        # 验证签名
        alipay = get_alipay()
        success = alipay.verify(data, signature)
        logger.info(f"签名验证结果: {success}")
        
        if success:
            order_number = data.get("out_trade_no")
            logger.info(f"订单号: {order_number}")
            if order_number:
                try:
                    order = Order.objects.get(order_number=order_number)
                    # 对于同步回调，我们主要关心订单是否存在
                    # 支付状态以异步通知为准，但通常用户能访问到这里说明支付成功了
                    return render(request, 'orderapp/payment_success.html', {'order': order})
                except Order.DoesNotExist:
                    logger.error(f"订单不存在: {order_number}")
                    return render(request, 'orderapp/payment_fail.html', {'error': '订单不存在'})
            else:
                logger.error("缺少订单号参数")
                return render(request, 'orderapp/payment_fail.html', {'error': '缺少订单号参数'})
        else:
            logger.error(f"签名验证失败")
            return render(request, 'orderapp/payment_fail.html', {'error': '支付验证失败'})
    except Exception as e:
        logger.error(f"支付宝同步回调处理失败: {e}", exc_info=True)
        return render(request, 'orderapp/payment_fail.html', {'error': f'处理失败: {str(e)}'})


# 支付宝异步回调
@csrf_exempt
def alipay_notify(request):
    """
    支付宝异步回调 - 接收支付结果通知
    """
    logger.info("收到支付宝异步回调请求")
    logger.info(f"POST数据: {request.POST}")
    logger.info(f"GET数据: {request.GET}")
    
    try:
        # 处理POST数据（通常是异步通知）
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            # 处理GET数据（可能是测试）
            data = request.GET.dict()
            
        signature = data.pop("sign", None)
        
        logger.info(f"提取的签名: {signature}")
        logger.info(f"待验证数据: {data}")
        
        if not signature:
            logger.error("缺少签名参数")
            return HttpResponse("fail")
        
        # 验证签名
        alipay = get_alipay()
        success = alipay.verify(data, signature)
        logger.info(f"签名验证结果: {success}")
        
        if success and data.get("trade_status") in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            order_number = data.get("out_trade_no")
            logger.info(f"支付成功，订单号: {order_number}")
            try:
                order = Order.objects.get(order_number=order_number)
                if order.status == Order.PENDING:
                    order.status = Order.PAID
                    order.save()
                    logger.info(f"订单状态更新为已支付: {order.order_number}")
                return HttpResponse("success")
            except Order.DoesNotExist:
                logger.error(f"订单不存在: {order_number}")
                return HttpResponse("fail")
        else:
            logger.error(f"支付失败或状态不正确: {data}")
            return HttpResponse("fail")
    except Exception as e:
        logger.error(f"支付宝异步回调处理失败: {e}", exc_info=True)
        return HttpResponse("fail")


# 调试支付宝回调参数debug
def alipay_debug(request):
    """
    调试支付宝回调参数
    """
    # 获取所有可能的参数
    get_params = dict(request.GET)
    post_params = dict(request.POST)
    body_content = request.body.decode('utf-8') if request.body else ""
    
    context = {
        'get_params': get_params,
        'post_params': post_params,
        'body_content': body_content,
        'headers': dict(request.headers),
        'method': request.method,
        'full_path': request.get_full_path(),
    }
    logger.info(f"支付宝调试信息: {context}")
    return JsonResponse(context)


# 待付款订单pending
@login_required
def pending_payment_orders(request):
    """待付款订单页面"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            
            # 获取订单
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # 确保订单状态是待付款
            if order.status != Order.PENDING:
                return JsonResponse({'success': False, 'error': '订单状态不正确'})
            # 删除订单
            order.delete()
            return JsonResponse({'success': True, 'message': '订单删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
 
        return JsonResponse({'success': False, 'error': '无效的请求方法'})

    else :

        orders = Order.objects.filter(user=request.user, status=Order.PENDING).order_by('-created_at')
        
        return render(request, 'orderapp/order_list.html', {
            'orders': orders,
            'page_title': '待付款订单',
            'status_filter': 'pending'
        })


# 待发货订单paid
@login_required
def pending_shipment_orders(request):
    """待发货订单页面"""
    orders = Order.objects.filter(user=request.user, status=Order.PAID).order_by('-created_at')
    return render(request, 'orderapp/order_list.html', {
        'orders': orders,
        'page_title': '待发货订单',
        'status_filter': 'paid'
    })


# 待收货订单shipped
@login_required
def pending_receipt_orders(request):
    """待收货订单页面"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            
            # 获取订单
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # 确保订单状态是已发货
            if order.status != Order.SHIPPED:
                return JsonResponse({'success': False, 'error': '订单状态不正确'})
            
            # 更新订单状态为已完成
            order.status = Order.COMPLETED
            order.save()
            
            return JsonResponse({
                'success': True, 
                'message': '确认收货成功',
                'order_id': order.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '无效的请求方法'})



    else:
        orders = Order.objects.filter(user=request.user, status=Order.SHIPPED).order_by('-created_at')
        return render(request, 'orderapp/order_list.html', {
            'orders': orders,
            'page_title': '待收货订单',
            'status_filter': 'shipped'
        })


# 已完成订单
@login_required
def completed_orders(request):
    """已完成订单页面"""
    orders = Order.objects.filter(user=request.user, status=Order.COMPLETED).order_by('-created_at')

    print(orders)
    return render(request, 'orderapp/order_list.html', {
        'orders': orders,
        'page_title': '已完成订单',
        'status_filter': 'completed'
    })



