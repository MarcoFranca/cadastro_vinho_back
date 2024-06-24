# users/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            logger.debug("Social account already exists for user.")
            return

        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                user = CustomUser.objects.get(email=email)
                logger.debug(f"Found existing user with email: {email}")

                sociallogin.connect(request, user)
                raise ImmediateHttpResponse(redirect('/accounts/profile/'))
            else:
                logger.debug("Email not found in social account extra_data.")
        except CustomUser.DoesNotExist:
            logger.debug(f"No user found with email: {email}")
        except Exception as e:
            logger.error(f"Error during social login: {str(e)}")
