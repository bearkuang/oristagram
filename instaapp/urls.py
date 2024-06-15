from django.urls import path, include
from rest_framework.routers import DefaultRouter
from instaapp.views.user_views import UserViewSet
from instaapp.views.post_views import PostViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('auth/register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('posts/<int:pk>/like/', PostViewSet.as_view({'post': 'like'}), name='post-like'),
    path('posts/<int:pk>/unlike/', PostViewSet.as_view({'post': 'unlike'}), name='post-unlike'),
    path('posts/<int:pk>/mark/', PostViewSet.as_view({'post': 'mark'}), name='post-mark'),
    path('posts/<int:pk>/unmark/', PostViewSet.as_view({'post': 'unmark'}), name='post-unmark'),
]