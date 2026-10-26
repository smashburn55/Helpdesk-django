from pathlib import Path
import os

def load_env_file(path):
    """Load local environment settings without overriding existing variables."""
    if not path.is_file():
        return

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file(Path(__file__).resolve().parent.parent / ".env")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
# SECURITY WARNING: don't run with debug turned on in production!
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "ticketApp",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ticketSite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ticketSite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

# Automatically detect the hostname of the machine executing the code
# Configuration is selected explicitly through environment variables.
# Mac and DigitalOcean each have their own private .env file.

DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

if DJANGO_ENV == "production":
    ALLOWED_HOSTS = [
        "mashburndatasystems.com",
        "www.mashburndatasystems.com",
        "209.97.146.203",
    ]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DJANGO_DB_NAME"],
        "USER": os.environ["DJANGO_DB_USER"],
        "PASSWORD": os.environ["DJANGO_DB_PASSWORD"],
        "HOST": os.environ["DJANGO_DB_HOST"],
        "PORT": os.environ["DJANGO_DB_PORT"],
    }
}

# Keep the rest of your settings (STATIC_URL, STATIC_ROOT, etc.) exactly the same below!


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "static/"
import os
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

# MODERN DJANGO 6.1+ OUTBOUND SMTP MAIL ROUTER CHANNELS
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": "ams3.greengeeks.net",  # <-- UPDATED TO THE DIRECT MASTER SMTP ENDPOINT
            "port": 465,
            "use_ssl": True,
            "username": "support@mashburndatasystems.com",
            "password": "Tinman55!",
        },
    },
}

# --- COMMERCIAL CORS SAFE AUTHORIZATION RULES ---

# During local testing, this allows your web form to communicate seamlessly
CORS_ALLOW_ALL_ORIGINS = True

# When you deploy your software to production, change the variable to this to stay secure:
# CORS_ALLOWED_ORIGINS = [
#     "https://mashburndatasystems.com",
#     "https://mashburndatasystems.com",
# ]

# --- GREENGEEKS PRODUCTION SMTP EMAIL ROUTING ---
# --- MODERN DJANGO 6.1+ GREENGEEKS PRODUCTION EMAIL CONFIGURATION ---

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": "://mashburndatasystems.com",
            "port": 465,
            "use_ssl": True,
            "username": "support@mashburndatasystems.com",
            "password": "Tinman55!",
        },
    },
}

# This setting remains outside the dictionary to handle branding defaults
DEFAULT_FROM_EMAIL = "Mashburn Data Support <support@mashburndatasystems.com>"

# Forces all @login_required security decorators to redirect straight to your admin login desk
LOGIN_URL = '/admin/login/'

