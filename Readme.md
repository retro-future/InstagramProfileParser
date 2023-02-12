# Instagram Profile Parser using Selenium and Django

## How to set up the project:
* #### Copy the project using:
```
  https://github.com/retro-future/InstagramProfileParser.git
```


* #### Rename .env.dist to .env

```bash
  cd InstagramProfileParser 
```
```bash
  pip install -r requirements.txt 
```
* #### Activate Virtual environment
* #### Generate new django secret key
```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
 
```
* #### Write your credentials to the .env 

* #### make and run migrations
```bash
  python manage.py makemigrations
  python manage.py migrate
```
* #### Install Redis and run it on port 6379
* #### On terminal Run Celery with following commands
```bash
celery -A insta_clone worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
```
* #### Run django server
* #### In Browser open localhost:8000/parser
* #### Enter instagram profile username, click parse button and parsing should start
* #### All parsed imaged saved in media/profile_pictures folder

* Don't forget to update chromedriver.exe and place it in root directory