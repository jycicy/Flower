from django.shortcuts import render
import json
from django.http import JsonResponse
from django.conf import settings
import os
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from goodsapp.models import Goods, Review, Card, Flower
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods


# Create your views here.
@login_required(login_url='userapp:login')
def index(request):
    return render(request, 'goodsapp/index.html')


# 商品列表页
def goods_list(request):
    # 从数据库获取数据
    goods_data = Goods.objects.all()
    context = {
        'goods_list': goods_data
    }

    return render(request, 'goodsapp/flowers_list.html', context)

# 商品列表分页API
def goods_list_api(request):
    page = request.GET.get('page', 1)  # 获取当前页码，默认为第1页
    per_page = 12  # 每页显示的商品数量

    goods = Goods.objects.all()  # 获取所有商品
    paginator = Paginator(goods, per_page)  # 使用分页器

    try:
        goods_page = paginator.page(page)
    except:
        return JsonResponse({'goods': [], 'has_next': False})  # 如果页码超出范围

    # 返回商品数据
    data = {
        'goods': [
            {
                'id': item.id,
                'title': item.title,
                'price': str(item.price),
                'description': item.description,
                'image_url': item.image_url,
            }
            for item in goods_page
        ],
        'has_next': goods_page.has_next()  # 是否还有下一页
    }
    return JsonResponse(data)


#api(json)
def flowers_data(request):
    try:
        # 构建正确的文件路径: project/api/goods/flowers_data.json
        json_file_path = os.path.join(settings.BASE_DIR, 'api', 'goods', 'flowers_data.json')
        
        # 检查文件是否存在
        if not os.path.exists(json_file_path):
            return JsonResponse({
                'error': '数据文件不存在',
                'file_path': json_file_path,
                'base_dir': str(settings.BASE_DIR)
            }, status=404)
        
        # 读取并解析JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'type': type(e).__name__
        }, status=500)

#商品详情(json)
@login_required(login_url='userapp:login')
def goods_detail(request, id):
    """使用数据库中 Flower 模型的详情页"""
    # 从数据库获取 Flower 对象，而不是从 JSON 文件
    flower = get_object_or_404(Flower, id=id)
    
    # 获取评论数据（取消分页）
    reviews = Review.objects.filter(goods_id=id).select_related('user').order_by('-created_at')
    
    # 计算统计数据
    total_reviews = reviews.count()
    avg_rating = 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    rating_percentages = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    if total_reviews > 0:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / total_reviews, 1)
        
        for review in reviews:
            rating_counts[review.rating] += 1
            
        # 计算百分比
        for i in range(1, 6):
            rating_percentages[i] = round((rating_counts[i] / total_reviews) * 100)
    
    context = {
        'goods': flower,  # 直接使用从数据库获取的 flower 对象
        'reviews': reviews,  # 直接传递所有评论，不进行分页
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages,
    }
    
    return render(request, 'goodsapp/goods_detail.html', context)


def flower_detail(request, id):
    """使用 Flower 模型的详情页"""
    # 获取 Flower 对象
    flower = get_object_or_404(Flower, id=id)
    
    # 获取评论数据（这里需要根据您的需求调整，因为 Review 模型关联的是 Goods）
    # 如果您想让 Flower 也有评论功能，需要修改 Review 模型或者创建新的评论模型
    reviews = Review.objects.none()  # 暂时返回空的评论集
    
    # 计算统计数据（暂时使用默认值）
    total_reviews = 0
    avg_rating = 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    rating_percentages = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    context = {
        'goods': flower,  # 为了兼容现有模板，使用 goods 作为变量名
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages,
    }
    
    return render(request, 'goodsapp/goods_detail.html', context)



def product_detail(request, goods_id):
    goods = get_object_or_404(Goods, id=goods_id)
    
    # 获取评论，按创建时间倒序排列
    reviews = Review.objects.filter(goods=goods).select_related('user').order_by('-created_at')
    
    # 分页处理（每页显示10条评论）
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 计算统计数据
    total_reviews = reviews.count()
    avg_rating = 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    if total_reviews > 0:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / total_reviews, 1)
        
        for review in reviews:
            rating_counts[review.rating] += 1
    
    context = {
        'goods': goods,
        'reviews': page_obj,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
    }
    
    return render(request, 'goodsapp/goods_detail.html', context)


#添加评论
@login_required
@require_http_methods(["POST"])
def add_review(request, id):
    """
    添加评论
    """
    try:
        goods = get_object_or_404(Goods, id=id)
        data = json.loads(request.body)
        
        rating = int(data.get('rating', 0))
        comment = data.get('comment', '').strip()
        
        # 验证数据
        if not (1 <= rating <= 5):
            return JsonResponse({'success': False, 'message': '请选择有效的评分'})
        
        if not comment:
            return JsonResponse({'success': False, 'message': '评论内容不能为空'})
        
        # 创建评论
        Review.objects.create(
            goods=goods,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({'success': True, 'message': '评论提交成功'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '评论提交失败，请稍后再试'})


#获取商品评论
def get_goods_reviews(request, id):
    """
    获取商品评论的API接口
    """
    try:
        goods = get_object_or_404(Goods, id=id)
        
        # 获取评论数据
        reviews = Review.objects.filter(goods=goods).select_related('user').order_by('-created_at')
        
        # 分页处理
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        paginator = Paginator(reviews, per_page)
        page_obj = paginator.get_page(page)
        
        # 构造返回数据
        reviews_data = []
        for review in page_obj:
            reviews_data.append({
                'id': review.id,
                'username': review.user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # 计算统计数据
        total_reviews = reviews.count()
        avg_rating = 0
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        if total_reviews > 0:
            total_rating = sum(r.rating for r in reviews)
            avg_rating = round(total_rating / total_reviews, 1)
            
            for review in reviews:
                rating_counts[review.rating] += 1
        
        return JsonResponse({
            'success': True,
            'reviews': reviews_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_reviews': total_reviews
            },
            'stats': {
                'avg_rating': avg_rating,
                'rating_counts': rating_counts
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

       


# 获取所有卡片数据的API
def get_cards(request):
    """
    获取所有卡片数据
    """
    try:
        cards = Card.objects.all().order_by('-created_at')[:50]  # 限制最多50个卡片
        
        cards_data = []
        for card in cards:
            cards_data.append({
                'id': card.id,
                'text': card.text,
                'color': card.color,
                'border_color': card.border_color,
                'x': card.x,
                'y': card.y,
                'dx': card.dx,
                'dy': card.dy,
                'width': card.width,
                'height': card.height,
            })
        
        return JsonResponse({
            'success': True,
            'cards': cards_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

# 添加新卡片的API
@login_required
def add_card(request):
    """
    添加新卡片
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '只支持POST请求'
        })

    try:
        data = json.loads(request.body)
        
        # 创建新卡片
        card = Card.objects.create(
            text=data.get('text', '漂流的卡片'),
            color=data.get('color', '#FFE0B2'),
            border_color=data.get('borderColor', '#FFA726'),
            x=float(data.get('x', 100)),
            y=float(data.get('y', 100)),
            dx=float(data.get('dx', 0.5)),
            dy=float(data.get('dy', 0.5)),
            width=float(data.get('width', 120)),
            height=float(data.get('height', 80)),
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': '卡片添加成功',
            'card': {
                'id': card.id,
                'text': card.text,
                'color': card.color,
                'border_color': card.border_color,
                'x': card.x,
                'y': card.y,
                'dx': card.dx,
                'dy': card.dy,
                'width': card.width,
                'height': card.height,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'添加卡片失败: {str(e)}'
        })

        