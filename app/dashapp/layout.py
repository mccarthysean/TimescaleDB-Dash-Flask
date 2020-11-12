# /app/dashapp/layout.py

import os

from flask import url_for
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from psycopg2.extras import RealDictCursor

# Local imports
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


def get_body():
    """Get the body of the layout for our Dash SPA"""

    types = get_sensor_types()

    # The layout starts with a Bootstrap row, containing a Bootstrap column
    return dbc.Row(
        [
            # 1st column and dropdown (NOT empty at first)
            dbc.Col(
                [
                    html.Label('Types of Sensors', style={'margin-top': '1.5em'}),
                    dcc.Dropdown(
                        options=types,
                        value=types[0]['value'],
                        id="types_dropdown"
                    )
                ], xs=12, sm=6, md=4
            ),
            # 2nd column and dropdown (empty at first)
            dbc.Col(
                [
                    html.Label('Locations of Sensors', style={'margin-top': '1.5em'}),
                    dcc.Dropdown(
                        # options=None,
                        # value=None,
                        id="locations_dropdown"
                    )
                ], xs=12, sm=6, md=4
            ),
            # 3rd column and dropdown (empty at first)
            dbc.Col(
                [
                    html.Label('Sensors', style={'margin-top': '1.5em'}),
                    dcc.Dropdown(
                        # options=None,
                        # value=None,
                        id="sensors_dropdown"
                    )
                ], xs=12, sm=6, md=4
            ),
        ]
    )


def get_chart_row():
    """Create a row and column for our Plotly/Dash time series chart"""

    return dbc.Row(
        dbc.Col(
            id="time_series_chart_col"
        )
    )


def get_layout():
    """Function to get Dash's "HTML" layout"""

    # A Bootstrap 4 container holds the rest of the layout
    return dbc.Container(
        [
            get_navbar(),
            get_body(), 
            get_chart_row(),
        ], 
    )

