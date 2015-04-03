import os

MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
USE_TZ = True,

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

TEMPLATE_DIRS = (os.path.join(MODULE_ROOT, 'templates'),)

INSTALLED_APPS = (
    # django modules
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # third parties
    "djbetty",
    "elastimorphic",
    "rest_framework",
    "polymorphic",
    # local apps
    "bulbs.api",
    "bulbs.campaigns",
    "bulbs.feeds",
    "bulbs.redirects",
    "bulbs.cms_notifications",
    "bulbs.videos",
    "bulbs.content",
    "bulbs.contributions",
    "bulbs.promotion",
    "bulbs.special_coverage",
    "bulbs.sections",
    # local testing apps
    "example.testcontent",
)

ROOT_URLCONF = "example.urls"

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

# django 1.7 drops some of the necessary middleware to make elastimorphic work
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'bulbs.promotion.middleware.PromotionMiddleware'
)

CELERY_ALWAYS_EAGER = True

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    )
}

SECRET_KEY = "no-op"

ES_DISABLED = False

ES_URLS = ['http://localhost:9200']