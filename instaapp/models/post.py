from django.db import models
from .user import CustomUser
from django.core.exceptions import ValidationError

def validate_file_type(value):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/jpg', 'video/mp4', 'video/mpeg']
    file_mime_type = value.file.content_type
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Unsupported file type.')

# 태그
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    post_count = models.PositiveIntegerField(default=0) # 태그된 게시물 수
    
    def __str__(self):
        return self.name

# 피드 엔터티
class Post(models.Model):
    # 작성자
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    # 내용
    content = models.TextField(blank=True, null=True)
    # 작성 시간
    created_at = models.DateTimeField(auto_now_add=True)
    # 태그
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    # 언급
    mentions = models.ManyToManyField(CustomUser, related_name='mentioned_posts', blank=True)
    
    def __str__(self):
        return self.content[:20] if self.content else "No Content"
    
# 이미지 모델 (여러 이미지를 업로드하기 위해)
class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    file = models.FileField(upload_to='posts/', validators=[validate_file_type])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'File for post {self.post.id}'
    
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
        return f'{self.user.username} commented on {self.post.id}'
    

