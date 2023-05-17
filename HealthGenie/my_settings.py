# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-!iy!ama-6vh+i+ml2apagt@0v(naf0d&l4n3$_x8ui9t(78_-y"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pha_test',
        'USER': 'yonghoonjeon',
        'PASSWORD': '927090',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
