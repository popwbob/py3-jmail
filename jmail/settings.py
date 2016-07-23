"""
Django settings for jmail project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

JMAIL_DATA_DIR = '/opt/jmail'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yof4hw@+2appuvzg(v+5twtf&qduqn8zxwqzj75dy0k&kac0#2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                #~ 'django.template.loaders.app_directories.Loader',
            ],
            'string_if_invalid': 'TMPL_MISS:[%s]',
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
            ],
        },
    }
]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jmail.user.apps.JMailUserConfig',
    'jmail.macct.apps.JMailMAcctConfig',
    'jmail.msg.apps.JMailMsgConfig',
    'jmail.mdir.apps.JMailMDirConfig',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'jmail.urls'
WSGI_APPLICATION = 'jmail.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(JMAIL_DATA_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# 1209600 -> 2 weeks
CSRF_COOKIE_AGE = 1209600
CSRF_COOKIE_NAME = 'jmail_token'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_NAME = 'jmail_sid'

#~ LOGGING = {
    #~ 'version': 1,
    #~ 'disable_existing_loggers': False,
    #~ 'handlers': {
        #~ 'file': {
            #~ 'level': 'DEBUG',
            #~ 'class': 'logging.FileHandler',
            #~ 'filename': '/tmp/django-debug.log',
        #~ },
    #~ },
    #~ 'loggers': {
        #~ 'django.db.backends': {
            #~ 'handlers': ['file'],
            #~ 'level': 'DEBUG',
            #~ 'propagate': True,
        #~ },
    #~ },
#~ }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(JMAIL_DATA_DIR, 'cache', 'default'),
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'jmail_cache',
        'VERSION': 0,
    },
    'mdir-cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(JMAIL_DATA_DIR, 'cache', 'mdir'),
        'TIMEOUT': 15,
        'KEY_PREFIX': 'jmail_cache_mdir',
        'VERSION': 0,
    }
}

JMAIL = {
    #~ 'DATA_DIR': JMAIL_DATA_DIR,
    #~ 'CONF_LOCAL': os.path.join(JMAIL_DATA_DIR, 'jmail.json')
    'DATE_HEADER_FORMAT': '%a, %d %b %Y %H:%M:%S %z',
    'MDIR_CACHE_ENABLE': True,
    'MDIR_CACHE_META_TTL': 30,
    'MDIR_CACHE_DATA_TTL': 900,
    'SOCKETLIB_TIMEOUT': 10,
}
