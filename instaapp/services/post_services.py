from instaapp.models.post import Post
from django.core.exceptions import ObjectDoesNotExist

def create_post(data, user):
    content = data.get('content', None)
    image = data.get('image', '')
    
    post = Post.objects.create(author=user, content=content, image=image)
    return post

def get_posts_by_user(user):
    return Post.objects.filter(author=user).order_by('-created_at')
