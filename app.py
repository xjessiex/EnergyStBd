#!/usr/bin/env python
# coding: utf-8

import os

import dash as dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=external_stylesheets)

# set app layout
app.layout = html.Div(children=[
    html.Label("Date Range of Inquiry"),
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=dt(2015, 1, 1),
        max_date_allowed=dt(2019, 5, 5),
        initial_visible_month=dt(2018, 7, 23),
        end_date = dt(2018, 7, 24)
    ),
    html.Div(id="output-date-picker-range")
])


@app.callback(dash.dependencies.Output("output-date-picker-range", "children"),
              [dash.dependencies.Input('date-picker-range', "start_date"),
               dash.dependencies.Input('date-picker-range', "end_date")])
def update_output(start_date, end_date):
    string_prefix = "You have selected: "
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix


if __name__ == '__main__':
    app.run_server(debug=True)
