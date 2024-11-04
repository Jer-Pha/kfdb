"""
Django settings for kfdb project.

Generated by 'django-admin startproject' using Django 5.0.6.
"""

from os import getenv, path
from pathlib import Path
from sys import argv

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = getenv("DEBUG", "TRUE").strip() == "TRUE"

PROJECT_APPS = [
    "apps.channels",
    "apps.core",
    "apps.edits",
    "apps.hosts",
    "apps.shows",
    "apps.videos",
]

THIRD_PARTY_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_json_api",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
]

INSTALLED_APPS = PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SECRET_KEY = getenv(
    "SECRET_KEY",
    default="AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrZsTtUuVvWwXxYy",
).strip()

ALLOWED_HOSTS = [
    s.strip()
    for s in getenv(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1",
    ).split(",")
]

if not DEBUG:
    CORS_ALLOWED_ORIGINS = [
        s.strip() for s in getenv("CORS_ALLOWED_ORIGINS").strip().split(",")
    ]
    CORS_URLS_REGEX = r"^/api/news/.*$"
    DATABASES = {
        "default": {
            "ENGINE": getenv("SQL_ENGINE").strip(),
            "NAME": getenv("SQL_NAME").strip(),
            "HOST": getenv("SQL_HOST").strip(),
            "PORT": getenv("SQL_PORT").strip(),
            "USER": getenv("SQL_USER").strip(),
            "PASSWORD": getenv("SQL_PASSWORD").strip(),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "charset": "utf8mb4",
            },
        },
    }
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage.CompressedManifestStaticFilesStorage"
            ),
        },
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"

    # AWS
    AWS_S3_ACCESS_KEY_ID = getenv("AMZ_S3_ACCESS_KEY_ID").strip()
    AWS_S3_SECRET_ACCESS_KEY = getenv("AMZ_S3_SECRET_ACCESS_KEY").strip()
    AWS_STORAGE_BUCKET_NAME = getenv("AMZ_STORAGE_BUCKET_NAME").strip()
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_MAX_MEMORY_SIZE = 500000
    AWS_S3_REGION_NAME = getenv("AMZ_S3_REGION_NAME").strip()
    AWS_S3_SIGNATURE_VERSION = getenv("AMZ_S3_SIGNATURE_VERSION").strip()

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": getenv("REDIS_LOC", "").strip(),
        }
    }

else:
    INTERNAL_IPS = ["127.0.0.1"]
    CORS_ORIGIN_ALLOW_ALL = True
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    if "test" not in argv:
        INSTALLED_APPS += [
            "debug_toolbar",
        ]
        MIDDLEWARE += [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.global_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation"
            + ".UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

STATICFILES_DIRS = [
    path.join(BASE_DIR, "assets", "dist"),
    path.join(BASE_DIR, "apps", "core", "static"),
    # Only available after running `npm install`
    path.join(BASE_DIR, "node_modules/htmx.org/dist"),
    path.join(BASE_DIR, "node_modules/chart.js/dist"),
]

STATIC_URL = "/static-files/"
STATIC_ROOT = path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": (
        "rest_framework_json_api.exceptions.exception_handler"
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_json_api.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
    ),
    "DEFAULT_METADATA_CLASS": (
        "rest_framework_json_api.metadata.JSONAPIMetadata"
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_json_api.filters.QueryParameterValidationFilter",
        "rest_framework_json_api.filters.OrderingFilter",
        "rest_framework_json_api.django_filters.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ),
    "SEARCH_PARAM": "filter[search]",
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "vnd.api+json",
    # Added
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular_jsonapi.schemas.openapi.JsonApiAutoSchema",
    "DEFAULT_PAGINATION_CLASS": "drf_spectacular_jsonapi.schemas.pagination.JsonApiPageNumberPagination",
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Kinda Funny Database API",
    "DESCRIPTION": (
        "Four, sometimes five, best friends gather around this table."
    ),
    "VERSION": "1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Added
    "COMPONENT_SPLIT_REQUEST": True,
    "PREPROCESSING_HOOKS": [
        "drf_spectacular_jsonapi.hooks.fix_nested_path_parameters"
    ],
}

# Cookies
KFDB_COOKIE_SALT = getenv(
    "KFDB_COOKIE_SALT", "abcdefghijklmnopqrstuvwxyz123456"
).strip()

# Session
SESSION_COOKIE_NAME = "kfdb_session"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF
CSRF_COOKIE_NAME = "kfdb_csrf"
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
CSRF_TRUSTED_ORIGINS = ["https://*.kfdb.app/"]

# Video Update Keys
PATREON_RSS_FEED = getenv("PATREON_RSS_FEED", "").strip()
YOUTUBE_API_KEY = getenv("YOUTUBE_API_KEY", "").strip()

# Redis
if DEBUG and "test" not in argv:
    from decouple import config

    REDIS_HOST = config("REDIS_HOST", default="")
    REDIS_PORT = config("REDIS_PORT", default="")
    REDIS_PW = config("REDIS_PW", default="")
else:
    REDIS_HOST = getenv("REDIS_HOST", default="").strip()
    REDIS_PORT = getenv("REDIS_PORT", default="").strip()
    REDIS_PW = getenv("REDIS_PW", default="").strip()
