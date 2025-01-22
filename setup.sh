#!/bin/bash

git submodule --init
pip install poetry
poetry install --no-root
python manage.py collectstatic --noinput
python manage.py generateimages
python manage.py migrate

