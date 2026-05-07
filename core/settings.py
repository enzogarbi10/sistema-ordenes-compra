"""
Django settings for gestion_ordenes project.
"""

import os
import sys
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env (for local development)
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ─── Security ──────────────────────────────────────────────────────────────────

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-7#55)(9g9604m5yz!3%tpeqrfn)%avtky1e5xrk)fhrrx7*sqc')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://127.0.0.1',
    'http://localhost',
] + [
    origin for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if origin
]

# ─── Security Headers (solo en producción, cuando DEBUG=False) ─────────────────

if not DEBUG:
    # Forzar HTTPS: redirige HTTP → HTTPS
    SECURE_SSL_REDIRECT = True

    # HSTS: el navegador recordará usar HTTPS por 1 año
    SECURE_HSTS_SECONDS = 31536000          # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # También aplica a subdominios
    SECURE_HSTS_PRELOAD = True              # Permite entrar en la lista preload de browsers

    # Cookies solo por HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Proxy headers (Waitress + IIS)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ─── HTTP Security Headers ─────────────────────────────────────────────────────
# Protección XSS del navegador (legacy browsers)
SECURE_BROWSER_XSS_FILTER = True

# Evita que el navegador adivine el tipo de contenido (MIME sniffing)
SECURE_CONTENT_TYPE_NOSNIFF = True

# Política de referrer: no envía la URL completa al salir del sitio
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Clickjacking: impide que el sitio sea embebido en iframes externos
X_FRAME_OPTIONS = 'DENY'

# Cookies de sesión: no accesibles por JavaScript
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # Debe ser False para que el JS pueda leer el token CSRF

# URL del panel de administración (cambiada para dificultar ataques automáticos)
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')

# ─── Applications ──────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'ordenes_trabajo',
    'web',
    'postprensa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ─── Database ──────────────────────────────────────────────────────────────────
# En producción (Render) usa DATABASE_URL (PostgreSQL)
# En desarrollo local usa SQLite

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── Password Validation ───────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},  # Mínimo 10 caracteres
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalization ──────────────────────────────────────────────────────

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# ─── Static Files ──────────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Compatibilidad con django-cloudinary-storage (no compatible con Django 5.x aún)
# Le indica que los archivos estáticos NO van a Cloudinary, solo los media.
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ─── Media Files → Almacenamiento Local ────────────────────────────────────────

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# ─── Default Primary Key ───────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Email (SendGrid) ──────────────────────────────────────────────────────────

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = 'graficamelfa@gmail.com'

# ─── Auth ──────────────────────────────────────────────────────────────────────

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# ─── Session ───────────────────────────────────────────────────────────────────

SESSION_COOKIE_AGE = 28800         # 8 horas (suficiente para una jornada laboral completa)
SESSION_SAVE_EVERY_REQUEST = True  # Reiniciar timer con cada request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Mantener sesión aunque se cierre el navegador
SESSION_COOKIE_NAME = 'sid'        # Nombre genérico (no revela el framework)

# ─── Logging de seguridad ──────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB por archivo
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'django_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django': {
            'handlers': ['django_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Crear carpeta de logs si no existe
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
