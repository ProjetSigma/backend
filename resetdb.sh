#!/bin/sh
python3 manage.py reset_db && \
python3 manage.py migrate && \
python3 manage.py loaddata sigma_core/fixtures/fixtures_prod.json && \
python3 manage.py loaddata fixtures.json
