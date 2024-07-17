import logging
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
from instaapp.models.user import CustomUser
import random
from django.core.mail import send_mail
from django.core.cache import cache

logger = logging.getLogger(__name__)

User = get_user_model()

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email):
    code = generate_verification_code()
    subject = '이메일 인증 코드'
    message = f'귀하의 인증 코드는 {code} 입니다. 이 코드는 10분간 유효합니다.'
    from_email = 'ori178205@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)
    
    # 캐시에 인증 코드 저장 (10분 동안 유효)
    cache_key = f'verification_code_{email}'
    cache.set(cache_key, code, 600)
    
    # 디버그 로그 추가
    print(f"Stored code in cache: {code}")
    print(f"Retrieved code from cache: {cache.get(cache_key)}")

    return code

def verify_email_code(email, code):
    cache_code = cache.get(f'verification_code_{email}')
    return cache_code == code

def create_user(user_data):
    bio = user_data.pop('bio', '')
    birth_date = user_data.pop('birth_date', '')
    website = user_data.pop('website', '')
    profile_picture = user_data.pop('profile_picture', None)
    
    # 필수 필드 확인
    username = user_data.get('username')
    email = user_data.get('email')
    password = user_data.pop('password', None)  # password를 pop해서 따로 처리
    
    print(f"Received user data: {user_data}")  # 디버깅을 위한 출력
    
    if not username or not email or not password:
        raise ValueError("Username, email, and password are required")
    
    # 중복 확인
    if CustomUser.objects.filter(username=username).exists():
        raise ValidationError("A user with that username already exists.")
    
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError("A user with that email already exists.")
    
    try:
        # create_user 메서드 호출
        user = CustomUser.objects.create_user(
            password=password,
            **user_data
        )
        
        user.bio = bio
        user.birth_date = birth_date
        user.website = website
        user.profile_picture = profile_picture
        user.save()
        
        return user
    except IntegrityError:
        # 데이터베이스 레벨에서의 중복 체크
        raise ValidationError("An error occurred while creating the user. The username or email may already be in use.")

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
        except CustomUser.DoesNotExist:
            pass
    else:
        try:
            user = CustomUser.objects.get(username=username_or_email)
        except CustomUser.DoesNotExist:
            pass

    if user and user.check_password(password):
        if user.is_active:
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'is_active': True,
                'message': 'Logged in successfully.'
            }
        else:
            # 비활성화된 계정을 위한 임시 토큰
            temp_token = AccessToken.for_user(user)
            temp_token.set_exp(lifetime=timedelta(minutes=15))
            return {
                'temp_token': str(temp_token),
                'user_id': user.id,
                'is_active': False,
                'message': 'Account is deactivated. Use this token to reactivate or delete your account.'
            }
    
    raise ValidationError("Invalid credentials")

def reactivate_user(user_id):
    logger.debug(f"Attempting to reactivate user with id: {user_id}")
    try:
        user = CustomUser.objects.get(id=user_id)
        logger.debug(f"Found user: {user}, current is_active: {user.is_active}")
        if user.is_active:
            logger.warning("Attempt to reactivate an already active account")
            raise ValidationError("This account is already active")
        user.is_active = True
        user.save()
        logger.debug(f"User reactivated successfully, new is_active: {user.is_active}")
        return user
    except CustomUser.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        raise ValidationError("User not found")

def delete_user(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return True
    except CustomUser.DoesNotExist:
        raise ValidationError("User not found")