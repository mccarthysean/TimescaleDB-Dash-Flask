# /app/dashapp/callbacks.py

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


def get_sensor_data():
    """
    Get a dictionary of labels/values for the sensors in our TimescaleDB database, 
    to populate the dropdown menu in the layout
    """
    sql = """
        SELECT 
            t2.location, --from the second metadata table
            time, 
            temperature, 
            cpu
        FROM sensor_data t1 
        INNER JOIN sensors t2 
            on t1.sensor_id = t2.id
        ORDER BY 
            t2.location,
            time;
    """
    with psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv("POSTGRES_PORT"), 
        dbname=os.getenv("POSTGRES_DB"), 
        user=os.getenv("POSTGRES_USER"), 
        password=os.getenv("POSTGRES_PASSWORD"), 
        connect_timeout=5
    ) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
    
    print(rows)


def register_callbacks(dash_app):
    """Register the callback functions for the Dash app, within the Flask app"""        

    return None
