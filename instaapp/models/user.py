from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# 사용자 엔터티
class CustomUser(AbstractUser):
    # 자기 소개
    bio = models.TextField(blank=True, null=True)
    # 생일
    birth_date = models.DateField(blank=True, null=True)
    # 프로필 사진
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # 웹 사이트
    website = models.URLField(blank=True, null=True)
    
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')
    
    def __str__(self):
        return self.username