from django.shortcuts import render
from goodsapp.models import Goods  
from django.core.cache import cache
from django.utils import timezone
import random
import datetime

def get_daily_hot_goods():
    """
    获取每日热门商品，每天0点刷新
    """
    # 生成今天的日期作为缓存键的一部分
    today = timezone.now().date()
    cache_key = f'daily_hot_goods_{today}'
    
    # 尝试从缓存中获取商品
    hot_goods_ids = cache.get(cache_key)
    
    if hot_goods_ids is None:
        # 缓存中没有数据，从数据库获取
        all_active_goods_ids = list(Goods.objects.filter(is_active=True).values_list('id', flat=True))
        
        # 随机选择8个ID
        if len(all_active_goods_ids) > 8:
            hot_goods_ids = random.sample(all_active_goods_ids, 8)
        else:
            hot_goods_ids = all_active_goods_ids
        
        # 计算到明天0点的时间差（秒）
        now = timezone.now()
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        timeout = (tomorrow_midnight - now).total_seconds()
        
        # 将商品ID列表缓存到明天0点
        cache.set(cache_key, hot_goods_ids, timeout=int(timeout))
    
    # 根据ID获取完整的商品对象
    hot_goods = Goods.objects.filter(id__in=hot_goods_ids)
    return hot_goods

def index(request):
    # 获取每日热门商品
    hot_goods = get_daily_hot_goods()


    # 猜你喜欢（每次刷新变化）
    all_active_goods_ids = list(Goods.objects.filter(is_active=True).values_list('id', flat=True))
    if len(all_active_goods_ids) > 8:
        guess_ids = random.sample(all_active_goods_ids, 8)
    else:
        guess_ids = all_active_goods_ids
    
    guess_goods = Goods.objects.filter(id__in=guess_ids)
    
    context = {
        'hot_goods': hot_goods,
        'guess_goods': guess_goods,
    }
    return render(request, 'index.html', context)


def bloomwave(request):
    return render(request, 'bloomwave.html')
def about(request):
    return render(request, 'about.html')

def other(request):
    return render(request, 'other.html')
