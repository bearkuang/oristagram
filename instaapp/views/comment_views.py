from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from instaapp.models.comment import Comment
from instaapp.serializers import CommentSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(parent__isnull=True)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def replies(self, request, pk=None):
        comment = self.get_object()
        replies = Comment.objects.filter(parent=comment).order_by('created_at')
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)
