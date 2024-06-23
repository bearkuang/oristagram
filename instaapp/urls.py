from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from instaapp.views.user_views import UserViewSet
from instaapp.views.post_views import PostViewSet
from instaapp.views.follow_views import FollowViewSet
from instaapp.views.reels_views import ReelsViewSet
from instaapp.views.explore_views import ExploreViewSet
from instaapp.views.comment_views import CommentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'follows', FollowViewSet, basename='follows')
router.register(r'reels', ReelsViewSet, basename='reels')
router.register(r'explore', ExploreViewSet, basename='explore')
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('auth/register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('posts/<int:pk>/like/', PostViewSet.as_view({'post': 'like'}), name='post-like'),
    path('posts/<int:pk>/unlike/', PostViewSet.as_view({'post': 'unlike'}), name='post-unlike'),
    path('posts/<int:pk>/mark/', PostViewSet.as_view({'post': 'mark'}), name='post-mark'),
    path('posts/<int:pk>/unmark/', PostViewSet.as_view({'post': 'unmark'}), name='post-unmark'),
    path('posts/<int:pk>/comment/', PostViewSet.as_view({'post': 'comment'}), name='post-comment'),
    path('posts/user/<int:user_id>/', PostViewSet.as_view({'get': 'user_posts'}), name='user-posts'),
    path('follows/<int:pk>/follow/', FollowViewSet.as_view({'post': 'follow'}), name='follow-follow'),
    path('follows/<int:pk>/unfollows/', FollowViewSet.as_view({'post': 'unfollows'}), name='follows-unfollows'),
    path('feed/', PostViewSet.as_view({'get': 'feed'}), name='user-feed'),
    path('users/following/', UserViewSet.as_view({'get': 'following'}), name='user-following'),
    path('users/profile/', UserViewSet.as_view({'get': 'profile'}), name='user-profile'),
    path('users/profile/<int:pk>/', UserViewSet.as_view({'get': 'profile'}), name='user-profile-specific'),
    path('search/tags/', PostViewSet.as_view({'get': 'search_tags'}), name='search-tags'),
    path('search/tagged/', PostViewSet.as_view({'get': 'tagged'}), name='search-tagged'),
    path('search/usernames/', UserViewSet.as_view({'get': 'search_usernames'}), name='search-usernames'),
    path('reels/<int:pk>/like/', ReelsViewSet.as_view({'post': 'like'}), name='reels-like'),
    path('reels/<int:pk>/unlike/', ReelsViewSet.as_view({'post': 'unlike'}), name='reels-unlike'),
    path('reels/<int:pk>/mark/', ReelsViewSet.as_view({'post': 'mark'}), name='reels-mark'),
    path('reels/<int:pk>/unmark/', ReelsViewSet.as_view({'post': 'unmark'}), name='reels-unmark'),
    path('reels/<int:pk>/comment/', ReelsViewSet.as_view({'post': 'comment'}), name='reels-comment'),
    path('reels/user/<int:user_id>/', ReelsViewSet.as_view({'get': 'user_reels'}), name='user-reels-specific'),
    path('reels/top_reels/', ReelsViewSet.as_view({'get': 'top_reels'}), name='top-reels'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
