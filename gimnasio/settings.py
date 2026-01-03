from pathlib import Path
import os
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SECURITY SETTINGS
# ==========================================

SECRET_KEY = config('SECRET_KEY', default='django-insecure-j)$i8#vx-^gdg#apoumb9gkb*u6b)=viy(rcm&1=jb@(f+e$l8')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='proud-integrity-production.up.railway.app,gimnasiolebloncalama.cl,www.gimnasiolebloncalama.cl,localhost,127.0.0.1', cast=Csv())

CSRF_TRUSTED_ORIGINS = [
    "https://proud-integrity-production.up.railway.app",
    "https://gimnasiolebloncalama.cl",
    "https://www.gimnasiolebloncalama.cl",
]

# ==========================================
# FLOW API CONFIGURATION
# ==========================================

FLOW_SANDBOX = config('FLOW_SANDBOX', default=True, cast=bool)

# Sandbox credentials
FLOW_SANDBOX_API_KEY = config('FLOW_SANDBOX_API_KEY', default='346F180A-05F3-4C5A-8846-20LEBCB5EF2B')
FLOW_SANDBOX_SECRET_KEY = config('FLOW_SANDBOX_SECRET_KEY', default='2f49d0c08940ba4de53d387edaf76ac3b6a93cc3')

# Production credentials
FLOW_PROD_API_KEY = config('FLOW_PROD_API_KEY', default='')
FLOW_PROD_SECRET_KEY = config('FLOW_PROD_SECRET_KEY', default='')

# ==========================================
# APPLICATION DEFINITION
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'principal',
    'tienda',
    'django.contrib.humanize',
    'participaciones',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gimnasio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gimnasio.wsgi.application'

# ==========================================
# DATABASE
# ==========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}




# ==========================================
# USER AUTH
# ==========================================

AUTH_USER_MODEL = 'principal.Miembro'
AUTHENTICATION_BACKENDS = [
    'principal.authentication.EmailOrPhoneBackend',  
    'django.contrib.auth.backends.ModelBackend',
]



# ==========================================
# PASSWORD VALIDATION
# ==========================================

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

# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = False
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
NUMBER_GROUPING = 3

# ==========================================
# STATIC FILES
# ==========================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ==========================================
# MEDIA FILES
# ==========================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==========================================
# DEFAULT PRIMARY KEY
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# EMAIL CONFIGURATION
# ==========================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='benjaminjavier46@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='mgvq uhwb ttwk lhxm')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==========================================
# LOGGING
# ==========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'principal': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tienda': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==========================================
# SECURITY SETTINGS FOR PRODUCTION
# ==========================================

if not DEBUG:
    # Railway maneja HTTPS por ti
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Seguridad del navegador
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # NO forzar redirect a HTTPS (Railway ya lo hace)
    SECURE_SSL_REDIRECT = False