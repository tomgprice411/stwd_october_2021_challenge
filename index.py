from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from app import server
from apps import main


from environment.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK

header = dbc.Container([
    dbc.Row([
        dbc.Col(html.P(""), className = "col-2"),
        dbc.Col(html.H1("Monthly Average House Prices in Hamilton 2019-2021"), className = "col-8 col-center"),
        dbc.Col(html.P(""), className = "col-2")
    ])
])

app.layout = html.Div([
    dcc.Location(id = "url", refresh = False),
    header,
    html.Div(id = "page-content")
])

#callback to load the correct page content
@app.callback(Output("page-content", "children"),
                Input("url", "pathname"))
def create_page_content(pathname):
    if pathname == "/main":
        return main.layout
    else:
        return main.layout


if __name__ == "__main__":
    app.run_server(
        host=APP_HOST,
        port=APP_PORT,
        debug=APP_DEBUG,
        dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )
