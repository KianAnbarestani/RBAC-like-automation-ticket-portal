# -*- coding: utf-8 -*-

import os
import socket
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# For development purposes, a default key is provided.
# In production, ensure to set DJANGO_SECRET_KEY as an environment variable.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', ')tbz@z2px&&9@+l6$8o$*z8m2&%az1c(5c#&7!g-x)lci&dr4t')

# Determine if the application is running in production
# For development, DJANGO_PRODUCTION_DOMAIN can be set to your local domain
PRODUCTION_DOMAIN = os.environ.get("DJANGO_PRODUCTION_DOMAIN", "mysite.local")

if socket.gethostname() == PRODUCTION_DOMAIN:
    # Production-specific settings
    DEBUG = False
    TEMPLATE_DEBUG = False  # Deprecated in newer Django versions; consider removing if using Django >= 1.8
    ALLOWED_HOSTS = ['mysite.local', 'your_production_domain.com']  # Replace with your production domain
    # SSL/HTTPS settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Development-specific settings
    DEBUG = True
    TEMPLATE_DEBUG = True  # Deprecated in newer Django versions; consider removing if using Django >= 1.8
    ALLOWED_HOSTS = ['mysite.local', 'localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'main',
]

# Template configuration
# Updated to use the TEMPLATES setting instead of TEMPLATE_CONTEXT_PROCESSORS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Ensure this directory exists
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required for admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# If using older Django versions (<1.8), you might still need TEMPLATE_CONTEXT_PROCESSORS
# Uncomment the following lines if you're on an older version
# TEMPLATE_CONTEXT_PROCESSORS = (
#     'django.core.context_processors.request',
# )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tickets.urls'

WSGI_APPLICATION = 'tickets.wsgi.application'

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Or your preferred DB engine
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", os.path.join(BASE_DIR, 'staticfiles'))

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", os.path.join(BASE_DIR, 'media'))

# On login do not redirect to "/accounts/profile/" but "/inbox/"
LOGIN_REDIRECT_URL = "/inbox/"

# In urls.py the function "logout_then_login" is used to log out
# Changing the default value from "/accounts/login/" to "/"
LOGIN_URL = "/"

# Django Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Define who gets code error notifications.
# When DEBUG=False and a view raises an exception,
# Django will email these people with the full exception information.
ADMINS = [
    (os.environ.get("DJANGO_ADMIN_NAME", "Admin"), os.environ.get("DJANGO_ADMIN_EMAIL", "admin@example.com")),
]

# Specifies who should get broken link notifications when
# BrokenLinkEmailsMiddleware is enabled.
MANAGERS = ADMINS

# Email delivery to local Postfix-Installation
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "localhost")
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.environ.get("DJANGO_LOG_FILE", os.path.join(BASE_DIR, 'django.log')),
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'main': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
}
