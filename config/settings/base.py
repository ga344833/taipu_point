from django.utils.translation import gettext_lazy as _
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv(".env")

DJANGO_LOG_LEVEL = "DEBUG"

BASE_DIR = Path(__file__).resolve().parent.parent.parent.as_posix()

# 所有 apps 將統一放置於 ./apps/
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

ROOT_URLCONF = "config.urls"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-in-production")

# CSRF檢查開關
CSRF_CHECK = True if os.getenv("CSRF_CHECK", "false").lower() == "true" else False

# COOKIE/CSRF_COOKIE Samesite
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SAMESITE = None
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8000",
    "http://localhost:3000",
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    # Local apps
    "core",
    "apps.users",
    "apps.products",
    "apps.points",
    "apps.orders",
    "apps.payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom middlewares
    "config.middlewares.LogApiEndpointMiddleware",
    "config.middlewares.CurrentUserMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static_collect/")

# Media files (Client interactive medias)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

# User Model
AUTH_USER_MODEL = "users.User"

# Internationalization
LANGUAGE_CODE = "zh-hant"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Taipei")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF Standardized Errors
DRF_STANDARDIZED_ERRORS = {"ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True}

