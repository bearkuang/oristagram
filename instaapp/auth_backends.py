import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned

logger = logging.getLogger(__name__)

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info(f"Attempting authentication for username: {username}")
        
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            logger.info(f"Using {User.USERNAME_FIELD}: {username}")

        try:
            if '@' in username:
                logger.info(f"Attempting to find user by email: {username}")
                user = User.objects.get(email=username)
            else:
                logger.info(f"Attempting to find user by username: {username}")
                user = User.objects.get(username=username)
            
            logger.info(f"User found: {user.username}")
        except User.DoesNotExist:
            logger.warning(f"User not found for {username}")
            return None
        except MultipleObjectsReturned:
            logger.error(f"Multiple users found for {username}")
            return None

        if user.check_password(password):
            logger.info(f"Password check passed for user: {user.username}")
            if self.user_can_authenticate(user):
                logger.info(f"Authentication successful for user: {user.username}")
                return user
            else:
                logger.warning(f"User {user.username} cannot be authenticated")
        else:
            logger.warning(f"Password check failed for user: {user.username}")
        
        return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            logger.info(f"User retrieved: {user.username}")
            return user
        except User.DoesNotExist:
            logger.warning(f"User not found for id: {user_id}")
            return None