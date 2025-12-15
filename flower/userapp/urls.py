from django.urls import path
from . import views

app_name = 'userapp'
urlpatterns = [
    # api
    path('api/city-data/', views.get_city_data, name='city_data'),
    # 用户登录、注册、注销
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    # 发送验证码
    path('send_mail_vcode/', views.send_mail_vcode, name='send_mail_vcode'),
    # 用户信息
    path('profile/', views.profile_view, name='profile'),
    # 地址管理
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/update/<int:address_id>/', views.update_address, name='update_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/set_default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    # path('change_password/', views.change_password_view, name='change_password'),
]