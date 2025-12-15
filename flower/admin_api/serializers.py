# admin_api/serializers.py
from rest_framework import serializers
from goodsapp.models import Goods
from orderapp.models import Order

class GoodsSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    class Meta:
        model = Goods
        fields = '__all__'  # 或者指定具体字段，例如 ['id', 'name', 'price', 'description']

class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    class Meta:
        model = Order
        fields = '__all__'  # 或者指定具体字段