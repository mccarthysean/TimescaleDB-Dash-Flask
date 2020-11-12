#!/bin/bash

# Finally, start the Gunicorn app server for the Flask app
gunicorn --config /gunicorn-cfg.py wsgi:app
