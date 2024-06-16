from django.db import models
from .user import CustomUser

# 피드 엔터티
class Post(models.Model):
    # 작성자
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    # 내용
    content = models.TextField(blank=True, null=True)
    # 사진
    image = models.ImageField(upload_to='posts/', null=False, blank=False)
    # 작성 시간
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.content[:20] if self.content else "No Content"
    
# 좋아요 모델
class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [('user', 'post')]
        
    def __str__(self):
        return f'{self.user.username} likes {self.post.id}'

# 피드 저장 모델
class Mark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='marks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [('user', 'post')]
        
    def __str__(self):
        return f'{self.user.username} saved {self.post.id}'
    
# 피드 댓글
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} saved {self.post.id}'
