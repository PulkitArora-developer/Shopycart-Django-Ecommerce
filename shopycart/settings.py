import os
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = '5wr&o@kd@63=di%3vqzqw_cdk^qvtttzyb^%yg%i^xbl#%k__3'

DEBUG = False

ALLOWED_HOSTS = ['shopycart-ecommerce.herokuapp.com','127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mysite.apps.MysiteConfig',
    'category.apps.CategoryConfig',
    'accounts.apps.AccountsConfig',
    'shop.apps.ShopConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'admin_honeypot',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware', # Logout after inactive
]

SESSION_EXPIRE_SECONDS = 7200  # 2 hour   # How much time session expire after logout  # 1 hour = 3600
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = 'accounts/login'

ROOT_URLCONF = 'shopycart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_list',
                'cart.context_processors.cart_quantity'
            ],
        },
    },
]

WSGI_APPLICATION = 'shopycart.wsgi.application'

AUTH_USER_MODEL = 'accounts.Account'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR,'static')
STATIC_URL = '/static/'


MEDIA_ROOT = os.path.join(BASE_DIR,'media')
MEDIA_URL = '/media/'


# SMTP CONFIGURATION

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apulkit673@gmail.com'
EMAIL_HOST_PASSWORD = 'Pulkit@2000'
EMAIL_USE_TLS = True
