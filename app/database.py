
import os
import psycopg2
# from psycopg2.extras import DictCursor
# import click
# from flask import current_app
from flask import g
# from flask.cli import with_appcontext
# import boto3
# import logging
# import time


def get_conn():
    """
    Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'conn' not in g:
        g.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv("POSTGRES_PORT"), 
            dbname=os.getenv("POSTGRES_DB"), 
            user=os.getenv("POSTGRES_USER"), 
            password=os.getenv("POSTGRES_PASSWORD"), 
            connect_timeout=5
        )
    
    return g.conn


def close_db(e=None):
    """
    If this request connected to the database, close the
    connection.
    """
    conn = g.pop('conn', None)

    if conn is not None:
        conn.close()
    
    return None


def init_app(app):
    """
    Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
