# HealthGenie
This repository for PHA project. 
## Features
user signup, signin
### installation
required packages need to be installed
```shell
pip install -r requirements.txt
```
### Usage
Go to the HealthGenie folder and modify my_settings.py as your Database connection.
```python
...
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Go to the HealthGenie folder and migrate.
```shell
python manage.py migrate
```
then run server
```shell
python manage.py runserver
```
### Create admin user account
You can access the django admin page at **http://127.0.0.1:8000/admin/** and login with username 'admin' and the above password.
Also a new admin user can be created using
```shell
python manage.py createsuperuser
```
### Signup user account
(http://127.0.0.1:8000/pha/signup)
### Signin user account
(http://127.0.0.1:8000/pha/signin)
