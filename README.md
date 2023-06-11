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

for other portable devices such as phone, IPAD, and etc.
```shell
python manage.py runserver 0.0.0.0:8000 
``` 
\
To connect to the url on the phone or IPAD
1. First, you need to connect to the same WIFI as your notebook is connecting to 
2. Secondly, write the wifi_address:0808/pha/ 
   - for example, 192.168.68.53:0808/pha/signin


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
\
For food data,
you have to import directly pha_food.csv file in staticfiles directory
(**YOU NEED TO IMPORT pha_food.csv BEFORE RUNNING PYTHON FILES**)

Please go to data_generating directory.
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
A password for all users is Jane902

### Project detail page
1. Go to the  HealthGenie/pha/view.py
2. you need to change a directory inside a function of project_detail(request, project_id):
   
```python
    def project_detail(request, project_id):
    project = Project.objects.get(pk=project_id)
    ### change directory here
    streamlit_app_dir = 'C:/Users/daye/Desktop/P4DS/HealthGenie/pha/final_streamlit'
```


### Food Classification 

1. Go to a link that follows: https://colab.research.google.com/drive/1wGxywzdOba5jgmdp7KEyaCK5tX1LK2Bi 
2. Run the code blocks sequentially in the colab and then follow the instruction (especially for ngrok token)
3. A return url for the last code block needs to be written in /HealthGenie/pha/views.py at line 273 where you have to write a flask url
   
   ```python 
    # change this url to your own url 
    # line 273 
    flask_url = 'http://f344-34-90-28-57.ngrok-free.app/analyze'
        with open(image_path, 'rb') as img:
            response = requests.post(flask_url, files={'file': img})
   ```
   
### CORS(Cross-Origin Resource Sharing)
1. install nginx
```shell
   sudo apt-get install nginx
```   
2. open the Nginx configuration file 
```shell
  sudo nano /etc/nginx/nginx.conf
```
3. inside the http block, add the following lines to enable CORS headers:
``` shell
   http {
      # Other configurations
   
      server {
          # Other server configurations
          location / {
              proxy_pass http://<your-ipaddress>:8501;  # Replace with your Streamlit app URL
              add_header 'Access-Control-Allow-Origin' '*';
              add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
              add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
              add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
          }
      }
   }
``` 
4.Save the Nginx configuration file and restart Nginx to apply the changes:
```shell
   sudo service nginx restart
```
5. replace <your-ipaddress> in pha/project_detail.html
```html
   <iframe src="http://<your-ipaddress>:8501" width="100%" height="850" style="border: none;"></iframe>
```
6. run the django server
```shell
  python manage.py runserver 0.0.0.0:8000 
``` 