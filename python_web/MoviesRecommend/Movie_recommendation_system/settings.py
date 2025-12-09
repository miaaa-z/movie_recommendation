import os

# Project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Project secret key
SECRET_KEY = 'bhml2023(140w8x3ktw=yzm0=@3h5wr=$$4s!g(s-^s7^@e5=kz'

# Debug mode (True = development mode, shows detailed error info)
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = []

# Registered apps
INSTALLED_APPS = [
    'django.contrib.admin',           # Django built-in admin interface
    'django.contrib.auth',            # Authentication system
    'django.contrib.contenttypes',    # Content type framework
    'django.contrib.sessions',        # Session management
    'django.contrib.messages',        # Messaging framework
    'django.contrib.staticfiles',     # Static file management
    'movie'                           # Our movie recommendation system app
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration
ROOT_URLCONF = 'Movie_recommendation_system.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'movie.context_processors.movie_user'
            ],
            'builtins': ['django.templatetags.static']
        },
    },
]

# WSGI application
WSGI_APPLICATION = 'Movie_recommendation_system.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_movie_recommend',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}

# Password validation
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
# Django's built-in password validation:
# MinimumLengthValidator: ensures a minimum length (default is 8)
# CommonPasswordValidator: prevents using common passwords (e.g., 123456)
# NumericPasswordValidator: prevents using only numeric passwords

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']
