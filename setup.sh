#!/bin/bash

pip install poetry
poetry init -n
poetry install --no-root
python3 manage.py collectstatic --noinput
python3 manage.py generateimages
python3 manage.py migrate

