from rest_framework import serializers
from .models import CustomUser, Post

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'birth_date', 'profile_picture', 'website']
        extra_kwargs = {'profile_picture': {'required': False}}

    def create(self, validated_data):
        if 'profile_picture' not in validated_data or not validated_data['profile_picture']:
            validated_data['profile_picture'] = 'profile_pics/default_profile_image.png'
        return super().create(validated_data)
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'created_at', 'like_count', 'mark_count']
        read_only_fields = ['author', 'created_at']
        
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_mark_count(self, obj):
        return obj.marks.count()