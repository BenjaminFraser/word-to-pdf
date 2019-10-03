#!/bin/sh
flask db upgrade
flask translate compile
exec gunicorn -b :5000 --access-logfile - --error-logfile - wordtopdf:app
