from rest_framework import serializers
from .models import CustomUser, Post

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'birth_date', 'profile_picture', 'website']
        
class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'created_at']