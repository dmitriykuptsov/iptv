#!/bin/bash

/usr/local/bin/uwsgi --socket 0.0.0.0:5000 --master --processes 10 --protocol=http -w wsgi:app
