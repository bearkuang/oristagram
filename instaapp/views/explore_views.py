from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from instaapp.models.post import Post
from instaapp.models.reels import Reels
from instaapp.serializers import PostSerializer, ReelsSerializer

class ExploreViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        # 피드 정렬 (예시: 좋아요 수와 댓글 수 기준으로 정렬)
        feeds = Post.objects.annotate(
            engagement=Count('likes') + Count('comments')
        ).order_by('-engagement')

        # 릴스 정렬 (예시: 좋아요 수와 댓글 수 기준으로 정렬)
        reels = Reels.objects.annotate(
            engagement=Count('likes') + Count('comments')
        ).order_by('-engagement')

        # 피드와 릴스를 결합하여 하나의 리스트로 반환
        combined_results = list(feeds) + list(reels)

        # 예시: 피드와 릴스를 번갈아가며 섞는 로직
        combined_results_sorted = sorted(combined_results, key=lambda x: x.engagement, reverse=True)

        # 시리얼라이저로 데이터 변환
        feed_serializer = PostSerializer(feeds, many=True, context={'request': request})
        reels_serializer = ReelsSerializer(reels, many=True, context={'request': request})

        # 결합된 결과 반환
        return Response({
            'feeds': feed_serializer.data,
            'reels': reels_serializer.data
        })
