# import dash_core_components as dcc
from dash import Dash

import flask

server = flask.Flask(__name__) # define flask app.server


external_stylesheets = ["assets/1bootstrap.css", "assets/2style.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets,
                server = server,
                suppress_callback_exceptions= True,
            meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ])

