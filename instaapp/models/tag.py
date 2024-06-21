from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    post_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
