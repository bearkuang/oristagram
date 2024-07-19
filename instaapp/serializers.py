from rest_framework import serializers
from .models import CustomUser, Post, Image, Follow, Like, Mark, Comment, Tag, Reels, ChatRoom, Message
from .models.reels import Video

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'email', 'password', 'bio', 'birth_date', 'profile_picture', 'website']
        extra_kwargs = {
            'profile_picture': {'required': False},
            'bio': {'required': True},
            'birth_date': {'required': True},
            'website': {'required': False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
    
class ImageSerializer(serializers.ModelSerializer):
    filtered_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'file', 'filter', 'created_at', 'filtered_url']

    def get_filtered_url(self, obj):
        if obj.filter != 'none':
            return obj.file.url  # 필터가 적용된 이미지의 URL을 반환
        return None  # 필터가 적용되지 않은 경우 None 반환
        
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
        fields = ['id', 'author', 'content', 'images', 'created_at', 'like_count', 'mark_count', 'is_liked', 'is_saved', 'comment_count', 'tags', 'mentions', 'site']
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
    
class CombinedFeedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author = UserSerializer()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()
    like_count = serializers.IntegerField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        if isinstance(obj, Post):
            return obj.comments.count()
        elif isinstance(obj, Reels):
            return obj.comments.count()
        return 0

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if isinstance(obj, Post):
            return Like.objects.filter(user=user, post=obj).exists()
        elif isinstance(obj, Reels):
            return Like.objects.filter(user=user, reels=obj).exists()
        return False

    def get_is_saved(self, obj):
        user = self.context['request'].user
        if isinstance(obj, Post):
            return Mark.objects.filter(user=user, post=obj).exists()
        elif isinstance(obj, Reels):
            return Mark.objects.filter(user=user, reels=obj).exists()
        return False

    def get_type(self, obj):
        return 'post' if isinstance(obj, Post) else 'reels'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, Post):
            data['images'] = ImageSerializer(instance.images.all(), many=True).data
        elif isinstance(instance, Reels):
            data['videos'] = VideoSerializer(instance.videos.all(), many=True).data
        return data
    
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