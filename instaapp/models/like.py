from django.db import models
from .user import CustomUser
from .post import Post
from .reels import Reels

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    reels = models.ForeignKey(Reels, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('user', 'post'),
            ('user', 'reels'),
        ]

    def __str__(self):
        return f'{self.user.username} likes {self.post.id if self.post else self.reels.id}'
