Appcinema
============

Demo app - a seat reservation module for cinemas.

How to run
----------

You have to set up API/Key for Facebook and pusher services.

 1. create file ```settings_secret.py``` in ```appcinema/appcinema```
 2. set ```SOCIAL_AUTH_FACEBOOK_KEY```, ```SOCIAL_AUTH_FACEBOOK_SECRET```,
    ```PUSHER_SECRET```, ```PUSHER_KEY```

You can use virtualenv

```
$ python3 -m venv appcinema
$ cd appcinema
$ source bin/activate
$ git clone https://bitbucket.org/jkrajniak/appcinema.git
$ cd appcinema
$ pip install -r requirements.txt
$ cd appcinema
$ ./manage.py migrate
```

or docker-compose
```
$ git clone https://bitbucket.org/jkrajniak/appcinema.git
$ cd appcinema
$ docker-compose build
$ docker-compose up
```

Libraries
---------

Core:

 - Django 1.11
 - Django REST Framework
 - pusher
 - coreapi
 - python-social-auth

Full list of the required packages is in ```requirements.txt``` file.

GUI:

 - Twitter Bootstrap
 - JQuery