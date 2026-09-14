from pathlib import Path

from corsheaders.defaults import default_headers
from environ import Env

env = Env()

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Django
# -----------------------------------------------------------------------------
env.read_env(
    env_file=BASE_DIR / ".env",
    overwrite=True,
)

DEBUG = env.bool(
    var="DJANGO_DEBUG",
    default=True,
)

SECRET_KEY = env("DJANGO_SECRET_KEY")

APPEND_SLASH = False

ROOT_URLCONF = "config.urls"

ASGI_APPLICATION = "config.asgi.application"

WSGI_APPLICATION = "config.wsgi.application"


# -----------------------------------------------------------------------------
# HOSTS
# -----------------------------------------------------------------------------
ALLOWED_HOSTS = env(
    var="DJANGO_ALLOWED_HOSTS",
    cast=list,
    default=[],
)


# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    *default_headers,
]

CORS_ALLOWED_ORIGINS = env(
    var="DJANGO_CORS_ALLOWED_ORIGINS",
    cast=list,
    default=[],
)

FRONTEND_URL = env(
    var="FRONTEND_URL",
    default="http://localhost:3000",
)


# -----------------------------------------------------------------------------
# CSRF
# -----------------------------------------------------------------------------
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = not DEBUG

CSRF_TRUSTED_ORIGINS = env(
    var="DJANGO_CSRF_TRUSTED_ORIGINS",
    cast=list,
    default=[],
)


# -----------------------------------------------------------------------------
# Session
# -----------------------------------------------------------------------------
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_SECURE = not DEBUG

SESSION_CACHE_ALIAS = "default"

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = not DEBUG


# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------
USE_TZ = True

TIME_ZONE = "America/Sao_Paulo"

LOCALE_PATHS = [BASE_DIR / "locale"]

LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", "English"),
    ("pt", "Portuguese"),
]


# -----------------------------------------------------------------------------
# Application
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "daphne",
    "auditlog",
    # -------------------------------------------------------------------------
    # Django Tasks
    # -------------------------------------------------------------------------
    "django_rq",
    "django_tasks",
    "django_tasks_rq",
    # -------------------------------------------------------------------------
    # DRF
    # -------------------------------------------------------------------------
    "corsheaders",
    "drf_spectacular",
    "rest_framework",
    "drf_standardized_errors",
    # -------------------------------------------------------------------------
    # Guardian (object-level permissions)
    # -------------------------------------------------------------------------
    "guardian",
    # -------------------------------------------------------------------------
    # Allauth
    # -------------------------------------------------------------------------
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.usersessions",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
]

if DEBUG:
    THIRD_PARTY_APPS.append("silk")

INSTALLED_APPS = [
    *THIRD_PARTY_APPS,
    *DJANGO_APPS,
    "apps.domains.media",
    "apps.domains.document",
    "apps.domains.form",
    "apps.domains.inbox",
    "apps.domains.sticky",
    "apps.domains.task",
    "apps.domains.workplace",
    "apps.domains.user",
    "apps.integrations.google",
    "apps.integrations.unsplash",
    "apps.common.realtime",
    "apps.common.streaming",
]


# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("silk.middleware.SilkyMiddleware")


# -----------------------------------------------------------------------------
# Template
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "django.templatetags.static",
            ],
        },
    },
]

# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

EMAIL_USE_TLS = not DEBUG
EMAIL_USE_SSL = False

# -----------------------------------------------------------------------------
# Postgres
# -----------------------------------------------------------------------------
POSTGRES_DB = env("POSTGRES_DB")
POSTGRES_USER = env("POSTGRES_USER")
POSTGRES_PASSWORD = env("POSTGRES_PASSWORD")
POSTGRES_HOST = env("POSTGRES_HOST")
POSTGRES_PORT = env("POSTGRES_PORT")

# -----------------------------------------------------------------------------
# db
# -----------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# Redis
# -----------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL")

# -----------------------------------------------------------------------------
# RQ
# -----------------------------------------------------------------------------
RQ_QUEUES = {
    "default": {
        "URL": REDIS_URL,
        "DEFAULT_TIMEOUT": 360,
    }
}

# -----------------------------------------------------------------------------
# Channels
# -----------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    }
}

# -----------------------------------------------------------------------------
# Cache
# -----------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# -----------------------------------------------------------------------------
# Tasks
# -----------------------------------------------------------------------------
TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
        "QUEUES": ["default", "special"],
    }
}

# -----------------------------------------------------------------------------
# Static
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

# -----------------------------------------------------------------------------
# MEDIA
# -----------------------------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}

