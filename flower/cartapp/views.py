from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
import json
from .models import Cart, CartItem
from goodsapp.models import Goods

# Create your views here.


@login_required(login_url='userapp:login')
def index(request):
    # 确保正确获取购物车对象
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cartapp/index.html', context)



# 添加商品到购物车
@require_POST
def add_to_cart(request):
    # 检查用户是否已登录
    if not request.user.is_authenticated:
        return HttpResponseForbidden('用户未登录')
    
    try:
        # 解析请求数据
        data = json.loads(request.body)
        goods_id = data.get('goods_id')
        quantity = int(data.get('quantity', 1))
        package = data.get('package', '无礼盒')
        package_price = float(data.get('package_price', 0))
        
        # 获取商品信息
        goods = get_object_or_404(Goods, id=goods_id)
        
        # 获取或创建用户的购物车
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # 检查是否已经存在相同的商品（相同商品和包装）
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=goods,
            package=package,
            defaults={
                'quantity': quantity,
                'package_price': package_price
            }
        )
        
        # 如果商品已存在，则更新数量
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': '商品已成功加入购物车',
            'cart_items_count': cart.items.count()
        })
        
    except Goods.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '商品不存在'
        }, status=404)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': '数据格式错误: ' + str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '系统错误: ' + str(e)
        }, status=500)


# 删除购物车中的商品
@require_POST
@login_required
def delete_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'message': '商品已从购物车中删除'
        })


    except Exception as e:
        return JsonResponse({
            'success': False,
            'messge': '系统错误' + str(e)
        }, status=500)



# 更新购物车中的商品数量
@require_POST
@login_required
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity'))

        # 获取购物车项
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        #cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        # 更新数量
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            
        else:
            cart_item.delete()
           
        return JsonResponse({
            'success': True,
            'message': '更新成功'
        })


    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '系统错误' + str(e)

        }, status=500)

