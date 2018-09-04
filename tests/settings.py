import os

SECRET_KEY = 'roverdotcom'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'tests',
    'tests.test_app_1',
    'tests.test_app_2',
]

TEST_DATABASE = os.environ.get('TEST_DATABASE', 'sqlite')

if TEST_DATABASE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'testdb',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        }
    }
else:
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'woofwoof',
            }
    }
