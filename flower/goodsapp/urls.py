from django.urls import path
from . import views

app_name = 'goodsapp'

urlpatterns = [
    # 首页
    path('', views.index, name='index'),

    path('flowers_data.json', views.flowers_data, name='flowers_data'),
    
    # 商品列表
    path('list/', views.goods_list, name='goods_list'),
    # 商品列表分页
    path('api/', views.goods_list_api, name='goods_list_api'),
    # 商品详情
    path('goods_detail/<int:id>/', views.goods_detail, name='goods_detail'),
    path('flower/<int:id>/', views.flower_detail, name='flower_detail'),

   # 商品评论相关
    path('goods_detail/<int:id>/add_review/', views.add_review, name='add_review'),
    path('goods_detail/<int:id>/reviews/', views.get_goods_reviews, name='get_goods_reviews'),

    # 花漾卡片
    path('cards/', views.get_cards, name='get_cards'),
    path('cards/add/', views.add_card, name='add_card'),
]