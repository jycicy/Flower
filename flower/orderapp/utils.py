# orderapp/utils.py
import logging
from alipay import AliPay
from django.conf import settings

# 配置日志
logger = logging.getLogger(__name__)


# 获取支付宝实例
def get_alipay():
    """获取支付宝实例"""
    try:
        alipay = AliPay(
            appid=settings.ALIPAY_CONFIG['appid'],
            app_notify_url=settings.ALIPAY_CONFIG['app_notify_url'],
            app_private_key_string=settings.ALIPAY_CONFIG['app_private_key_string'].strip(),
            alipay_public_key_string=settings.ALIPAY_CONFIG['alipay_public_key_string'].strip(),
            sign_type=settings.ALIPAY_CONFIG['sign_type'],
            debug=settings.ALIPAY_CONFIG['debug']
        )
        return alipay
    except Exception as e:
        logger.error(f"创建支付宝实例失败: {e}")
        raise

# 创建支付宝支付订单
def create_alipay_payment(order):
    """创建支付宝支付订单"""
    try:
        alipay = get_alipay()
        
        # 构造支付宝支付链接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order.order_number,
            total_amount=str(order.total_amount),
            subject=f"鲜花订单-{order.order_number}",
            return_url="https://b888e2925deb.ngrok-free.app/order/return/",
            notify_url="https://b888e2925deb.ngrok-free.app/order/notify/"
        )
        
        # 沙箱环境支付网关
        if settings.ALIPAY_CONFIG['debug']:
            gateway = "https://openapi-sandbox.dl.alipaydev.com/gateway.do?" 
        else:
            gateway = "https://openapi.alipay.com/gateway.do?"
        
        pay_url = gateway + order_string
        logger.info(f"生成支付链接: {pay_url}")
        return pay_url
        
    except Exception as e:
        logger.error(f"创建支付宝支付订单失败: {e}")
        raise