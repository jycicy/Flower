from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class User(AbstractUser):
    """
    自定义用户模型，使用邮箱作为主要认证方式
    """
    # 重写 username 字段，使其可选
    username = models.CharField(
        _("用户名"),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_("可选的用户名")
    )
    #密码
    password = models.CharField(
        _("密码"),
        max_length=128,
        help_text=_("用户登录密码")
    )
    
    # 邮箱作为主要认证字段
    email = models.EmailField(
        _("邮箱地址"),
        unique=True,
        help_text=_("用户的主要邮箱地址，用于登录")
    )
    
    # 用户个人手机号（与收件地址手机号区分开）
    phone = models.CharField(
        _("个人手机号"),
        max_length=15,
        blank=True,
        null=True,
        help_text=_("用户个人手机号码，与收件地址手机号码不同")
    )
    
    # 头像
    avatar = models.ImageField(
        _("头像"), 
        upload_to="users/avatars/", 
        default='users/avatars/default.png',
        blank=True, 
        null=True,
        help_text=_("用户头像图片")
    )
    
    # 昵称
    nickname = models.CharField(
        _("昵称"), 
        max_length=30, 
        blank=True,
        help_text=_("用户昵称，最多30字")
    )

    # 性别选择
    GENDER_CHOICES = [
        ('M', _('男')),
        ('F', _('女')),
    ]
    gender = models.CharField(
        _("性别"), 
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True,
        help_text=_("用户的性别")
    )
    
    # 生日
    birth_date = models.DateField(
        _("出生日期"), 
        blank=True, 
        null=True,
        help_text=_("用户的出生日期")
    )
    
    # 个人简介
    bio = models.TextField(
        _("个人简介"), 
        max_length=500, 
        blank=True,
        help_text=_("用户个人简介，最多500字")
    )
    
    # 邮箱验证状态
    email_verified = models.BooleanField(
        _("邮箱已验证"),
        default=False,
        help_text=_("标识用户的邮箱是否已验证")
    )
    
    # 手机号验证状态
    phone_verified = models.BooleanField(
        _("手机号已验证"),
        default=False,
        help_text=_("标识用户的手机号是否已验证")
    )
    
    # 创建和更新时间
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    
    # 指定邮箱为 USERNAME_FIELD（用于登录）
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # 创建超级用户时需要
    
    class Meta:
        db_table = 'custom_user'
        verbose_name = _("用户")
        verbose_name_plural = _("用户")
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        if self.get_full_name():
            return f"{self.get_full_name()} ({self.email})"
        return self.email
    
    def get_full_name(self):
        """
        返回用户的全名
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def get_short_name(self):
        """
        返回用户的简称
        """
        return self.first_name or self.username or self.email.split('@')[0]
    
    def get_absolute_url(self):
        """
        返回用户详情页的URL
        """
        return reverse('userapp:user_detail', kwargs={'pk': self.pk})
    
    def get_avatar_url(self):
        """
        获取用户头像URL，如果没有则返回默认头像
        """
        if self.avatar:
            return self.avatar.url
        return "/static/images/default-avatar.png"

# 在 models.py 中添加地址模型
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    receiver_name = models.CharField(max_length=50, verbose_name="收货人")
    receiver_phone = models.CharField(max_length=20, verbose_name="联系电话")
    province = models.CharField(max_length=50, verbose_name="省份")
    city = models.CharField(max_length=50, verbose_name="城市")
    district = models.CharField(max_length=50, verbose_name="区县")
    detail_address = models.CharField(max_length=200, verbose_name="详细地址")
    is_default = models.BooleanField(default=False, verbose_name="是否默认地址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = "收货地址"
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.receiver_name} - {self.detail_address}"