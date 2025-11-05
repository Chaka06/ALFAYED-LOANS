import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-votre-cle-secrete-ici-a-changer-en-production')

# RENDER Configuration
if os.environ.get('RENDER'):
    DEBUG = True  # Temporaire pour voir l'erreur exacte
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '.render.com',
        '.onrender.com',
        'ecobank-pret.onrender.com',
        '*',  # Temporaire pour éliminer les problèmes d'host
    ]
    
    # Database configuration for Render PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
    
    # Static files configuration for production
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # LIGNE AJOUTÉE
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Media files configuration
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
    
    # Security settings for production - Temporairement désactivées pour diagnostic
    # SECURE_SSL_REDIRECT = True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
else:
    # Development settings
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    
    # Database pour développement
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
    # Static files pour développement
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [BASE_DIR / 'static']
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    
    # Media files pour développement
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'loan_system',
]

# Middleware avec WhiteNoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Pour servir les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecobank_project.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ecobank_project.wsgi.application'

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

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# WhiteNoise configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Configuration des chemins d'images pour les attestations PDF
INVESTOR_LOGO_PATH = os.path.join(BASE_DIR, 'static', 'images', 'logos', 'investor_logo.png')
MANAGER_SIGNATURE_PATH = os.path.join(BASE_DIR, 'static', 'images', 'signatures', 'manager_signature.png')
BANK_SEAL_PATH = os.path.join(BASE_DIR, 'static', 'images', 'seals', 'bank_seal.png')

# Informations de la banque
BANK_NAME = 'Investor Banque'
BANK_PHONE = '+49 157 50098219'
MANAGER_NAME = 'Damien Boudraux'
MANAGER_EMAIL = 'damien.boudraux17@outlook.fr'

# Configuration pour gérer les fichiers statiques manquants en production
if os.environ.get('RENDER'):
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]

# Configuration Email Professionnel ECOBANK - OPTIMISÉE
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.virement.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'support@virement.net'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'Ch@coulamelo72')
DEFAULT_FROM_EMAIL = 'Investor Banque <support@virement.net>'
SERVER_EMAIL = 'support@virement.net'

# Optimisations pour la vitesse
EMAIL_TIMEOUT = 30
EMAIL_CONNECTION_POOL_SIZE = 10
EMAIL_CONNECTION_POOL_KWARGS = {
    'max_connections': 10,
    'max_retries': 3,
    'retry_delay': 1,
}

# Configuration des emails automatiques
EMAIL_AUTOMATION_ENABLED = True
EMAIL_ASYNC_SENDING = True  # Envoi asynchrone pour la vitesse