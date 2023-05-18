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
Go to the HealthGenie folder and modify my_settings.py as your own Database connection.
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
Do migration
```shell
python manage.py migrate
```
then run server.
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

### Import data

For food data,
you have to import directly pha_food.csv file in staticfiles directory

First, please go to data_generating directory.
And then open the my_db_setting.py file to correctly fill data for your own computer setting  
Finally, run the below codes line by line (it will takes some time when creating meal_time)

```shell 
python .\data_pha_user.py
python .\data_w_tracking.py     
python .\data_pha_project_1.py
python .\data_pha_project_2.py
python .\data_pha_meal.py
python .\data_pha_health_info.py
```

a password for all user is Jane902

### Project detail page 
(http://127.0.0.1:8000/pha/projects/'project_id'/)

