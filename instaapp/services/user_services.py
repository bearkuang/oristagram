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
    
    # 디버깅을 위해 비밀번호 출력 (주의: 실제로는 보안상 이유로 이렇게 하지 말아야 합니다)
    # print(f"Created user: {user.username}, password: {user.password}")
    
    return user

def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return None

def login_user(username_or_email, password):
    user = None

    if '@' in username_or_email:
        try:
            user = CustomUser.objects.get(email=username_or_email)
            print(f"Found user by email: {user.username}")
        except CustomUser.DoesNotExist:
            print("No user found with this email.")
    else:
        try:
            user = CustomUser.objects.get(username=username_or_email)
            print(f"Found user by username: {user.username}")
        except CustomUser.DoesNotExist:
            print("No user found with this username.")

    if user:
        print(f"Authenticating user: {user.username} with password: {password}")
        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user:
            print("Authentication successful")
        else:
            print("Authentication failed")

    if user is None:
        return {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }