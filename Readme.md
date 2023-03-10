# Borcelle CRM | Django Redis/RabbitMQ Celery test

This project provides following features

-Implemented CRM
    
1. A user can register and start adding his contacts separately which are private to him
2. You can do CRUD operation with your contacts
3. Message your contacts via portal which will be emailed to them to their email.
4. Check history of messages
5. Email Verification before user can login


-Implemented Celery and Redis to Take Notes and Email it.
    
1. Used MailJet in Production to send Emails, at first Gmail with SMTP was using. Since heroku don't allow SMTP activities in the server, MailJet was used 
2. You can see the progress of the task in frontend
3. Progress Bar is Implemented with Ajax as well as Channels


-Implemented Celery Beat to Schedule Emails as Messages

1. Used Celery beat to Schedule Message Emails
2. used asyncio inside Signals Code to avoid interference with sync_to_async
3. As soon as task is completed a notification is send to CRM manager about its completion

-Broadcast Notifications using Web Sockets and Channels

-Deployed on Heroku

1. Used Heroku Postgres 
2. Used Daphene
3. Used REDIS-CLOUD Sever, provided by heroku add-ons

-Deployed on AWS

1. Used AWS EC2 Ubuntu 22.0 LTS
2. Used Nginx as a Web Proxy Server
3. Used Let's Encrypt Wildcard certificate 
4. Used Acme-dns server for automating renewal of wildcard certificates
5. Used docker to run inside a container since other projects are also running on the same server
6. Used Jenkins for CI/CD Integration Jenkins Server Running at: https://jenkins.arpansahu.me
7. Used AWS Elastic Cache for redis which is not accessible outside AWS
8. Used PostgresSql Schema based Database, all projects are using single Postgresql

## What is Redis, Celery, Celery Beat, Web Sockets, Channels, Signals, Ajax and working ?
In the below image I will try to explain everything.

