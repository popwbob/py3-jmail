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

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yof4hw@+2appuvzg(v+5twtf&qduqn8zxwqzj75dy0k&kac0#2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

TEMPLATE_DEBUG = True
TEMPLATE_DIRS = ('/'.join([BASE_DIR, 'templates']),)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader'
)
TEMPLATE_STRING_IF_INVALID = 'TMPL_MISS:[%s]'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jmail.user',
    'jmail.macct',
    'jmail.msg',
    'jmail.mdir',
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
        'NAME': os.path.join(BASE_DIR, '/opt/jmail/db.sqlite3'),
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
STATICFILES_DIRS = ('/'.join([BASE_DIR, 'static']),)

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
        'LOCATION': '/opt/jmail/cache/default',
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'jmail_cache',
        'VERSION': 0,
    },
    'mdir-cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/opt/jmail/cache/mdir',
        'TIMEOUT': 60,
        'KEY_PREFIX': 'jmail_cache_mdir',
        'VERSION': 0,
    }
}

JMAIL = {
    'DATE_HEADER_FORMAT': '%a, %d %b %Y %H:%M:%S %z',
    'MDIR_CACHE_ENABLE': True,
}
