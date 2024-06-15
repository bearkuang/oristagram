from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from instaapp.models.post import Like, Mark, Post
from instaapp.serializers import PostSerializer
from instaapp.services.post_services import create_post

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwagrgs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = create_post(serializer.validated_data, self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED, headers=headers)
        
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.author != request.user:
            return Response({'error': 'You are not allowed to edit this post.'}, status=status.HTTP_403_FORBIDDEN)
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