# -*- coding: utf-8 -*-
# Django settings for social pinax project.

import sys
import os.path
import posixpath
import pinax
import logging

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = "default"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
     ("Alex Marandon", "al@smeuh.org"),
]

CONTACT_EMAIL = 'al@smeuh.org'

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": os.path.join(PROJECT_ROOT, "dev.sqlite3"),                       # Or path to database file if using sqlite3.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Europe/Paris"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "fr"

SITE_ID = 1
SITE_NAME = 'MySmeuh'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/media/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
    os.path.join(PINAX_ROOT, "media", PINAX_THEME),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    "account.middleware.LocaleMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
    "pagination.middleware.PaginationMiddleware",
    "django_sorting.middleware.SortingMiddleware",
    "pinax.middleware.security.HideSensistiveFieldsMiddleware",
#    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "smeuhsocial.middleware.WsgiLogErrors",
]

ROOT_URLCONF = "smeuhsocial.urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "staticfiles.context_processors.static_url",
    "pinax.core.context_processors.pinax_settings",
    "account.context_processors.account",
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "smeuhsocial.context_processors.combined_inbox_count",
]

COMBINED_INBOX_COUNT_SOURCES = [
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "pinax.templatetags",
    
    # external
    "compressor",
    "notification", # must be first
    "django.contrib.staticfiles",
    "mailer",
    "uni_form",
    "django_openid",
    "ajax_validation",
    "timezones",
    "emailconfirmation",
    "pagination",
    "friends",
    "messages",
    "threadedcomments",
    "tagging",
    "photologue",
    "avatar",
    "microblogging",
    "django_sorting",
    "django_markup",
    "markup_deprecated",
    "tagging_ext",
    'bootstrap3',
    "django_extensions",
    "django_bleach",
    
    # Pinax
    "account",
    "pinax.apps.analytics",
    "profiles",
    "photos",
    "apps.threadedcomments_extras",
    
    # project
    "about",
    "audiotracks",
    "smeuhoverride",
    "timeline",
    "artist",
    "blog"
    
   
]


MIGRATION_MODULES = {
    'django_openid': 'migrations.django_openid',
}

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = "none"
MARKUP_CHOICES = [
    ("markdown", u"Markdown"),
    ("restructuredtext", u"reStructuredText"),
]

MARKUP_SETTINGS = {
    'restructuredtext': { 
        'settings_overrides': {
            'initial_header_level': 2 
        } 
    }
}


AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

if 'test' in sys.argv:
    AUTHENTICATION_BACKENDS = [
        "account.auth_backends.AuthenticationBackend",
    ]
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
else:
    AUTHENTICATION_BACKENDS = [
        "django_auth_ldap.backend.LDAPBackend",
        "account.auth_backends.AuthenticationBackend",
    ]

AUTHENTICATION_BACKENDS.append(
    'django.contrib.auth.backends.ModelBackend')

LOGIN_URL = "/account/login/" # @@@ any way this can be a url name?
LOGIN_REDIRECT_URLNAME = "home"

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

ugettext = lambda s: s
LANGUAGES = [
    ("fr", u"Français"),
    ("en", u"English"),
]

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, "locale"),
    os.path.join(PINAX_ROOT, "locale"),
)

YAHOO_MAPS_API_KEY = "..."

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    "cloak_email_addresses": True,
    "file_insertion_enabled": False,
    "raw_enabled": False,
    "warning_stream": NullStream(),
    "strip_comments": True,
}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ""

#DEBUG_TOOLBAR_CONFIG = {
#    "INTERCEPT_REDIRECTS": False,
#}


AVATAR_DEFAULT_URL = "/media/static/pinax/img/avatar-defaut.png"
AVATAR_GRAVATAR_BACKUP = False

import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType

AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=people,o=loc",
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# This doesn't work very well
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "sn",
    "last_name": "givenName",
}

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=people,o=loc",
    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)

AUTH_LDAP_GROUP_TYPE = PosixGroupType()

ALLOWED_HOSTS = ['my.smeuh.org']

ldap_log = logging.getLogger('django_auth_ldap')
ldap_log_handler = logging.StreamHandler()
ldap_log_handler.setLevel(logging.DEBUG)
ldap_log.addHandler(ldap_log_handler)

AUDIOTRACKS_MODEL = 'smeuhoverride.Track'
AUDIOTRACKS_PER_PAGE = 6

BLEACH_ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
    'ul', 'strong', 'ul' 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote',
    'div', 'pre', 'span', 'tt', 'table', 'tr', 'td', 'th', 'img', 'audio',
    'video',
]


BLEACH_MEDIA_ATTRIBUTES = ['src', 'height', 'width', 'alt', 'controls']

BLEACH_ALLOWED_ATTRIBUTES = {
    '*': ['class', 'title'],
    'a': ['href'],
    'img': BLEACH_MEDIA_ATTRIBUTES,
    'video': BLEACH_MEDIA_ATTRIBUTES,
    'audio': BLEACH_MEDIA_ATTRIBUTES,
}




DEFAULT_MAX_COMMENT_LENGTH = 100000

SECRET_KEY = 'coin'
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass

if os.environ.get('DJANGO_TEST_FAST'):
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['default']['NAME'] = ':memory:'
