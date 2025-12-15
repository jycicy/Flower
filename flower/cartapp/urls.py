from django.urls import path
from . import views

app_name = 'cartapp'

urlpatterns = [
    # # 首页
    path('', views.index, name='index'),

    #添加到购物车
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),

    # 删除购物车商品
    path('delete/', views.delete_cart_item, name='delete_cart_item'),

    # 修改购物车商品参数
    path('update/', views.update_cart_item, name='update_cart_item'),
    
    # # 商品详情页
    # path('goods/<int:goods_id>/', views.goods_detail, name='goods_detail'),
    
    # # 添加商品到购物车
    # path('add_to_cart/<int:goods_id>/', views.add_to_cart, name='add_to_cart'),
    
    # # 查看购物车
    # path('cart/', views.view_cart, name='view_cart'),
    
    # # 删除购物车中的商品
    # path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
]