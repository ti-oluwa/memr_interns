#!/bin/bash

pip install poetry
poetry init -n
poetry install
python3 manage.py collectstatic
python3 manage.py generateimages
python3 manage.py migrate

