"""
plot documentation: https://dash.plot.ly/urls
"""
import datetime

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from database import db
from database.db import get_dataframe_from_mongo
from database.db_index import get_index
from html_renderer.render_graph import render_graph, generate_graph_dataframe_dummy
from html_renderer.render_map import render_map_html
from html_renderer.render_table import render_dataframe

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# database.ingest_data('csv')  # ingest all csv data into mongo database

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Traffic Analysis", className="display-4"),
        html.Hr(),
        html.P(
            "ENSF 592 Term Project \n " + str(datetime.date.today()), className="lead"
        ),
        dcc.Dropdown(
            id='db-type',
            options=[
                {'label': 'Traffic Volume', 'value': 'volume'},
                {'label': 'Incidents', 'value': 'incidents'},
            ],
            # value='volume',
            placeholder="(Select a data type)",
            searchable=True,
        ),
        dcc.Dropdown(
            id='data-year',
            options=[
                {'label': '2016', 'value': '2016'},
                {'label': '2017', 'value': '2017'},
                {'label': '2018', 'value': '2018'},
            ],
            # value='2016',
            placeholder="(Select a year)",
            searchable=True,
        ),
        dbc.Nav(
            [
                # dbc.NavLink("Traffic Vol", href="/page-1", id="page-1-link"),
                # dbc.NavLink("Year", href="/page-2", id="page-2-link"),
                dbc.NavLink("Read", href="/page-3", id="page-3-link"),
                dbc.NavLink("Sort", href="/page-4", id="page-4-link"),
                dbc.NavLink("Analysis", href="/page-5", id="page-5-link"),
                dbc.NavLink("Map", href="/page-6", id="page-6-link"),
            ],
            vertical=True,
            pills=True,
        ),
        dbc.Alert(
            'Status',
            id='load-status-bar',
            color='success',
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(3, 7)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        # return True, False, False, False, False, False
        return False, False, False, False
    return [pathname == f"/page-{i}" for i in range(3, 7)]


@app.callback(
    [Output("load-status-bar", "children")],
    [Input("url", "pathname")],
)
def render_status_bar(pathname):
    switcher = {
        '/': 'Status',
        '/page-1': 'Status',
        '/page-2': 'Status',
        '/page-3': 'Successfully read from DB',
        '/page-4': 'Successfully sorted',
        '/page-5': 'Successfully analyzed',
        '/page-6': 'Successfully Written Map'
    }
    status = [switcher.get(pathname, "Invalid status")]
    # print(status)
    return status


@app.callback(Output("page-content", "children"),
              [Input("url", "pathname"), Input("db-type", "value"), Input("data-year", "value")])
def render_page_content(pathname, type_input, year_input):
    # print('print1', pathname, type_input, year_input)
    if pathname in ["/", "/page-1"]:
        return html.Div([
            html.H1('Welcome to ENSF 592 Term Project Demo'),
            html.H2('Presentation topics and presenter:'),
            html.P('Data - Burak Gulseren'),
            html.P('Plot - Sarang Kumar'),
            html.P('Others - Stan Chen')
        ])
    elif pathname == "/page-2":
        return html.P("")
    elif pathname == "/page-3":
        inputs = get_index(type_input, year_input)
        # print(inputs[0],inputs[1])
        df = get_dataframe_from_mongo(inputs[0], inputs[1])
        # df = db.get_dataframe_from_mongo_dummy('csv/2017_Traffic_Volume_Flow.csv')
        return render_dataframe(df)
    elif pathname == "/page-4":
        return html.P("Sort")
    elif pathname == "/page-5":
        test_df = generate_graph_dataframe_dummy()
        return render_graph(test_df, 'year', 'lifeExp', 'graph render test')
    elif pathname == "/page-6":
        # return html.P("Map")
        df = db.get_dataframe_from_mongo_dummy('csv/2017_Traffic_Volume_Flow.csv')
        return render_map_html(df, 'the_geom')
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(port=8888)
