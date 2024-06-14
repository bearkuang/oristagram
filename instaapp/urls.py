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
]