from django.db import models
from userapp.models import *
from django.conf import settings
from goodsapp.models import Goods

# Create your models here.


class Order(models.Model):
    """订单模型"""
    
    # 订单状态
    PENDING = 'pending'
    PAID = 'paid'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, '待付款'),
        (PAID, '待发货'),
        (SHIPPED, '已发货'),# 待收货
        (DELIVERED, '已送达'),
        (COMPLETED, '已完成'),
        (CANCELLED, '已取消'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name='订单号')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    
    # 收货信息（完整地址）
    receiver_name = models.CharField(max_length=50, verbose_name='收货人')
    receiver_phone = models.CharField(max_length=20, verbose_name='联系电话')
    province = models.CharField(max_length=50, verbose_name='省份')
    city = models.CharField(max_length=50, verbose_name='城市')
    district = models.CharField(max_length=50, verbose_name='区县')
    detail_address = models.CharField(max_length=200, verbose_name='详细地址')
    
    # 金额信息
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')
    
    # 状态和时间
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'订单 {self.order_number}'
    
    def get_full_address(self):
        """获取完整地址"""
        return f"{self.province}{self.city}{self.district}{self.detail_address}"





class OrderItem(models.Model):
    """订单商品项"""
    
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 商品单价
    package = models.CharField(max_length=100, blank=True)  # 包装选项
    
    def get_total_price(self):
        return self.quantity * self.price
    
    def __str__(self):
        return f'{self.product.title} x {self.quantity}'

    
