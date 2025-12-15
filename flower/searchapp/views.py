from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from goodsapp.models import Goods
from django.contrib.auth.decorators import login_required


# 搜索结果页面
@login_required(login_url='userapp:login')
def search_view(request):
    """
    搜索结果页面
    """
    keyword = request.GET.get('keyword', '').strip()
    products = None  # 初始化为None而不是空列表
    
    if keyword:
        # 根据实际模型字段进行搜索（使用title而不是name）
        products = Goods.objects.filter(
            Q(title__icontains=keyword) | 
            Q(description__icontains=keyword)
        )
    else:
        # 如果没有关键词，返回空的查询集
        products = Goods.objects.none()
    
    context = {
        'keyword': keyword,
        'products': products,
        'total_count': products.count(),  # 现在可以正确调用count()方法
    }
    # 使用正确的模板路径
    return render(request, 'searchapp/search_results.html', context)


# 搜索联想功能
def search_suggest(request):
    """
    搜索联想功能
    """
    keyword = request.GET.get('keyword', '').strip()
    suggestions = []
    
    if keyword:
        # 使用title字段而不是name字段
        suggestions = Goods.objects.filter(
            title__icontains=keyword
        ).values('title').distinct()[:10]
    
    # 转换数据格式以匹配前端期望的格式
    results = [{'name': item['title']} for item in suggestions]
    
    return JsonResponse({
        'results': results
    })