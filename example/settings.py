import os

DEBUG = True

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'database.sqlite'),
    }
}

STATIC_URL = '/static/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TIME_ZONE = 'Europe/Amsterdam'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'DO NOT USE THIS KEY!'

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'user_sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'two_factor.middleware.threadlocals.ThreadLocals',
)

ROOT_URLCONF = 'example.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, 'templates')],
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

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'user_sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_email',
    'two_factor',
    'two_factor.plugins.phonenumber',
    'two_factor.plugins.email',
    'example',

    'debug_toolbar',
    'bootstrapform'
]


LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'two_factor:profile'

INTERNAL_IPS = ('127.0.0.1',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

TWO_FACTOR_CALL_GATEWAY = 'example.gateways.Messages'
TWO_FACTOR_SMS_GATEWAY = "two_factor.gateways.twilio.gateway.Twilio"
PHONENUMBER_DEFAULT_REGION = 'NL'
TWO_FACTOR_WHATSAPP_GATEWAY = TWO_FACTOR_SMS_GATEWAY
TWILIO_WHATSAPP_TWO_FACTOR_TEMPLATE_SID = "your_twilio_whatsapp_template_sid"

TWO_FACTOR_REMEMBER_COOKIE_AGE = 120  # Set to 2 minute for testing

TWO_FACTOR_PHONE_THROTTLE_FACTOR = 10
OTP_TOTP_THROTTLE_FACTOR = 10

TWO_FACTOR_WEBAUTHN_RP_NAME = 'Demo Application'

SESSION_ENGINE = 'user_sessions.backends.db'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@example.org'

SILENCED_SYSTEM_CHECKS = ['admin.E410']

try:
    from .settings_private import *  # noqa
except ImportError:
    pass
