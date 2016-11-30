#!/bin/sh
python3 manage.py reset_db && \
python3 manage.py migrate && \
python3 manage.py loaddata sigma_core/fixtures.json && \
python3 manage.py loaddata fixtures_oauth.json
