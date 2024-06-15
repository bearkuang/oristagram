from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from instaapp.models import Follow, CustomUser
from instaapp.serializers import FollowSerializer

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        follower = request.user
        try:
            followed = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if Follow.objects.filter(follower=follower, followed=followed).exists():
            return Response({'error': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow = Follow.objects.create(follower=follower, followed=followed)
        return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        follower = request.user
        try:
            followed = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            follow = Follow.objects.get(follower=follower, followed=followed)
            follow.delete()
            return Response({'status': 'Unfollowed successfully'}, status=status.HTTP_200_OK)
        except Follow.DoesNotExist:
            return Response({'error': 'No Follow matches the given query.'}, status=status.HTTP_400_BAD_REQUEST)
