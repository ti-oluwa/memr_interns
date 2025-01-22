#!/bin/bash

git submodule update --init --recursive
pip install poetry
poetry install --no-root -vvv
python manage.py collectstatic --noinput
python manage.py generateimages
python manage.py migrate

