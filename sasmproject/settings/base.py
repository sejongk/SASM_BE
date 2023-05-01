"""
Django settings for sasmproject project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os
import json
import sys
import environ
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env(DEBUG=(bool, True))

# env_file = os.path.join(BASE_DIR, '.env')
# if os.path.exists(env_file):
#     environ.Env.read_env(
#         env_file=env_file
#     )

SECRET_KEY = env('SASM_BE_SECRET_KEY')

STATE = env('SASM_BE_STATE')
KAKAO_REST_API_KEY = env('SASM_BE_KAKAO_REST_API_KEY')
KAKAO_SECRET_KEY = env('SASM_BE_KAKAO_SECRET_KEY')
SOCIAL_AUTH_GOOGLE_CLIENT_ID = env('SASM_BE_SOCIAL_AUTH_GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_SECRET = env('SASM_BE_SOCIAL_AUTH_GOOGLE_SECRET')
NAVER_CLIENT_ID = env('SASM_BE_NAVER_CLIENT_ID')
NAVER_SECRET_KEY = env('SASM_BE_NAVER_SECRET_KEY')

NAVER_STATIC_MAP_CLIENT_ID = env('SASM_BE_NAVER_STATIC_MAP_CLIENT_ID')
NAVER_STATIC_MAP_SECRET_KEY = env('SASM_BE_NAVER_STATIC_MAP_SECRET_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '3.38.89.18']

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]
PROJECT_APPS = [
    "users.apps.UsersConfig",
    "places.apps.PlacesConfig",
    "stories.apps.StoriesConfig",
    "core.apps.CoreConfig",
    "sdp_admin.apps.SdpAdminConfig",
    "community.apps.CommunityConfig",
    "curations.apps.CurationsConfig"
]
THIRD_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.naver',
    'knox',
    'debug_toolbar',
    'corsheaders',
    'drf_yasg',
    'storages',
    'silk',
    'sentry_sdk',
]
INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_APPS

SITE_ID = 1

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'silk.middleware.SilkyMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sasmproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sasmproject.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated", ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    'EXCEPTION_HANDLER': 'sasmproject.exceptions.custom_exception_handler',
}

# username 필드 사용 X email 필드 사용
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

REST_USE_JWT = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=28),
    'ROTATE_REFRESH_TOKENS': False,  # true면 토큰 갱신 시 refresh도 같이 갱신
    'BLACKLIST_AFTER_ROTATION': True,
}


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

# 이메일 인증
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = env('SASM_BE_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('SASM_BE_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('SASM_BE_EMAIL_HOST_USER')

# corheaders
# CORS_ORIGIN_WHITELIST = ('http://127.0.0.1:3000', 'http://localhost:3000', 'http://127.0.0.1:8000',
#                        'https://api.sasmbe.com', 'https://main.d2hps9gsgzjxq.amplifyapp.com',
#                        'https://www.sasm.co.kr')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

# aws s3
# AWS 정보
AWS_STORAGE_BUCKET_NAME = env('SASM_BE_AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = env('SASM_BE_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('SASM_BE_AWS_SECRET_ACCESS_KEY')

AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)

# 이거없어서 엄청 헤맴.. (AWS_S3_HOST, AWS_QUERYSTRING_AUTH )
AWS_S3_HOST = 's3.ap-northeast-2.amazonaws.com'
AWS_QUERYSTRING_AUTH = False

# static files setting
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'sasmproject.custom_storages.StaticStorage'
STATIC_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN,
                                     STATICFILES_LOCATION)

# media files setting
MEDIAFILES_LOCATION = 'media'
MEDIA_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'sasmproject.custom_storages.MediaStorage'

# STATIC_URL = '/static/'
# MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]  # debug-tool-bar
INTERNAL_IPS = [
    '127.0.0.1',
]
# django silk
SILKY_PYTHON_PROFILER = True
SILKY_INTERCEPT_PERCENT = 5
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True

# drf-yasg
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
    },
    'DEFAULT_AUTO_SCHEMA_CLASS': 'core.inspectors.SerializerExampleSchema',
}
