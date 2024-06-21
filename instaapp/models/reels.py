from django.db import models
from .user import CustomUser
from django.core.exceptions import ValidationError
from .tag import Tag
from .validators import validate_reels_file_type, validate_reels_video_length

class Reels(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reels')
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='reels', blank=True)
    mentions = models.ManyToManyField(CustomUser, related_name='mentioned_reels', blank=True)

    def __str__(self):
        return self.content[:20] if self.content else "No Content"

class Video(models.Model):
    reels = models.ForeignKey(Reels, on_delete=models.CASCADE, related_name='videos')
    file = models.FileField(upload_to='reels/', validators=[validate_reels_file_type, validate_reels_video_length])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Video for reels {self.reels.id}'