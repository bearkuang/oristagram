from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission

class CustomUserManager(BaseUserManager):
    def create_user(self, username, name, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, name, email, password, **extra_fields)

# 사용자 엔터티
class CustomUser(AbstractUser):
    # 이름
    name = models.TextField(blank=True, null=True)
    # 자기 소개
    bio = models.TextField(blank=True, null=True)
    # 생일
    birth_date = models.DateField(blank=True, null=True)
    # 프로필 사진
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # 웹 사이트
    website = models.URLField(blank=True, null=True)
    # 활성화 여부
    is_active = models.BooleanField(default=True)
    
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username