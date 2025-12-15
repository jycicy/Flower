"""
URL configuration for flower project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    #后台
    path("admin/", admin.site.urls),
    # 后台 API 根路由：所有 Vue 后台请求都走这个路径
    path('api/admin/', include('admin_api.urls')),
    # DRF 调试登录界面（方便测试 API，可选）
    path('api-auth/', include('rest_framework.urls')),

    #商品模块API - 使用更简洁的路径
    path('api/goods/', include('goodsapp.urls', namespace='api_goods')),

    #前台
    # 首页
    path('index/', views.index, name = 'index'),
    # 花漾
    path('bloomwave/', views.bloomwave, name = 'bloomwave'),
    # 关于我们
    path('about/', views.about, name = 'about'),
    # 其他
    path('other/', views.other, name = 'other'),

    #搜索模块
    path('search/', include('searchapp.urls', namespace='search')),
    #用户模块
    path('user/', include('userapp.urls')),
    #商品模块
    path('goods/', include('goodsapp.urls')),
    #购物车模块
    path('cart/', include('cartapp.urls')),
    #订单模块
    path('order/', include('orderapp.urls')),
    #评论模块

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)