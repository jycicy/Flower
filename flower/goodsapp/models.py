import json
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.

class Category(models.Model):
    cname = models.CharField(verbose_name='类别名称', max_length=50)
    slug = models.SlugField(verbose_name='类别网址', max_length=50, unique=True)
    
    class Meta:
        db_table = 'category'
        verbose_name = '类别'
        verbose_name_plural = '类别'

    def __str__(self):
        return self.cname

    def __unicode__(self):
        return u'<Category: %s>'% self.cname

# 商品
class Goods(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="商品类别")
    title = models.CharField(max_length=200, verbose_name="商品标题")
    link = models.URLField(verbose_name="商品链接")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    stock = models.IntegerField(verbose_name="库存", default=100)
    image_url = models.URLField(verbose_name="图片链接")
    description = models.TextField(verbose_name="商品描述", blank=True)
    crawl_time = models.DateTimeField(verbose_name="上架时间", auto_now_add=True)
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    is_active = models.BooleanField(verbose_name="是否激活", default=True)
    
    class Meta:
        db_table = 'goods'
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-crawl_time']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('goodsapp:goods_detail', args=[str(self.id)])


class Flower(models.Model):
    """花卉商品模型 - 只包含必需字段"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name="商品标题")
    price = models.CharField(max_length=20, verbose_name="价格")
    thumbnails = models.JSONField(default=list, verbose_name="缩略图")
    description = models.TextField(verbose_name="商品描述")
    materials = models.TextField(verbose_name="花材信息")
    packaging = models.TextField(verbose_name="包装信息")
    scenarios = models.TextField(verbose_name="适用场景")
    meaning = models.TextField(verbose_name="花语")
    crawl_time = models.DateTimeField(verbose_name="爬取时间")
    list_title = models.CharField(max_length=300, verbose_name="列表标题")
    
    class Meta:
        db_table = 'flowers'
        verbose_name = '花卉商品'
        verbose_name_plural = '花卉商品'
    
    def __str__(self):
        return self.title


class Review(models.Model):
    STAR_CHOICES = [
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    ]
    
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=STAR_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 移除 unique_together 约束，允许同一用户多次评价
    
    def __str__(self):
        return f"{self.user.username} - {self.goods.title} - {self.rating}星"


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(verbose_name="卡片内容")
    color = models.CharField(max_length=20, verbose_name="背景颜色")
    border_color = models.CharField(max_length=20, verbose_name="边框颜色")
    x = models.FloatField(verbose_name="X坐标")
    y = models.FloatField(verbose_name="Y坐标")
    dx = models.FloatField(verbose_name="X方向速度")
    dy = models.FloatField(verbose_name="Y方向速度")
    width = models.FloatField(verbose_name="宽度")
    height = models.FloatField(verbose_name="高度")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name="创建用户")
    
    class Meta:
        db_table = 'cards'
        verbose_name = '漂流卡片'
        verbose_name_plural = '漂流卡片'
    
    def __str__(self):
        return f"Card: {self.text[:20]}..."
