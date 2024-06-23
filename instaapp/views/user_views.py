from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Count, Case, When, IntegerField, Value
from instaapp.models.user import CustomUser
from instaapp.models.follow import Follow
from instaapp.models.post import Post
from instaapp.models.mark import Mark
from instaapp.models.reels import Reels
from instaapp.serializers import UserSerializer, PostSerializer, ReelsSerializer
from instaapp.services.user_services import create_user, login_user

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'login', 'register']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({"error": "Username/Email and password must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = login_user(username_or_email, password)
        if "error" in tokens:
            return Response(tokens, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(tokens, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user(serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def following(self, request):
        user = request.user
        follows = Follow.objects.filter(follower=user).select_related('followed')
        followed_users = [follow.followed for follow in follows]
        serializer = UserSerializer(followed_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request, pk=None):
        user = self.get_object() if pk else request.user
        posts = Post.objects.filter(author=user).order_by('-created_at')
        reels = Reels.objects.filter(author=user).order_by('created_at')
        saved_post_ids = Mark.objects.filter(user=user, post__isnull=False).values_list('post_id', flat=True)
        saved_posts = Post.objects.filter(id__in=saved_post_ids).order_by('-created_at')
        saved_reel_ids = Mark.objects.filter(user=user, reels__isnull=False).values_list('reels_id', flat=True)
        saved_reels = Reels.objects.filter(id__in=saved_reel_ids).order_by('created_at')
        
        followers_count = Follow.objects.filter(followed=user).count()
        following_count = Follow.objects.filter(follower=user).count()
        posts_count = posts.count()
        reels_count = reels.count()

        user_data = UserSerializer(user).data
        context = {'request': request}
        post_data = PostSerializer(posts, many=True, context=context).data
        reels_data = ReelsSerializer(reels, many=True, context=context).data
        saved_post_data = PostSerializer(saved_posts, many=True, context=context).data
        saved_reels_data = ReelsSerializer(saved_reels, many=True, context=context).data

        user_data.update({
            'followers_count': followers_count,
            'following_count': following_count,
            'posts_count': posts_count + reels_count,
            'posts': post_data,
            'reels': reels_data,
            'saved_reels': saved_reels_data,
            'saved_posts': saved_post_data
        })

        return Response(user_data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def search_usernames(self, request):
        search_term = request.query_params.get('q', '').strip()
        if not search_term:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        users = CustomUser.objects.annotate(
            follower_count=Count('followers'),
            match_score=Case(
                When(username__istartswith=search_term, then=Value(3)),  # username이 검색어로 시작하면 높은 점수
                When(username__icontains=search_term, then=Value(2)),    # username에 검색어가 포함되면 중간 점수
                When(bio__icontains=search_term, then=Value(1)),         # bio에 검색어가 포함되면 낮은 점수
                default=Value(0),
                output_field=IntegerField()
            )
        ).filter(
            Q(username__icontains=search_term) | Q(bio__icontains=search_term)
        ).order_by('-match_score', '-follower_count')

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # 사용자 정보 수정 메서드 추가
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if instance != request.user:
            return Response({'error': 'You are not allowed to update this user.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)