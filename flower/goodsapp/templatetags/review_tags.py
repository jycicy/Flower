from django import template

register = template.Library()

@register.simple_tag
def star_rating(rating):
    """生成星级评分HTML"""
    html = ""
    for i in range(1, 6):
        if i <= rating:
            html += '<span class="star active">★</span>'
        else:
            html += '<span class="star">★</span>'
    return html