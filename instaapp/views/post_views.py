from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from instaapp.models.post import Like, Mark, Post, Image, Comment, Tag
from instaapp.models.follow import Follow
from instaapp.models.user import CustomUser
from instaapp.serializers import PostSerializer, ImageSerializer, CommentSerializer, TagSerializer
from django.db.models import Count
import json

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        files = request.FILES.getlist('files')
        content = data.get('content')

        try:
            tags_data = json.loads(data.get('tags', '[]'))
        except json.JSONDecodeError:
            tags_data = []

        try:
            mentions_data = json.loads(data.get('mentions', '[]'))
        except json.JSONDecodeError:
            mentions_data = []

        post = Post.objects.create(author=request.user, content=content)
        
        # 디버그 출력
        print(f"Tags: {tags_data}")
        print(f"Mentions: {mentions_data}")

        for file in files:
            Image.objects.create(post=post, file=file)
        
        for tag_name in tags_data:
            tag_name = tag_name.strip()  # 태그 이름의 앞뒤 공백 제거
            if tag_name:  # 빈 태그는 추가하지 않음
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag.post_count += 1  # 태그된 게시물 수 증가
                tag.save()
                post.tags.add(tag)
    
        for username in mentions_data:
            try:
                user = CustomUser.objects.get(username=username)
                post.mentions.add(user)
            except CustomUser.DoesNotExist:
                pass
    
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.author != request.user:
            return Response({'error': 'You are not allowed to edit this post.'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        tags_data = json.loads(data.get('tags', '[]'))
        mentions_data = json.loads(data.get('mentions', '[]'))
        
        instance.tags.clear()
        for tag_name in tags_data:
            tag_name = tag_name.strip()  # 태그 이름의 앞뒤 공백 제거
            if tag_name:  # 빈 태그는 추가하지 않음
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)

        instance.mentions.clear()
        for username in mentions_data:
            try:
                user = CustomUser.objects.get(username=username)
                instance.mentions.add(user)
            except CustomUser.DoesNotExist:
                pass
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if Like.objects.filter(user=user, post=post).exists():
            return Response({'error': 'You already liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user=user, post=post)
        return Response({'status': 'post_liked'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(user=user, post=post)
            like.delete()
            return Response({'status': 'post unliked'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'error': 'You have not liked this post'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if Mark.objects.filter(user=user, post=post).exists():
            return Response({'error': 'You already saved this post'}, status=status.HTTP_400_BAD_REQUEST)
        Mark.objects.create(user=user, post=post)
        return Response({'status': 'post saved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unmark(self, request, pk=None):
        post = self.get_object()
        user = request.user
        try:
            mark = Mark.objects.get(user=user, post=post)
            mark.delete()
            return Response({'status': 'post unsaved'}, status=status.HTTP_200_OK)
        except Mark.DoesNotExist:
            return Response({'error': 'You have not saved this post'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def feed(self, request):
        user = request.user
        followed_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
        posts = Post.objects.filter(author__in=followed_users).order_by('-created_at')
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = Comment.objects.filter(post=post).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        user = request.user
        content = request.data.get('text')
        if not content:
            return Response({'error': 'Comment content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        comment = Comment.objects.create(user=user, post=post, text=content)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def search_tags(self, request):
        search_term = request.query_params.get('q', '').strip()
        if not search_term:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        tags = Tag.objects.filter(name__icontains=search_term).order_by('-post_count')
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def tagged(self, request):
        tag_name = request.query_params.get('tag', '').strip()
        if not tag_name:
            return Response({"error": "Tag parameter 'tag' is required."}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            tag = Tag.objects.get(name=tag_name)
            posts = tag.posts.annotate(like_count=Count('likes')).order_by('-like_count')
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)
