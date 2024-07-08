import logging
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.core.exceptions import ValidationError
from django.db.models import Q, Count, Case, When, IntegerField, Value
from instaapp.models.user import CustomUser
from instaapp.models.follow import Follow
from instaapp.models.post import Post
from instaapp.models.mark import Mark
from instaapp.models.reels import Reels
from instaapp.serializers import UserSerializer, PostSerializer, ReelsSerializer
from instaapp.services.user_services import create_user, login_user, reactivate_user, delete_user
from instaapp.authentication import TempTokenAuthentication

logger = logging.getLogger(__name__)

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

        try:
            result = login_user(username_or_email, password)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = create_user(serializer.validated_data)
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        user = self.get_object() if pk else request.user
        follows = Follow.objects.filter(follower=user).select_related('followed')
        followed_users = [follow.followed for follow in follows]
        serializer = UserSerializer(followed_users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        user = self.get_object() if pk else request.user
        followers = Follow.objects.filter(followed=user).select_related('follower')
        follower_users = [follow.follower for follow in followers]
        serializer = UserSerializer(follower_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        try:
            user_to_unfollow = CustomUser.objects.get(pk=pk)
            follow_instance = Follow.objects.get(follower=user_to_unfollow, followed=request.user)
            follow_instance.delete()
            return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Follow.DoesNotExist:
            return Response({'error': 'Follow relationship not found'}, status=status.HTTP_400_BAD_REQUEST)
    
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
    
    # 계정 비활성화
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request):
        user = request.user
        user.is_active = False
        user.save()
        
        # 데이터는 삭제하지 않고 비활성화
        return Response({"message": "User account has been deactivated."}, status=status.HTTP_200_OK)
    
    # 계정 비활성화 해제
    @action(detail=False, methods=['post'], authentication_classes=[TempTokenAuthentication], permission_classes=[AllowAny])
    def reactivate_account(self, request):
        user = request.user
        logger.debug(f"Reactivate account requested for user: {user}, is_active: {user.is_active}")
        
        try:
            user = reactivate_user(user.id)
            logger.debug(f"User reactivated: {user}, is_active: {user.is_active}")
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Account reactivated successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error reactivating account: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # 비활성화 계정 탈퇴
    @action(detail=False, methods=['post'], authentication_classes=[TempTokenAuthentication], permission_classes=[AllowAny])
    def delete_deactivated_account(self, request):
        user = request.user
        logger.debug(f"Delete deactivated account requested for user: {user}, is_active: {user.is_active}")
        
        try:
            if user.is_active:
                return Response({'error': 'This account is active. Use the normal delete account process.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if delete_user(user.id):
                return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting deactivated account: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # 활성화된 계정 탈퇴
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_account(self, request):
        user = request.user
        logger.debug(f"Delete account requested for user: {user}, is_active: {user.is_active}")
        
        # 비밀번호 확인
        password = request.data.get('password')
        if not user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user.delete()
            return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting account: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # 신규 가입한 사용자 5명 추천
    @action(detail=False, methods=['get'])
    def new_users(self, request):
        current_user = request.user
        
        # 현재 사용자가 팔로우하는 사용자들의 ID 목록
        followed_users = Follow.objects.filter(follower=current_user).values_list('followed', flat=True)
        
        # 현재 사용자와 팔로우하는 사용자들을 제외한 최근 가입한 사용자 5명을 조회
        new_users = CustomUser.objects.exclude(
            Q(id=current_user.id) | Q(id__in=followed_users)
        ).order_by('-date_joined')[:5]
        
        serializer = self.get_serializer(new_users, many=True)
        return Response(serializer.data)