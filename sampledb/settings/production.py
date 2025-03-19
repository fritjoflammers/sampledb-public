from .base import *  # noqa: F403 F401
import django_heroku

DEBUG = False

SESSION_COOKIE_SECURE = False

ALLOWED_HOSTS = [
    "sampledb-bcf190cc0d1b.herokuapp.com",
    "sampledb.flammers.dev",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgresql-tetrahedral-50349",
        "USER": "sampledb",
        "PASSWORD": "sampledb@postgres",
        "HOST": "postgres://vqusyqdlysuitc:fa3fbf65de662ae05a78c1ebc12f72fefabacd29f04ec2bf4808a2a2fd8d4c8a@ec2-54-156-8-21.compute-1.amazonaws.com:5432/de4cpeuf6g3j8q",  # noqa: E501
        "PORT": "5432",
        "CONN_MAX_AGE": 500,
    }
}

django_heroku.settings(locals())
