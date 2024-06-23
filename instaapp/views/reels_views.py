# views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from instaapp.models.reels import Reels, Video
from instaapp.models.mark import Mark
from instaapp.models.like import Like
from instaapp.models.comment import Comment
from instaapp.models.tag import Tag
from instaapp.models.follow import Follow
from instaapp.models.user import CustomUser
from instaapp.serializers import ReelsSerializer, VideoSerializer, CommentSerializer, TagSerializer
from django.db.models import Count
from instaapp.models.validators import validate_reels_file_type, validate_reels_video_length
import json

class ReelsViewSet(viewsets.ModelViewSet):
    queryset = Reels.objects.all().annotate(
        total_engagement=Count('likes') + Count('comments')
    ).order_by('-total_engagement', '-created_at')
    serializer_class = ReelsSerializer
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

        reels = Reels.objects.create(author=request.user, content=content)

        for file in files:
            validate_reels_file_type(file)
            validate_reels_video_length(file)  # 수정된 부분: 일시적으로 파일 저장 및 검증
            Video.objects.create(reels=reels, file=file)

        for tag_name in tags_data:
            tag_name = tag_name.strip()
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag.post_count += 1
                tag.save()
                reels.tags.add(tag)

        for username in mentions_data:
            try:
                user = CustomUser.objects.get(username=username)
                reels.mentions.add(user)
            except CustomUser.DoesNotExist:
                pass

        serializer = self.get_serializer(reels)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.author != request.user:
            return Response({'error': 'You are not allowed to edit this reels.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        tags_data = json.loads(data.get('tags', '[]'))
        mentions_data = json.loads(data.get('mentions', '[]'))

        instance.tags.clear()
        for tag_name in tags_data:
            tag_name = tag_name.strip()
            if tag_name:
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
        reels = self.get_object()
        user = request.user
        if Like.objects.filter(user=user, reels=reels).exists():
            return Response({'error': 'You already liked this reels'}, status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user=user, reels=reels)
        return Response({'status': 'reels_liked'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        reels = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(user=user, reels=reels)
            like.delete()
            return Response({'status': 'reels_unliked'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'error': 'You have not liked this reels'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark(self, request, pk=None):
        reels = self.get_object()
        user = request.user
        if Mark.objects.filter(user=user, reels=reels).exists():
            return Response({'error': 'You already saved this reels'}, status=status.HTTP_400_BAD_REQUEST)
        Mark.objects.create(user=user, reels=reels)
        return Response({'status': 'reels_saved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unmark(self, request, pk=None):
        reels = self.get_object()
        user = request.user
        try:
            mark = Mark.objects.get(user=user, reels=reels)
            mark.delete()
            return Response({'status': 'reels_unsaved'}, status=status.HTTP_200_OK)
        except Mark.DoesNotExist:
            return Response({'error': 'You have not saved this reels'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def feed(self, request):
        user = request.user
        followed_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
        reelss = Reels.objects.filter(author__in=followed_users).order_by('-created_at')
        serializer = self.get_serializer(reelss, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        reels = self.get_object()
        comments = Comment.objects.filter(reels=reels).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        reels = self.get_object()
        user = request.user
        content = request.data.get('text')
        if not content:
            return Response({'error': 'Comment content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        comment = Comment.objects.create(user=user, reels=reels, text=content)
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
            reelss = tag.reels.annotate(like_count=Count('likes')).order_by('-like_count')
            serializer = self.get_serializer(reelss, many=True)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_reels(self, request, user_id=None):
        user = CustomUser.objects.get(pk=user_id)
        reels = Reels.objects.filter(author=user).order_by('-created_at')
        serializer = self.get_serializer(reels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def top_reels(self, request):
        reels = Reels.objects.annotate(
            total_engagement=Count('likes') + Count('comments')
        ).order_by('-total_engagement', '-created_at')
        
        page = self.paginate_queryset(reels)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(reels, many=True)
        return Response(serializer.data)