Sigma - Backend
===============

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ProjetSigma/backend/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ProjetSigma/backend/?branch=master)

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
