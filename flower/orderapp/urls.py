from django.urls import path
from . import views

app_name = 'orderapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.order_create, name='order_create'),
    path('confirm/', views.order_confirm, name='order_confirm'),
    path('submit/', views.order_submit, name='order_submit'),
    path('return/', views.alipay_return, name='alipay_return'),
    path('notify/', views.alipay_notify, name='alipay_notify'),
    path('update_address/<int:order_id>/', views.order_update_address, name='order_update_address'),

    # 订单状态分类页面
    path('pending/', views.pending_payment_orders, name='pending_payment'),  # 待付款
    path('paid/', views.pending_shipment_orders, name='pending_shipment'),   # 待发货
    path('shipped/', views.pending_receipt_orders, name='pending_receipt'),  # 待收货
    path('completed/', views.completed_orders, name='completed'),            # 已完成
    # path('', views.order_create, name='order_create'),
    # path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    # path('order/<int:order_id>/pay/', views.order_pay, name='order_pay'),
    # path('order/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    # path('test_alipay/', views.test_alipay, name='test_alipay'),
    path('debug/', views.alipay_debug, name='alipay_debug'),
]