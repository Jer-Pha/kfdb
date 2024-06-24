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
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_json_api",
    "django_filters",
    "drf_spectacular",
]

INSTALLED_APPS = PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    SECRET_KEY = getenv("SECRET_KEY").strip()
    ALLOWED_HOSTS = [
        s.strip() for s in getenv("ALLOWED_HOSTS").strip().split(",")
    ]
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
    }
    # AWS
    AWS_S3_ACCESS_KEY_ID = getenv("AMZ_S3_ACCESS_KEY_ID").strip()
    AWS_S3_SECRET_ACCESS_KEY = getenv("AMZ_S3_SECRET_ACCESS_KEY").strip()
    AWS_STORAGE_BUCKET_NAME = getenv("AMZ_STORAGE_BUCKET_NAME").strip()
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_MAX_MEMORY_SIZE = 500000
    AWS_S3_REGION_NAME = getenv("AMZ_S3_REGION_NAME").strip()
    AWS_S3_SIGNATURE_VERSION = getenv("AMZ_S3_SIGNATURE_VERSION").strip()

else:
    SECRET_KEY = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrZsTtUuVvWwXxYy"
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    INTERNAL_IPS = ["127.0.0.1"]
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
    }
    MEDIA_URL = "/media/"
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

STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
}

STATICFILES_DIRS = [
    path.join(BASE_DIR, "assets", "dist"),
    path.join(BASE_DIR, "apps", "core", "static"),
    # Only available after running `npm install`
    path.join(BASE_DIR, "node_modules/htmx.org/dist"),
]

STATIC_URL = "/static-files/"
STATIC_ROOT = path.join(BASE_DIR, "staticfiles")
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
        # If you're performance testing, you will want to use the
        # browseable API without forms, as the forms can generate their
        # own queries. If performance testing, enable:
        # 'example.utils.BrowsableAPIRendererWithoutForms',
        # Otherwise, to play around with the browseable API, enable:
        "rest_framework_json_api.renderers.BrowsableAPIRenderer",
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
    "VERSION": "0.2.2",
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
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF
CSRF_COOKIE_NAME = "kfdb_csrf"
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
