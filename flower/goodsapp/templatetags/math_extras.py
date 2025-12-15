from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """获取字典中的值"""
    return dictionary.get(str(key), 0)

@register.filter
def calculate_percentage(value, total):
    """计算百分比"""
    if total == 0:
        return 0
    return round((float(value) / float(total)) * 100)