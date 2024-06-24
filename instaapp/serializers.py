from rest_framework import serializers
from .models import CustomUser, Post, Image, Follow, Like, Mark, Comment, Tag, Reels, ChatRoom, Message
from .models.reels import Video

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'email', 'bio', 'birth_date', 'profile_picture', 'website']
        extra_kwargs = {'profile_picture': {'required': False}}

    def create(self, validated_data):
        if 'profile_picture' not in validated_data or not validated_data['profile_picture']:
            validated_data['profile_picture'] = 'profile_pics/default_profile_image.png'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'file', 'created_at']
        
class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'post_count']

class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    mark_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    mentions = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'images', 'created_at', 'like_count', 'mark_count', 'is_liked', 'is_saved', 'comment_count', 'tags', 'mentions']
        read_only_fields = ['author', 'created_at', 'like_count', 'mark_count', 'comment_count']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_mark_count(self, obj):
        return obj.marks.count()

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        return Like.objects.filter(user=user, post=obj).exists()

    def get_is_saved(self, obj):
        user = self.context.get('request').user
        return Mark.objects.filter(user=user, post=obj).exists()

    def get_author(self, obj):
        author = obj.author
        return {
            'id': author.id,
            'username': author.username,
            'profile_picture': author.profile_picture.url if author.profile_picture else None
        }

    def get_comment_count(self, obj):
        return obj.comments.count()

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']
        read_only_fields = ['follower', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    mentions = UserSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'reels', 'text', 'created_at', 'mentions', 'replies', 'parent']
        read_only_fields = ['user', 'post', 'reels', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'file', 'created_at']

class ReelsSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    mark_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    mentions = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Reels
        fields = ['id', 'author', 'content', 'videos', 'created_at', 'like_count', 'mark_count', 'is_liked', 'is_saved', 'comment_count', 'tags', 'mentions']
        read_only_fields = ['author', 'created_at', 'like_count', 'mark_count', 'comment_count']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_mark_count(self, obj):
        return obj.marks.count()

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        return Like.objects.filter(user=user, reels=obj).exists()

    def get_is_saved(self, obj):
        user = self.context.get('request').user
        return Mark.objects.filter(user=user, reels=obj).exists()

    def get_author(self, obj):
        author = obj.author
        return {
            'id': author.id,
            'username': author.username,
            'profile_picture': author.profile_picture.url if author.profile_picture else None
        }

    def get_comment_count(self, obj):
        return obj.comments.count()
    
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'chatroom', 'sender', 'receiver', 'content', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at', 'last_message']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        return MessageSerializer(last_message).data if last_message else None