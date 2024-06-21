from django.db import models
from .user import CustomUser
from django.core.exceptions import ValidationError
from moviepy.editor import VideoFileClip
from .tag import Tag
from .validators import validate_feed_file_type, validate_feed_video_length

# 피드
class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    mentions = models.ManyToManyField(CustomUser, related_name='mentioned_posts', blank=True)

    def __str__(self):
        return self.content[:20] if self.content else "No Content"

# 이미지 혹은 영상
class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    file = models.FileField(upload_to='posts/', validators=[validate_feed_file_type])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'File for post {self.post.id}'