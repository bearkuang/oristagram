from django.db import models
from .user import CustomUser

# 피드 엔터티
class Post(models.Model):
    # 작성자
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    # 내용
    content = models.TextField()
    # 사진
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    # 작성 시간
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.content[:20]