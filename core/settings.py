import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from django.templatetags.static import static


load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

APPLICATION_NAME = os.getenv("APPLICATION_NAME")

APPLICATION_ALIAS = os.getenv("APPLICATION_ALIAS")


# Application definition

INSTALLED_APPS = [
    "daphne",
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    "imagekit",
    
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "phonenumber_field",
    "timezone_field",

    "apps.accounts",
    "apps.tokens",
    "apps.interns",
]

MIDDLEWARE = [
    "helpers.django.response.middlewares.MaintenanceMiddleware",  # Handles application maintenance mode
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

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
                "helpers.django.context_processors.application",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

ASGI_APPLICATION = "core.asgi.application"

CONN_MAX_AGE = 60

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


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

AUTH_USER_MODEL = "accounts.UserAccount"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

STATIC_ROOT = BASE_DIR / "static/"

STATICFILES_DIRS = [
    BASE_DIR / "core/static",
]

MEDIA_URL = "media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#################
# EMAIL CONFIGS #
#################

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv("EMAIL_HOST")

EMAIL_PORT = os.getenv("EMAIL_PORT")

EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"

EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


LOGIN_URL = "accounts:signin"

if DEBUG is False:
    # PRODUCTION SETTINGS ONLY
    ALLOWED_HOSTS = ["*"]

else:
    # DEVELOPMENT SETTINGS ONLY
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]


CSRF_TRUSTED_ORIGINS = ["https://*"]

OTP_LENGTH = 6

OTP_VALIDITY_PERIOD = 60 * 30

MEMR_SITE_URL = "https://lagosmemr.com/"


UNFOLD = {
    "STYLES": [
        lambda request: static("core//styles//admin.css"),
    ],
}

####################
# HELPERS SETTINGS #
####################

HELPERS_SETTINGS = {
    "MAINTENANCE_MODE": {
        "status": os.getenv("MAINTENANCE_MODE", "off").lower() in ["on", "true"],
        "message": os.getenv("MAINTENANCE_MODE_MESSAGE", "default:minimal_dark"),
    },
}


