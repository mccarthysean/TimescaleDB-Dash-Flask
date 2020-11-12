# /app/dashapp/callbacks.py

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from psycopg2.extras import RealDictCursor
import pandas as pd
import plotly.graph_objs as go

# Local imports
from app.database import get_conn


def get_sensor_locations(type_):
    """Get a list of different locations of sensors"""
    sql = f"""
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            distinct 
            location as label, 
            location as value
        FROM sensors
        WHERE type = '{type_}';
    """
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        # locations is a list of dictionaries that looks like this, for example:
        # [{'label': 'floor', 'value': 'floor'}]
        locations = cursor.fetchall()
    
    return locations


def get_sensors(type_, location):
    """
    Get a list of sensor dictionaries from our TimescaleDB database, 
    along with lists of distinct sensor types and locations
    """
    sql = f"""
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            location || ' - ' || type as label,
            id as value
        FROM sensors
        WHERE 
            type = '{type_}'
            and location = '{location}';
    """
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        # sensors is a list of dictionaries that looks like this, for example:
        # [{'label': 'floor - a', 'value': 1}]
        sensors = cursor.fetchall()

    return sensors


def get_sensor_time_series_data(sensor_id):
    """Get the time series data in a Pandas DataFrame, for the sensor chosen in the dropdown"""

    sql = f"""
        SELECT 
            --Get the 3-hour average instead of every single data point
            time_bucket('03:00:00'::interval, time) as time,
            sensor_id,
            avg(temperature) as temperature,
            avg(cpu) as cpu
        FROM sensor_data
        WHERE sensor_id = {sensor_id}
        GROUP BY 
            time_bucket('03:00:00'::interval, time), 
            sensor_id
        ORDER BY 
            time_bucket('03:00:00'::interval, time), 
            sensor_id;
    """

    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [str.lower(x[0]) for x in cursor.description]

    df = pd.DataFrame(rows, columns=columns)
    
    return df


def get_graph(trace, title):
    """Get a Plotly Graph object for Dash"""
    
    return dcc.Graph(
        # Disable the ModeBar with the Plotly logo and other buttons
        config=dict(
            displayModeBar=False
        ),
        figure=go.Figure(
            data=[trace],
            layout=go.Layout(
                title=title,
                plot_bgcolor="white",
                xaxis=dict(
                    autorange=True,
                    # Time-filtering buttons above chart
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                label="1d",
                                step="day",
                                stepmode="backward"),
                            dict(count=7,
                                label="7d",
                                step="day",
                                stepmode="backward"),
                            dict(count=1,
                                label="1m",
                                step="month",
                                stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    type = "date",
                    # Alternative time filter slider
                    rangeslider = dict(
                        visible = True
                    )
                )
            )
        )
    )


def register_callbacks(dash_app):
    """Register the callback functions for the Dash app, within the Flask app""" 

    @dash_app.callback(
        [
            Output("locations_dropdown", "options"),
            Output("locations_dropdown", "value")
        ],
        [
            Input("types_dropdown", "value")
        ]
    )
    def get_locations_from_types(types_dropdown_value):
        """Get the location options, based on the type of sensor chosen"""

        # First get the location options (i.e. a list of dictionaries)
        location_options = get_sensor_locations(types_dropdown_value)

        # Default to the first item in the list, 
        # and get the "value" from the dictionary
        location_value = location_options[0]["value"]

        return location_options, location_value


    @dash_app.callback(
        [
            Output("sensors_dropdown", "options"),
            Output("sensors_dropdown", "value")
        ],
        [
            Input("types_dropdown", "value"),
            Input("locations_dropdown", "value")
        ]
    )
    def get_sensors_from_locations_and_types(types_dropdown_value, locations_dropdown_value):
        """Get the sensors available, based on both the location and type of sensor chosen"""

        # First get the sensor options (i.e. a list of dictionaries)
        sensor_options = get_sensors(types_dropdown_value, locations_dropdown_value)

        # Default to the first item in the list, 
        # and get the "value" from the dictionary
        sensor_value = sensor_options[0]["value"]

        return sensor_options, sensor_value


    @dash_app.callback(
        Output("time_series_chart_col", "children"),
        [Input("sensors_dropdown", "value")],
        [
            State("types_dropdown", "value"),
            State("locations_dropdown", "value")
        ]
    )
    def get_time_series_chart(
        sensors_dropdown_value, 
        types_dropdown_value, 
        locations_dropdown_value
    ):
        """Get the sensors available, based on both the location and type of sensor chosen"""

        df = get_sensor_time_series_data(sensors_dropdown_value)
        x = df["time"]
        y1 = df["temperature"]
        y2 = df["cpu"]
        title = f"Location: {locations_dropdown_value} - Type: {types_dropdown_value}"

        trace1 = go.Scatter(
            x=x,
            y=y1,
            name="Temp"
        )
        trace2 = go.Scatter(
            x=x,
            y=y2,
            name="CPU"
        )

        # Create two graphs using the traces above
        graph1 = get_graph(trace1, f"Temperature for {title}")
        graph2 = get_graph(trace2, f"CPU for {title}")

        return html.Div(
            [
                dbc.Row(dbc.Col(graph1)),
                dbc.Row(dbc.Col(graph2)),
            ]
        )
