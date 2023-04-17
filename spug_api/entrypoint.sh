#!/bin/bash

# update database
python3 manage.py updatedb

# create user
if [ -n "$ROOT_USER" ] && [ -n "$ROOT_PASSWORD" ]; then
  python3 manage.py user add -u $ROOT_USER -p $ROOT_PASSWORD -n $ROOT_USER -s
fi

python3 manage.py runserver 0.0.0.0:${PORT:-8080}
