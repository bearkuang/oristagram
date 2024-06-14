from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from instaapp.models.user import CustomUser

User = get_user_model()

def create_user(user_data):
    bio = user_data.pop('bio', '')
    birth_date = user_data.pop('birth_date', None)
    website = user_data.pop('website', '')
    profile_picture = user_data.pop('profile_picture', None)
    
    user = CustomUser.objects.create_user(**user_data)
    user.bio = bio
    user.birth_date = birth_date
    user.website = website
    user.profile_picture = profile_picture
    user.save()
    return user

def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return None

def login_user(username_or_email, password):
    user = authenticate(username=username_or_email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    else:
        return None