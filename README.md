Sigma - Backend
===============

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ProjetSigma/backend/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ProjetSigma/backend/?branch=master)
[![Circle CI](https://circleci.com/gh/ProjetSigma/backend.svg?style=svg)](https://circleci.com/gh/ProjetSigma/backend)

Installation
------------

Install requirements

`pip install -r requirements.txt`

If problems to install mysqlclient

`apt-get install python-dev libmysqlclient-dev` or `yum install python-devel mysql-devel`

Migrate database

`python manage.py migrate`

Run dev server

`python manage.py runserver` or `python manage.py runserver_plus` (can be useful but buggier...)

API is accessible at `127.0.0.1:8000` and documented at `127.0.0.1:8000/docs/` (Swagger).

OAuth usage
-----------
###Create an application *(temporary)*
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
