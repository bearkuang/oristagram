from instaapp.models.post import Post
from django.core.exceptions import ObjectDoesNotExist

def create_post(data, author):
    post = Post.objects.create(author=author, **data)
    return post

def get_posts_by_user(user):
    return Post.objects.filter(author=user).order_by('-created_at')