# -----------------------------------------------------------------------------
# DRF
# -----------------------------------------------------------------------------
API_THROTTLE_ANON = env("API_THROTTLE_ANON", default="100/hour")
API_THROTTLE_USER = env("API_THROTTLE_USER", default="2000/hour")
API_THROTTLE_UNSPLASH = env("API_THROTTLE_UNSPLASH", default="300/hour")

API_VIEW_CACHE_TIMEOUT = env.int("API_VIEW_CACHE_TIMEOUT", default=60)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": API_THROTTLE_ANON,
        "user": API_THROTTLE_USER,
        "unsplash": API_THROTTLE_UNSPLASH,
    },
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_VERSION": "api",
    "ALLOWED_VERSIONS": ["api"],
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
}

if not DEBUG:
    REST_FRAMEWORK = {
        **REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "anon": "5000/hour",
            "user": "50000/hour",
        },
    }

# -----------------------------------------------------------------------------
# Spectacular
# -----------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "FlowWi API",
    "DESCRIPTION": "FlowWi API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# -----------------------------------------------------------------------------
# Google
# -----------------------------------------------------------------------------
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET_KEY = env("GOOGLE_CLIENT_SECRET_KEY")

GOOGLE_AI_API_KEY = env("GOOGLE_AI_API_KEY")

# -----------------------------------------------------------------------------
# Google
# -----------------------------------------------------------------------------
GITHUB_CLIENT_ID = env("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET_KEY = env("GITHUB_CLIENT_SECRET_KEY")

# -----------------------------------------------------------------------------
# Unsplash
# -----------------------------------------------------------------------------
UNSPLASH_ID = env("UNSPLASH_ID", default="")
UNSPLASH_ACCESS_KEY = env("UNSPLASH_ACCESS_KEY", default="")
UNSPLASH_SECRET_KEY = env("UNSPLASH_SECRET_KEY", default="")

# Application name Unsplash expects in the UTM parameters of every attribution link.
UNSPLASH_APP_NAME = env("UNSPLASH_APP_NAME", default="flowwi")

# How long a proxied Unsplash response stays fresh (seconds). Unsplash allows only
# 50 requests/hour on demo apps, so responses are served from Redis by default.
UNSPLASH_CACHE_TTL = env.int("UNSPLASH_CACHE_TTL", default=60 * 60 * 6)

# How long a cached response is kept around after it goes stale, so the picker keeps
# working when Unsplash is down or the hourly quota is exhausted.
UNSPLASH_CACHE_STALE_TTL = env.int("UNSPLASH_CACHE_STALE_TTL", default=60 * 60 * 24 * 7)

# -----------------------------------------------------------------------------
# Allauth
# -----------------------------------------------------------------------------
SITE_ID = 1
ALLAUTH_HEADLESS_ONLY = True

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
]

# -----------------------------------------------------------------------------
# Guardian
# -----------------------------------------------------------------------------
# Every endpoint that checks object permissions already requires authentication
# (IsAuthenticated), so guardian's anonymous-user bookkeeping is unnecessary here.
ANONYMOUS_USER_NAME = None

HEADLESS_ONLY = True
HEADLESS_SERVE_SPECIFICATION = True

HEADLESS_FRONTEND_URLS = {
    "socialaccount_login_cancelled": "/auth/login",
    "socialaccount_login_error": "/auth/login",
    "account_confirm_email": "/auth/verify-email/{key}",
    "account_reset_password_from_key": "/auth/reset-password/{key}",
}

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "password1*",
    "password2*",
]
ACCOUNT_EMAIL_VERIFICATION = "optional"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_CLIENT_ID,
            "secret": GOOGLE_CLIENT_SECRET_KEY,
        },
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "SCOPE": ["profile", "email"],
    },
    "github": {
        "APP": {
            "client_id": GITHUB_CLIENT_ID,
            "secret": GITHUB_CLIENT_SECRET_KEY,
        },
        "SCOPE": ["user:email"],
    },
}

SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# -----------------------------------------------------------------------------
# S3
# -----------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_ENDPOINT_URL = env("AWS_ENDPOINT_URL")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

# -----------------------------------------------------------------------------
# Storage
# -----------------------------------------------------------------------------
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

if not DEBUG:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "signature_version": "s3v4",
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "endpoint_url": AWS_ENDPOINT_URL,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
        },
    }


# -----------------------------------------------------------------------------
# Silk (dev only)
# -----------------------------------------------------------------------------
if DEBUG:
    SILKY_PYTHON_PROFILER = True
    SILKY_INTERCEPT_PERCENT = 100
    SILKY_AUTHENTICATION = False
    SILKY_AUTHORISATION = False
