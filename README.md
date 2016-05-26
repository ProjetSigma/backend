Sigma - Backend
===============

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ProjetSigma/backend/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ProjetSigma/backend/?branch=master)
[![Circle CI](https://circleci.com/gh/ProjetSigma/backend.svg?style=svg)](https://circleci.com/gh/ProjetSigma/backend)
[![Coverage Status](https://coveralls.io/repos/github/ProjetSigma/backend/badge.svg?branch=master)](https://coveralls.io/github/ProjetSigma/backend?branch=master)

## Licence
<a href="https://github.com/ProjetSigma/backend/blob/master/LICENSE.md">
<img src="https://img.shields.io/badge/license-GNU%20Affero%20General%20Public%20License%20%28AGPL%29%20v3.0-blue.svg" alt="license" />
</a>


Vagrant usage
-------------
If you want to use the vagrant setup, you don't have to install python libraries.  
Please see the [provisioning repository](https://github.com/ProjetSigma/provisioning).

Installation (standalone version)
---------------------------------

**Requirements.**  
On Debian-based distribution, you will need the following librairies:
```[sh]
apt-get install python-dev libmysqlclient-dev libjpeg-dev python3.5-dev
```

**Python 3 is required.**  
We recommend to use a virtualenv for python. If you have python3 installed, it should had come with it.  
After you have cloned the repository, you can execute the following commands in your shell:
```[sh]
cd /path/to/sigma/backend
virtualenv --python=python3 .env
source .env/bin/activate
pip install -r requirements/{prod,dev}.txt
cp sigma/settings.py.local sigma/settings.py
./resetdb.sh
./manage.py runserver
```

If you don't want to use a virtualenv, follow these instructions to setup the project.

Install requirements  
`pip install -r requirements/prod.txt`
`pip install -r requirements/dev.txt`

If problems to install mysqlclient  
`apt-get install python-dev libmysqlclient-dev` or `yum install python-devel mysql-devel`

Since you don't use the vagrant, you have to use the local settings file:  
`cp sigma/settings.py.local sigma/settings.py`  

For a first installation, or if you have broken your database, reset it !  
`./resetdb.sh`

If you have just made a `git pull`, onlu migrate the database with  
`python manage.py migrate`

You can load fixtures data with  
`python manage.py loaddata fixtures.json`

Run dev server  
`python manage.py runserver` or `python manage.py runserver_plus` (can be useful but buggier...)

API is accessible at `127.0.0.1:8000` and documented at `127.0.0.1:8000/docs/` (Swagger).




Fixtures
--------

A few fixtures are loaded when `resetdb.sh` is executed. You have several users, whose credentials are (login/password):
* admin@sigma.fr / admin
* user@sigma.fr / user
* and many others (see the database, the password is always the username in the email adress).

An OAuth client application is also created (see below for further information), with data:
* `clientId`: `bJeSCIWpvjbYCuXZNxMzVz0wglX8mHR2ZTKHxaDv`
* `clientSecret`: `XjbfZS6Apq05PDTSL4CoFHGo7NsKVAa1XMVrVElk5N1t0dOSyqxrHPff6okAi6X6Du9XxrK4dl0mLQ0YlscJsjnL5IKhQagQdGv2SgumhYRFaMi6LtHNPXicmMr8oLdy`

To see all fixtures, browse the web API at `127.0.0.1:8000`.


OAuth usage
-----------
###Create an application *(temporary)*
NB. For frontend usage only, you can skip this part.

When you are logged in, you can create a trusted application at: `http://127.0.0.1:8000/o/applications/`  

I still have to understand how to deal correctly with applications addition... :p

For the name, put whatever you want. Choose **Client Type**: *confidential* and **Authorization Grant Type**: *Resource owner password-based*.

###Get your token
`client_id` and `client_secret` depend on the trusted application. To get token, do:  
`curl -X POST -d "grant_type=password&username=<user_name>&password=<password>" -u"<client_id>:<client_secret>" http://127.0.0.1:8000/o/token/`

The answer should be:
```json
{
    "access_token": "<your_access_token>",
    "token_type": "Bearer",
    "expires_in": 36000,
    "refresh_token": "<your_refresh_token>",
    "scope": "read write groups"
}
```

###Visit the secured API
With your token, you can access the secured API by passing an *Authorization* token in your request:  
`curl -H "Authorization: Bearer <your_access_token>" http://127.0.0.1:8000/user/`
