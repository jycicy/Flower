# flower/admin_api/urls.py（新建，API 子路由）
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoodsAdminViewSet, OrderAdminViewSet
from . import views

# 路由注册器：自动生成增删改查 API 路径
router = DefaultRouter()
router.register(r'goods', GoodsAdminViewSet)  # 商品管理 API：/api/admin/goods/
router.register(r'orders', OrderAdminViewSet)  # 订单管理 API：/api/admin/orders/

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]