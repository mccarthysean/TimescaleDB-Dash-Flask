# -*- encoding: utf-8 -*-

bind = '0.0.0.0:5005'
threads = 2
accesslog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

# gevent setup
workers = 4
worker_class = 'gevent'
# The maximum number of simultaneous clients.
# This setting only affects the Eventlet and Gevent worker types.
worker_connections = 10