![alt text](https://github.com/arpansahu/borcelle_crm/blob/master/explanation.png?raw=true)

## Working:-

1. When a user wants to take notes and want it to email-ed. Then from Django app we send 
    a request to Django View to create and Send a task to Redis/RabbitMQ broker. Then 
    broker will be passing this task to celery. Moreover, since while creating a task we 
    used celery results to save the progress in CELER_RESULT_BACKEND (django-db or redis or rabbitmq).
    So while the task is being executed user can see progress bar via two methods:

    - Using Ajax Call: While the process is not completed you can continuously hit the 
      endpoint to check status fo the task. which eventually increase your server load.
    - Using Web Sockets and channels: As soon as you load the web page you make a web socket 
      protocol connection to the server via handshaking and once the connection is established
      your server can directly send messages to frontend without request from the user end.
      This channel layer is also using Redis for Quick Response. So as soon as there are any changes
      to status of task it is notified to channel and if user is still connected to the channels, will
      be able to see the results in progress bar.

2. When a user wants to Schedule an Email as Reminder then, Via Django Application View, a cron task is created and that is 
   assigned to Celery Beat and as soon as the scheduled time arrived it pass task to broker, and then it is finally assigned 
   to celery which finishes the task and at the end of the task, a message is passed through channels to frontend to notify about the completion of task.

3. Admin can broadcast a Notification to all users using django channels and cron tab, admin can schedule the notification 
   at a particular time and then as soon as time arrives Celery Beat transfers task to Broker, and then it passes to Celery Workers.
   Moreover, the task focuses on sending notification through channels and web sockets so that users connected to particular channels 
   will be able to see the notifications.





## What is Django ?
Django is a Python-based free and open-source web framework that follows the model-template-view architectural pattern.

## What is Web Sockets ?

WebSocket is bidirectional, a full-duplex protocol that is used in the same scenario of client-server communication, unlike HTTP it starts from ws:// or wss://. It is a stateful protocol, which means the connection between client and server will keep alive until it is terminated by either party (client or server). After closing the connection by either of the client and server, the connection is terminated from both ends. 

## What is Channels?
Channels preserve the synchronous behavior of Django and add a layer of asynchronous protocols allowing users to write the views that are entirely synchronous, asynchronous, or a mixture of both. Channels basically allow the application to support “long-running connections”. It replaces Django’s default WSGI with its ASGI.

## What is Django Signals?
Django includes a “signal dispatcher” which helps decoupled applications get notified when actions occur elsewhere in the framework. In a nutshell, signals allow certain senders to notify a set of receivers that some action has taken place.

## What is Ajax?
Ajax is a set of web development techniques that uses various web technologies on the client-side to create asynchronous web applications. With Ajax, web applications can send and retrieve data from a server asynchronously without interfering with the display and behaviour of the existing page. 

## What is Celery ?
Celery is an asynchronous task queue/job queue based on distributed message passing. It is focused on real-time operation but supports scheduling as well.

Why is this useful?

1. Think of all the times you have had to run a certain task in the future. Perhaps you needed to access an API every hour. Or maybe you needed to send a batch of emails at the end of the day. Large or small, Celery makes scheduling such periodic tasks easy.
2. You never want end users to have to wait unnecessarily for pages to load or actions to complete. If a long process is part of your application’s workflow, you can use Celery to execute that process in the background, as resources become available, so that your application can continue to respond to client requests. This keeps the task out of the application’s context.

Working:
1. Celery requires message broker to store messages received from task generators or producers. For reading information of messages in task
  serialization is required which can be in json/pickle/yaml/msgpack it can be in compressed form as zlib, bzip2 or a cryptographic message.
2. A celery system consists of multiple workers and brokers, giving way to high availability and horizontal scaling.
3. When a celery worker is started using command ```celery -A [borcelle_crm(project name)].celery worker -l info```, a supervisor is started.
4. Which spawns child processes or threads and deals with all the bookkeeping stuff. The child processes or threads execute the actual task.
  This child process are also known as execution pool. By default, no of child process worker can spawn is equal to the no of CPU cores.
5. The size of execution pool determines the number of tasks your celery worker can process
   1. Worker ----- Pool ----- Concurrency 
   2. When you start a celery worker, you specify the pool, concurrency, autoscale etc. in the command 
   3. Pool - Decides who will actually perform the task -thread, child process, worker itself or else. 
   4. Concurrency: will decide the size of pool
   5. autoscale: to dynamically resize the pool based on load. The autoscaler adds more pool processes when there is work
     to do, and starts removing processes when the workload is low.
   6. ```celery -A <project>.celery worker --pool=preform --concurrency=5 --autoscale=10 3 -l info ``` 
    this command states to start a worker with 5 child processes which can be auto-scaled upto 10 and can be decreased upto 3.
6. Type of Pools: 
    1. prefork (multiprocessing) (default):
       1. Use this when CPU bound task
       2. By passes GIL (Global Interpreter Lock)
       3. The number of available cores limits the number of concurrent processes.
       4. That's why Celery defaults concurrency to no of CPU cores available.
       5. Command: ```celery A -<project>.celery worker -l info```
    2. solo (Neither threaded nor process-based)
        1. Celery don't support windows, so you can use this pool of running celery on Windows
        2. It doesn't create pool as it runs solo.
        3. Contradicts the principle that the worker itself does not process any tasks
        4. The solo pool runs inside the worker process.
        5. This makes the solo worker fast, But it also blocks the worker while it executes tasks.
        6. In this concurrency doesn't make any sense.
        7. Command ```celery A -<project>.celery worker --pool=solo -l info```
    3. threads (multi threading)
        1. due to GIL in CPython, it restricts to single thread so can't achieve real multithreading
        2. Not much official support
        3. Uses threading module of python
        4. Command ```celery A -<project>.celery worker --pool=threads -l info```
    4. gevent/eventlet (Green Threads)
       1. Uses Green thread which are user level threads so can be manipulated at code level 
       2. This can be used to get a thousand of HTTP get request to fetch from external REST APIs.
       3. The bottleneck is waiting for I/O operation to finish and not CPU.
       4. There are implementation differences between the eventlet and gevent packages
       5. Command ```celery A -<project>.celery worker --pool=[gevent/eventlet] worker -l info```
    5. by default ```celery A -<project>.celery worker -l info``` uses pool-prefork and concurrency -no of cores
    6. Difference between greenlets and threads -
       1. Python's threading library makes use of the system's native OS to schedule threads. This general-purpose scheduler is not always very efficient. 
       2. It makes use of Python's global interpreter lock to make sure shared data structures are accessed by only one thread at a time to avoid race conditions.
          CPython Interpreter, GIL, OS Greenlets emulate multi-threaded environments without relying on any native operating system capabilities.
          Greenlets are managed in application space and not in kernel space. In greenlets, no scheduler pre-emptively switching between your threads
          at any given moment. 
       3. Instead, your greenlets voluntarily or explicitly give up control to one another at specified points in your code. 
       4. Thus more scalable and efficient. Less RAM required.
       
## What is Redis ?
    
Redis is an in-memory data structure project implementing a distributed, in-memory key-value database with optional durability. 
The most common Redis use cases are session cache, full-page cache, queues, leaderboards and counting, publish-subscribe, and much more. in this case, we will use Redis as a message broker.

## What is RabbitMQ?
RabbitMQ is an open-source message-broker software that originally implemented the Advanced Message Queuing Protocol and has since been extended with a plug-in architecture to support Streaming Text Oriented Messaging Protocol, MQ Telemetry Transport, and other protocols. 

## Tech Stack

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Glossary/HTML5)
[![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Javascript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](https://www.javascript.com/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/docs/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/docs/)
[![Celery](https://img.shields.io/badge/celery-%2337814A.svg?&style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/en/stable/index.html)
[![RabbitMQ](https://img.shields.io/badge/rabbitmq-%23FF6600.svg?&style=for-the-badge&logo=rabbitmq&logoColor=white")](https://www.rabbitmq.com/)
[![Heroku](https://img.shields.io/badge/-Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white)](https://heroku.com/)
[![Github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://www.github.com/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=Jenkins&logoColor=white)](https://www.jenkins.io/)
[![AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
[![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)]()

## Demo

Available at: https://crm-borcelle.herokuapp.com/

admin login details:--
username: admin@arpansahu.me
password: showmecode
## License

[MIT](https://choosealicense.com/licenses/mit/)


## Installation

Installing Pre requisites
```bash
  pip install -r requirements.txt
```

Create .env File
```bash
  add variables mentioned in .env.example
```

Making Migrations and Migrating them.
```bash
  python manage.py makemigrations
  python manage.py migrate
```

Creating Super User
```bash
  python manage.py createsuperuser
```

Installing Redis On Local (For ubuntu) for other Os Please refer to their website https://redis.io/
```bash
  curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
  sudo apt-get update
  sudo apt-get install redis
  sudo systemctl restart redis.service
```
to check if its running or not
```
  sudo systemctl status redis
```
--------------------------

Use these CELERY settings

``` 
CELERY_BROKER_URL = 'redis://localhost:6379'
# CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
```


CELERY_RESULT_BACKEND have been commented, because we have used ```task.apply_async()``` instead of ```task.dealy()```
with websockets for sending notification, django-db as a backend is synchronous
and thus gives error, Hence we have to use redis or other resources which primarily 
supports asynchronous work flow.


---

Creating Async App - create a file named celery.py in project directory.
``` 
import os

from celery import Celery
from celery.schedules import crontab
from decouple import config

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borcelle_crm.settings')

redis_url = config("REDISCLOUD_URL")

app = Celery('borcelle_crm', broker=redis_url, backend=redis_url, include=['tasks.tasks'])

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Settings
app.conf.beat_schedule = {
    'send-mail-every-day-at-8': {
        'task': 'send_email_app.tasks.send_mail_func',
        'schedule': crontab(hour=0, minute=38),
        # 'args' : (2,)
    }
}
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

```

set ASGI settings in settings.py
``` 
ASGI_APPLICATION = 'borcelle_crm.routing.application'
```

Uncomment Channel Layers Setting for Local Machine on settings.py
```bash
   CHANNEL_LAYERS = {
     'default': {
         'BACKEND': 'channels_redis.core.RedisChannelLayer',
         'CONFIG': {
             "hosts": [('127.0.0.1', 6379)],
         },
     },
   }
```
Comment Channel Layers Setting for Heroku on settings.py
```bash
   CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config('REDISCLOUD_URL')],
        },
    },
  }
```

Run Server
```bash
  python manage.py runserver
```

Run Celery (in a different terminal)
```bash
  celery -A borcelle_crm.celery worker -l info
```

Run Celery Beat (in a different terminal)
```bash
  celery -A borcelle_crm beat -l INFO
```

## Deployment on Heroku

Installing Heroku Cli from : https://devcenter.heroku.com/articles/heroku-cli
Create your account in Heroku.

Inside your project directory

Login Heroku CLI
```bash
  heroku login

```

Create Heroku App

```bash
  heroku create [app_name]

```

Push Heroku App
```
    git push heroku master
```

Configure Heroku App
```bash
  heroku config:set GITHUB_USERNAME=joesmith

```
Configuring Django App for Heroku

Install whitenoise 
```
pip install whitenoise 
```

Include it in Middlewares.
```
MIDDLEWARE = [
    # ...
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...
]
```

Create Procfile and include this code snippet in it.
```
release: python manage.py migrate
web: daphne borcelle_crm.asgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery -A borcelle_crm.celery worker -l info
celerybeat: celery -A borcelle_crm beat -l INFO
celeryworker2: celery -A borcelle_crm.celery worker & celery -A borcelle_crm beat -l INFO & wait -n
```

In the above Procfile there are three workers required for web, celery and celery beat, but since heroku free
plan only allows upto 2 free dynos we have merged celery and celerybeat into celeryworker2
and from the admin panel of heroku app we can enable just the web and celeryworker2.

Comment down Database setting and install 

``` 
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': config('DB_PORT'),
#     }
# }
```
```
pip install dj-database-url
```

and add these lines below the commented Database settings
``` 
import dj_database_url
DATABASES = {'default': dj_database_url.config(default=config('DATABASE_URL'))}
```

Change CELERY_BROKER_URL from 
``` 
CELERY_BROKER_URL = 'redis://localhost:6379'
```
to
```
CELERY_BROKER_URL=config("REDISCLOUD_URL")
```

## Deployment on AWS EC2 Ubuntu 22.0 LTS
Previously This project was hosted on Heroku, but now I am hosting this and all other projects in a 
Single EC2 Machine

Multiple Projects are running inside dockers so all projects are dockerized.
You can refer to all projects on https://www.arpansahu.me/projects

Every project have different port on which its running predefined inside Dockerfile and docker-compose.yml

### Step 1: Dockerizing

Installing Docker 

Reference: https://docs.docker.com/engine/install/ubuntu/

1. Setting up the Repository
   1. Update the apt package index and install packages to allow apt to use a repository over HTTPS: 
       ```
       sudo apt-get update
    
       sudo apt-get install \
       ca-certificates \
       curl \
       gnupg \
       lsb-release
       ```
   2. Add Docker’s official GPG key:

       ```
       sudo mkdir -p /etc/apt/keyrings
    
       curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
       ```

   3. Use the following command to set up the repository:

       ```
       echo \
         "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
         $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
       ```
2. Install Docker Engine
    
   1. Update the apt package index:

      ```
       sudo apt-get update
      ```
    
      1. Receiving a GPG error when running apt-get update?

         Your default umask may be incorrectly configured, preventing detection of the repository public key file. Try granting read permission for the Docker public key file before updating the package index:
            ```
            sudo chmod a+r /etc/apt/keyrings/docker.gpg
            sudo apt-get update
            ```
   2. Install Docker Engine, containerd, and Docker Compose.

        ```
        sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
        ```
   3. Verify that the Docker Engine installation is successful by running the hello-world image:

        ```
         sudo docker run hello-world
        ```

Now in your Git Repository

Create a file named Dockerfile with no extension and add following lines in it
```
FROM python:3.10.7

WORKDIR /app

COPY requirements.txt requirements.txt

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8014

CMD daphne borcelle_crm.asgi:application -b 0.0.0.0 --port 8014 & celery -A borcelle_crm.celery worker -l info & celery -A borcelle_crm beat -l INFO
```

Create a file named docker-compose.yml and add following lines in it

```
version: '3'

services:
  web:
    build: .
    env_file: ./.env
    command: bash -c "python manage.py makemigrations && python manage.py migrate && daphne borcelle_crm.asgi:application -b 0.0.0.0 --port 8014 & celery -A borcelle_crm.celery worker -l info & celery -A borcelle_crm beat -l INFO"
    image: borcelle_crm
    container_name: borcelle_crm
    volumes:
      - .:/borcelle_crm
    ports:
      - "8014:8014"
```

### **What is Difference in Dockerfile and docker-compose.yml?**

A Dockerfile is a simple text file that contains the commands a user could call to assemble an image whereas Docker Compose is a tool for defining and running multi-container Docker applications.

Docker Compose define the services that make up your app in docker-compose.yml so they can be run together in an isolated environment. It gets an app running in one command by just running docker-compose up. Docker compose uses the Dockerfile if you add the build command to your project’s docker-compose.yml. Your Docker workflow should be to build a suitable Dockerfile for each image you wish to create, then use compose to assemble the images using the build command.

Running Docker 
```
docker compose up --build --detach 
```

--detach tag is for running the docker even if terminal is closed
if you remove this tag it will be attached to terminal, and you will be able to see the logs too

--build tag with docker compose up will force image to be rebuild everytime before starting the container

### Step2: Serving the requests from Nginx

Installing Nginx server

```
sudo apt-get install nginx
```

Starting Nginx and checking its status 

```
sudo systemctl start nginx
sudo systemctl status nginx
```

#### Modify DNS Configurations

Add these two records to your DNS Configurations
```
A Record	*	0.227.49.244 (public ip of ec2)	Automatic
A Record	@	0.227.49.244 (public ip of ec2)	Automatic
```

Note: now you will be able to see nhinx running page if you open public ip of the machine

Make Sure your EC2 security Group have this entry inbound rules 

```
random-hash-id	IPv4	HTTP	TCP	80	0.0.0.0/0	–
```

Open a new Nginx Configuration file name can be anything i am choosing arpansahu since my domain is arpansahu.me. there is already a default configuration file but we will leave it like that only

```
sudo vi /etc/nginx/sites-available/arpansahu
```

paste this content in the above file

```
server_tokens               off;
access_log                  /var/log/nginx/supersecure.access.log;
error_log                   /var/log/nginx/supersecure.error.log;

server {
  server_name               borcelle-crm.arpansahu.me;        
  listen                    80;
  location / {
    proxy_pass              http://localhost:8014;
    proxy_set_header        Host $host;
  }
}
```

Basically this single Nginx File will be hosting all the multiple projects which I have listed before also.

Checking if configurations fie is correct

```
sudo service nginx configtest /etc/nginx/sites-available/arpansahu
```

Now you need to symlink this file to the sites-enabled directory:

``` 
cd /etc/nginx/sites-enabled
sudo ln -s ../sites-available/arpansahu
```

Restarting Nginx Server 
```
sudo systemctl restart nginx
```

Now It's time to enable HTTPS for this server

### Step 3: Enabling HTTPS 

1. Base Domain:  Enabling https for base domain only or a single sub domain

    To allow visitors to access your site over HTTPS, you’ll need an SSL/TLS certificate that sits on your web server. Certificates are issued by a Certificate Authority (CA).We’ll use a free CA called Let’s Encrypt. To actually install the certificate, you can use the Certbot client, which gives you an utterly painless step-by-step series of prompts.
    Before starting with Certbot, you can tell Nginx up front to disable TLS version 1.0 and 1.1 in favor of versions 1.2 and 1.3. TLS 1.0 is end-of-life (EOL), while TLS 1.1 contained several vulnerabilities that were fixed by TLS 1.2. To do this, open the file /etc/nginx/nginx.conf. Find the following line:
    
    Open nginx.conf file end change ssl_protocols 
    
    ```
    sudo vi /etc/nginx/nginx.conf
    
    From ssl_protocols TLSv1 TLSv1.1 TLSv1.2; to ssl_protocols TLSv1.2 TLSv1.3;
    ```
    
    Use this command to verify if nginx.conf file is correct or not
    
    ```
    sudo nginx -t
    ```
    
    Now you’re ready to install and use Certbot, you can use snap to install Certbot:
    
    ```
    sudo snap install --classic certbot
    sudo ln -s /snap/bin/certbot /usr/bin/certbot
    ```
    
    Now installing certificate
    
    ```
    sudo certbot --nginx --rsa-key-size 4096 --no-redirect
    ```
    
    It will be asking for domain name then you can enter your base domain 
    I have generated ssl for borcelle-crm.arpansahu.me
    
    Then a few questions will be asked by them answer them all and done your ssl certificate will be geerated
    
    Now These lines will be added to your # Nginx configuration: /etc/nginx/sites-available/arpansahu
    
    ```
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/www.supersecure.codes/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.supersecure.codes/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    ```
    
    Redirecting HTTP to HTTPS
    Open nginx configuration file  and make it like this

    ```
    sudo vi /etc/nginx/sites-available/arpansahu
    ```
    ```
    server_tokens               off;
    access_log                  /var/log/nginx/supersecure.access.log;
    error_log                   /var/log/nginx/supersecure.error.log;
     
    server {
      server_name               borcelle-crm.arpansahu.me;
      listen                    80;
      return                    307 https://$host$request_uri;
    }
    
    server {
    
      location / {
        proxy_pass              http://localhost:8014;
        proxy_set_header        Host $host;
        
        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }                          
    ``` 
    
    You can dry run and check weather it's renewal is working or not
    ```
    sudo certbot renew --dry-run
    ```
    
    Note: this process was for borcelle-crm.arpansahu.me and not for all subdomains.
        For all subdomains we will have to setup a wildcard ssl certificate


2. Enabling a Wildcard certificate

    Here we will enable ssl certificate for all subdomains at once
    
    Run following Command
    ```
    sudo certbot certonly --manual --preferred-challenges dns
    ```
    
    Again you will be asked domain name and here you will use *.arpansahu.me. and second domain you will use is
    arpansahu.me.
    
    Now, you should be having a question in your mind that why we are generating ssl for arpansahu.me separately.
    It's because Let's Encrupt does not include base doamin with wildcard certificates for subdomains.

    After running above command you will see a message similar to this
    
    ```
    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Please enter the domain name(s) you would like on your certificate (comma and/or
    space separated) (Enter 'c' to cancel): *.arpansahu.me
    Requesting a certificate for *.arpansahu.me
    
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Please deploy a DNS TXT record under the name:
    
    _acme-challenge.arpansahu.me.
    
    with the following value:
    
    dpWCxvq3mARF5iGzSfaRNXwmdkUSs0wgsTPhSaX1gK4
    
    Before continuing, verify the TXT record has been deployed. Depending on the DNS
    provider, this may take some time, from a few seconds to multiple minutes. You can
    check if it has finished deploying with aid of online tools, such as the Google
    Admin Toolbox: https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.arpansahu.me.
    Look for one or more bolded line(s) below the line ';ANSWER'. It should show the
    value(s) you've just added.
   
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Press Enter to Continue
    ```
   
    You will be given a dns challenge called ACME challenger you have to create a dns TXT record in DNS.
    Similar to below record.
    
    ```
    TXT Record	_acme-challenge	dpWCxvq3mARF5iGzSfaRNXwmdkUSs0wgsTPhSaX1gK4	5 Automatic
    ```
    
    Now, use this url to verify records are updated or not

    https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.arpansahu.me (arpansahu.me is domain)

    If its verified then press enter the terminal as mentioned above
    
    Then your certificate will be generated
    ```
    Successfully received certificate.
    Certificate is saved at: /etc/letsencrypt/live/arpansahu.me-0001/fullchain.pem            (use this in your nginx configuration file)
    Key is saved at:         /etc/letsencrypt/live/arpansahu.me-0001/privkey.pem
    This certificate expires on 2023-01-20.
    These files will be updated when the certificate renews.
    ```
    
    You can notice here, certificate generated is arpansahu.me-0001 and not arpansahu.me
    because we already generated a certificate named arpansahu.me
    
    So remember to delete it before generating this wildcard certificate
    using command

    ```
    sudo certbot delete
    ```
    
    Note: This certificate will not be renewed automatically. Auto-renewal of --manual certificates requires the use of an authentication hook script (--manual-auth-hook) but one was not provided. To renew this certificate, repeat this same certbot command before the certificate's expiry date.

3. Generating Wildcard SSL certificate and Automating its renewal

    1. Modify your ec2 inbound rules 
    
      ```
      –	sgr-0219f1387d28c96fb	IPv4	DNS (TCP)	TCP	53	0.0.0.0/0	–	
      –	sgr-01b2b32c3cee53aa9	IPv4	SSH	TCP	22	0.0.0.0/0	–
      –	sgr-0dfd03bbcdf60a4f7	IPv4	HTTP	TCP	80	0.0.0.0/0	–
      –	sgr-02668dff944b9b87f	IPv4	HTTPS	TCP	443	0.0.0.0/0	–
      –	sgr-013f089a3f960913c	IPv4	DNS (UDP)	UDP	53	0.0.0.0/0	–
      ```
    
   2. Install acme-dns Server

      * Create folder for acme-dns and change directory

        ```
         sudo mkdir /opt/acme-dns
         cd !$
        ```
      * Download and extract tar with acme-dns from GitHub

        ```
        sudo curl -L -o acme-dns.tar.gz \
        https://github.com/joohoi/acme-dns/releases/download/v0.8/acme-dns_0.8_linux_amd64.tar.gz
        sudo tar -zxf acme-dns.tar.gz
        ```
      * List files
        ```
        sudo ls
        ```
      * Clean Up
        ```
        sudo rm acme-dns.tar.gz
        ```
      * Create soft link
        ```
        sudo ln -s \
        /opt/acme-dns/acme-dns /usr/local/bin/acme-dns
        ```
      * Create a minimal acme-dns user
         ```
         sudo adduser \
         --system \	
         --gecos "acme-dns Service" \
         --disabled-password \
         --group \
         --home /var/lib/acme-dns \
         acme-dns
        ```
      * Update default acme-dns config compare with IP from the AWS console. CAn't bind to the public address need to use private one.
        ```
        ip addr
	  
        sudo mkdir -p /etc/acme-dns
	  
        sudo mv /opt/acme-dns/config.cfg /etc/acme-dns/
	  
        sudo vim /etc/acme-dns/config.cfg
        ```
      
      * Replace
        ```
        listen = "127.0.0.1:53” to listen = “private ip of the ec2 instance” 172.31.93.180:53(port will be 53)
 
        Similarly Edit other details mentioned below  

        # domain name to serve the requests off of
        domain = "auth.arpansahu.me"
        # zone name server
        nsname = "auth.arpansahu.me"
        # admin email address, where @ is substituted with .
        nsadmin = "admin@arpansahu.me"


        records = [
          # domain pointing to the public IP of your acme-dns server
           "auth.arpansahu.me. A 44.199.177.138. (public elastic ip)”,
          # specify that auth.example.org will resolve any *.auth.example.org records
           "auth.arpansahu.me. NS auth.arpansahu.me.”,
        ]
	
        [api]
        # listen ip eg. 127.0.0.1
        ip = "127.0.0.1”. (Changed)

        # listen port, eg. 443 for default HTTPS
        port = "8080" (Changed).         ——— we will use port 8090 because we will also use Jenkins which will be running on 8080 port
        # possible values: "letsencrypt", "letsencryptstaging", "cert", "none"
        tls = "none"   (Changed)

        ```
      * Move the systemd service and reload
        ```
        cat acme-dns.service
     
        sudo mv \
        acme-dns.service /etc/systemd/system/acme-dns.service
	  
        sudo systemctl daemon-reload
        ```
      * Start and enable acme-dns server
        ```
        sudo systemctl enable acme-dns.service
        sudo systemctl start acme-dns.service
        ```
      * Check acme-dns for posible errors
        ```
        sudo systemctl status acme-dns.service
        ```
      * Use journalctl to debug in case of errors
         ```
         journalctl --unit acme-dns --no-pager --follow
         ```
      * Create A record for your domain
         ```
         auth.arpansahu.me IN A <public-ip>
         ```
      * Create NS record for auth.arpansahu.me pointing to auth.arpansahu.me. This means, that auth.arpansahu.me is
        responsible for any *.auth.arpansahu.me records
        ```
        auth.arpansahu.me IN NS auth.arpansahu.me
        ```
      * Your DNS record will be looking like this
        ```
        A Record	auth	44.199.177.138	Automatic	
        NS Record	auth	auth.arpansahu.me.	Automatic
        ```
      * Test acme-dns server (Split the screen)
        ```
        journalctl -u acme-dns --no-pager --follow
        ```
      * From local host try to resolve random DNS record
        ```
        dig api.arpansahu.me
        dig api.auth.arpansahu.me
        dig 7gvhsbvf.auth.arpansahu.me
        ``` 
        
   3. Install acme-dns-client 
     ```
     sudo mkdir /opt/acme-dns-client
     cd !$
    
     sudo curl -L \
     -o acme-dns-client.tar.gz \
     https://github.com/acme-dns/acme-dns-client/releases/download/v0.2/acme-dns-client_0.2_linux_amd64.tar.gz
    
     sudo tar -zxf acme-dns-client.tar.gz
     ls
     sudo rm acme-dns-client.tar.gz
     sudo ln -s \
     /opt/acme-dns-client/acme-dns-client /usr/local/bin/acme-dns-client 
     ```
   4. Install Certbot
     ```
     cd
     sudo snap install core; sudo snap refresh core
     sudo snap install --classic certbot
     sudo ln -s /snap/bin/certbot /usr/bin/certbot
     ```
    Note: you can skip step4 if Certbot is already installed

    5. Get Letsencrypt Wildcard Certificate
       * Create a new acme-dns account for your domain and set it up
         ```
         sudo acme-dns-client register \
         -d arpansahu.me -s http://localhost:8090
         ```
         Note: When we edited acme-dns config file there we mentioned the port 8090 and thats why we are using this port here also
       * Creating Another DNS Entry 
         ```
         CNAME Record	_acme-challenge	e6ac0f0a-0358-46d6-a9d3-8dd41f44c7ec.auth.arpansahu.me.	Automatic
         ```
         Same as an entry is needed to be added to complete one time challenge as in previously we did.
       * Check the entry is added successfully or not
         ```
         dig _acme-challenge.arpansahu.me
         ```
       * Get wildcard certificate
         ```
         sudo certbot certonly \
         --manual \
         --test-cert \ 
         --preferred-challenges dns \ 
         --manual-auth-hook 'acme-dns-client' \ 
         -d ‘*.arpansahu.me’ -d arpansahu.me
         ```
         Note: Here we have to mention both the base and wildcard domain names with -d since let's encrypt don't provide base domain ssl by default in wildcard domain ssl
       *Verifying the certificate
         ```
         sudo openssl x509 -text -noout \
         -in /etc/letsencrypt/live/arpansahu.me/fullchain.pem
         ```
       * Renew certificate (test)
         ```
         sudo certbot renew \
         --manual \ 
         --test-cert \ 
         --dry-run \ 
         --preferred-challenges dns \
         --manual-auth-hook 'acme-dns-client'       
         ```
       * Check the entry is added successfully or not
         ```
         dig _acme-challenge.arpansahu.me
         ```
    6. Setup Auto-Renew for Letsencrypt WILDCARD Certificate
       * Setup cronjob
         ```
         sudo crontab -e
         ```
       * Add following lines to the file
         ```
         0 */12 * * * certbot renew --manual --test-cert --preferred-challenges dns --manual-auth-hook 'acme-dns-client'
         ```

After all these steps your Nginx configuration file located at /etc/nginx/sites-available/arpansahu will be looking similar to this

```
server_tokens               off;
access_log                  /var/log/nginx/supersecure.access.log;
error_log                   /var/log/nginx/supersecure.error.log;

server {
    listen         80;
    server_name    borcelle-crm.arpansahu.me;
    # force https-redirects
    if ($scheme = http) {
        return 301 https://$server_name$request_uri;
        }

    location / {
         proxy_pass              http://localhost:8014;
         proxy_set_header        Host $host;
         proxy_set_header    X-Forwarded-Proto $scheme;

	 # WebSocket support
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "upgrade";
    }
   
	

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```

### Step 4: CI/CD using Jenkins

Installing Jenkins

Reference: https://www.jenkins.io/doc/book/installing/linux/

Jenkins requires Java in order to run, yet certain distributions don’t include this by default and some Java versions are incompatible with Jenkins.

There are multiple Java implementations which you can use. OpenJDK is the most popular one at the moment, we will use it in this guide.

Update the Debian apt repositories, install OpenJDK 11, and check the installation with the commands:

```
sudo apt update

sudo apt install openjdk-11-jre

java -version
openjdk version "11.0.12" 2021-07-20
OpenJDK Runtime Environment (build 11.0.12+7-post-Debian-2)
OpenJDK 64-Bit Server VM (build 11.0.12+7-post-Debian-2, mixed mode, sharing)
```

Long Term Support release

```
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins
```

Start Jenkins

```
sudo systemctl enable jenkins
```

You can start the Jenkins service with the command:

```
sudo systemctl start jenkins
```

You can check the status of the Jenkins service using the command:
```
sudo systemctl status jenkins
```

Now for serving the Jenkins UI from Nginx add these following lines to the Nginx file located at 
/etc/nginx/sites-available/arpansahu by running the following command

```
sudo vi /etc/nginx/sites-available/arpansahu
```

* Add these lines to it.

    ```
    server {
        listen         80;
        server_name    jenkins.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }
    
        location / {
             proxy_pass              http://localhost:8080;
             proxy_set_header        Host $host;
             proxy_set_header    X-Forwarded-Proto $scheme;
        }
    
        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```

You can add all the server blocks to the same nginx configuration file
just make sure you place the server block for base domain at the last

* Now Create a file named Jenkinsfile at the root of Git Repo and add following lines to file

```
pipeline {
    agent any
    stages {
        stage('Production') {
            steps {
                script {
                    sh "docker compose up --build --detach"
                }
            }
        }
    }
    post {
        success {
            sh """curl -s \
            -X POST \
            --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
            https://api.mailjet.com/v3.1/send \
            -H "Content-Type:application/json" \
            -d '{
                "Messages":[
                        {
                                "From": {
                                        "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                        "Name": "ArpanSahuOne Jenkins Notification"
                                },
                                "To": [
                                        {
                                                "Email": "$MY_EMAIL_ADDRESS",
                                                "Name": "Development Team"
                                        }
                                ],
                                "Subject": "${currentBuild.fullDisplayName} deployed succcessfully",
                                "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} is now deployed",
                                "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} is now deployed </h3> <br> <p> Build Url: ${env.BUILD_URL}  </p>"
                        }
                ]
            }'"""
        }
        failure {
            sh """curl -s \
            -X POST \
            --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
            https://api.mailjet.com/v3.1/send \
            -H "Content-Type:application/json" \
            -d '{
                "Messages":[
                        {
                                "From": {
                                        "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                        "Name": "ArpanSahuOne Jenkins Notification"
                                },
                                "To": [
                                        {
                                                "Email": "$MY_EMAIL_ADDRESS",
                                                "Name": "Developer Team"
                                        }
                                ],
                                "Subject": "${currentBuild.fullDisplayName} deployment failed",
                                "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} deployment failed",
                                "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} is not deployed, Build Failed </h3> <br> <p> Build Url: ${env.BUILD_URL}  </p>"
                        }
                ]
            }'"""
        }
    }
}
```

* Configure a Jenkins project from jenkins ui located at https://jenkins.arpansahu.me

Make sure to use Pipline project and name it whatever you want I have named it as borcelle_crm_declarative_pipeline_project

![Jenkins Project for borcelle CRM Configuration File](https://github.com/arpansahu/borcelle_crm/blob/master/borcelle_crm_jenkins_config.png?raw=true)

In this above picture you can see credentials right? you can add your github credentials
from Manage Jenkins on home Page --> Manage Credentials

and add your GitHub credentials from there

* Add a .env file to you project using following command

    ```
    sudo vi  /var/lib/jenkins/workspace/borcelle_crm_declarative_pipeline_project/.env
    ```

    Your workspace name may be different.

    Add all the env variables as required and mentioned in the Readme File.

* Add Global Jenkins Variables from Dashboard --> Manage --> Jenkins
  Configure System
 
  * MAIL_JET_API_KEY
  * MAIL_JET_API_SECRET
  * MAIL_JET_EMAIL_ADDRESS
  * MY_EMAIL_ADDRESS

Now you are good to go.



## Documentation

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Glossary/HTML5)
[![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Javascript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](https://www.javascript.com/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/docs/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/docs/)
[![Celery](https://img.shields.io/badge/celery-%2337814A.svg?&style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/en/stable/index.html)
[![RabbitMQ](https://img.shields.io/badge/rabbitmq-%23FF6600.svg?&style=for-the-badge&logo=rabbitmq&logoColor=white")](https://www.rabbitmq.com/)
[![Heroku](https://img.shields.io/badge/-Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white)](https://heroku.com/)
[![Github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://www.github.com/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=Jenkins&logoColor=white)](https://www.jenkins.io/)
[![AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
[![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)]()


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

REDISCLOUD_URL=

SECRET_KEY=

DEBUG=

ALLOWED_HOSTS=

DATABASE_URL=

MAIL_JET_API_KEY=

MAIL_JET_API_SECRET=

MAIL_JET_EMAIL_ADDRESS=

AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_STORAGE_BUCKET_NAME=

DOMAIN=

PROTOCOL=