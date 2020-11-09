# /app/dashapp/layout.py

import os
from flask import url_for
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import psycopg2
from psycopg2.extras import RealDictCursor

from app.database import get_conn


def get_navbar():
    """Get a Bootstrap 4 navigation bar for our single-page application's HTML layout"""

    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Blog", href="https://mccarthysean.dev")),
            dbc.NavItem(dbc.NavLink("IJACK", href="https://myijack.com")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("References", header=True),
                    dbc.DropdownMenuItem("Dash", href="https://dash.plotly.com/"),
                    dbc.DropdownMenuItem("Dash Bootstrap Components", href="https://dash-bootstrap-components.opensource.faculty.ai/"),
                    dbc.DropdownMenuItem("Testdriven", href="https://testdriven.io/"),
                ],
                nav=True,
                in_navbar=True,
                label="Links",
            ),
        ],
        brand="Home",
        brand_href="/",
        color="dark",
        dark=True,
    )


def get_sensor_locations():
    """Get a list of different locations of sensors"""
    sql = """
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            distinct 
            location as label, 
            location as value
        FROM sensors;
    """
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        # locations is a list of dictionaries that looks like this, for example:
        # [{'label': 'floor', 'value': 'floor'}]
        locations = cursor.fetchall()
    
    return locations


def get_sensor_types():
    """Get a list of different types of sensors"""
    sql = """
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            distinct 
            type as label, 
            type as value
        FROM sensors;
    """
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        # types is a list of dictionaries that looks like this, for example:
        # [{'label': 'a', 'value': 'a'}]
        types = cursor.fetchall()
    
    return types


def get_sensors_for_dropdown():
    """
    Get a list of sensor dictionaries from our TimescaleDB database, 
    along with lists of distinct sensor types and locations
    """
    sql = """
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            location || ' - ' || type as label,
            id as value
        FROM sensors;
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
            # sensors is a list of dictionaries that looks like this, for example:
            # [{'label': 'floor - a', 'value': 1}]
            sensors = cursor.fetchall()

    sensor_options = []
    for sensor_dict in sensors:
        sensor_options.append({'label': sensor_dict['label'], 'value': sensor_dict['value']})

    return sensor_options


def get_body():
    """Get the body of the layout for our Dash SPA"""

    sensors, sensor_options = get_sensors_for_dropdown()
    types = get_sensor_types()
    locations = get_sensor_locations()

    # The layout starts with a Bootstrap row, containing a Bootstrap column
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.Label('Types of Sensors', style={'margin-top': '1.5em'}),
                    dcc.Dropdown(
                        options=types,
                        value=types[0],
                        id="types_radios"
                    )
                ], xs=12, sm=6, md=4
            ),
            dbc.Col(
                [
                    html.Label('Locations of Sensors', style={'margin-top': '1.5em'}),
                    dcc.Dropdown(
                        options=locations,
                        value=locations[0],
                        id="locations_radios"
                    )
                ], xs=12, sm=6, md=4
            ),
            dbc.Col(
                [
                    html.Label('Sensors', style={'margin-top': '1.5em'}),
                    dcc.Dropdown(
                        options=sensor_options,
                        value=sensor_options[0],
                        id="sensors_radios"
                    )
                ], xs=12, sm=6, md=4
            ),
        ]
    )


def get_layout():
    """Function to get Dash's "HTML" layout"""

    # A Bootstrap 4 container holds the rest of the layout
    return dbc.Container(
        [
            get_navbar(), # nav_menu at the top
            get_body(), 
        ], 
    )

