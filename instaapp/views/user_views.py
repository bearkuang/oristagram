from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from instaapp.models.user import CustomUser
from instaapp.models.follow import Follow
from instaapp.models.post import Post, Mark
from instaapp.serializers import UserSerializer, PostSerializer
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
    def profile(self, request):
        user = request.user
        posts = Post.objects.filter(author=user).order_by('-created_at')
        saved_posts = Mark.objects.filter(user=user).values_list('post', flat=True)
        saved_posts = Post.objects.filter(id__in=saved_posts).order_by('-created_at')
        
        followers_count = Follow.objects.filter(followed=user).count()
        following_count = Follow.objects.filter(follower=user).count()
        posts_count = posts.count()

        user_data = UserSerializer(user).data
        context = {'request': request}
        post_data = PostSerializer(posts, many=True, context=context).data
        saved_post_data = PostSerializer(saved_posts, many=True, context=context).data

        user_data.update({
            'followers_count': followers_count,
            'following_count': following_count,
            'posts_count': posts_count,
            'posts': post_data,
            'saved_posts': saved_post_data
        })

        return Response(user_data)