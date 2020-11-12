#!/bin/bash

gunicorn --chdir /workspace --bind 0.0.0.0:5005 wsgi:app
