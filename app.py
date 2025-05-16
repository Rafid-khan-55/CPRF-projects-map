import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np

# Load custom Excel data and clean column names
df = pd.read_excel("Updated_CPRF_structure_data.xlsx")
df.columns = df.columns.str.strip()

# Column labels mapped to clean access
column_map = {
    "Structures": "Structures",
    "Location": "Location",
    "Soil Condition": "Soil Condition",
    "Construction Firm": "Construction Firm",
    "Total load (MN)": "Total load (MN)",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "Foundation area (m2)": "Foundation area (m2)",
    "Raft thickness": "Raft thickness",
    "Pile Length (m)": "Pile Length (m)",
    "Pile diameter (m)": "Pile diameter (m)",
    "Pile numbers (n)": "Pile numbers (n)",
    "Pile Spacing": "Pile Spacing",
    "Instrumented Piles": "Instrumented Piles",
    "Pile Load (MN)": "Pile Load (MN)",
    "Max Settlement (mm)": "Max Settlement (mm)",
    "Eccentricity (e)": "Eccentricity (e)",
    "H/B": "H/B",
    "Buoyancy Force (MN)": "Buoyancy Force (MN)",
    "Floors Above Grade": "Floors Above Grade",
    "Basement Floors": "Basement Floors",
    "Foundation Level": "Foundation Level",
    "Earth Pressure Cells": "Earth Pressure Cells",
    "Piezometers": "Piezometers",
    "Extensometers": "Extensometers",
    "Observed Piled raft coefficient": "Observed Piled raft coefficient",
    "Reference 1": "Reference 1",
    "Reference 2": "Reference 2",
    "Reference 3": "Reference 3",
    "Reference 4": "Reference 4",
    "Reference 5": "Reference 5",
    "Reference 6": "Reference 6"
}

# Create the map figure with same-size circular markers and random color assignment
fig = px.scatter_map(
    df,
    lat=column_map["Latitude"],
    lon=column_map["Longitude"],
    hover_name=column_map["Structures"],
    zoom=0
)
fig.update_traces(
    marker={
        'size': 25,
        'opacity': 0.65,
    },
    hovertemplate="%{hovertext}<extra></extra>"
)
fig.update_coloraxes(showscale=False)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Prevent responsive scaling on mobile (fixed width layout)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=1024">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflowY": "auto"
}

CONTENT_STYLE = {
    "top": 0,
    "right": 0,
    "bottom": 0,  # or remove it if you don't want full-height stretching
    #"width": "34rem",
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Foundation System Configuration and Performance\u00a0Parameters", style={"fontSize": "1.3rem", "fontWeight": "bold"}),
        html.Hr(),
        html.Div(id="marker-info", children="Click a marker to see details.", className="lead"),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    dcc.Graph(
        id='map-plot',
        figure=fig,
        style={"height": "90vh"}
    ),
    style=CONTENT_STYLE
)
server=app.server
app.layout = html.Div([sidebar, content])

@app.callback(
    Output("marker-info", "children"),
    Input("map-plot", "clickData")
)
def display_marker_info(clickData):
    if clickData is None:
        return "Click a marker to see details."

    point = clickData['points'][0]
    lat = point['lat']
    lon = point['lon']

    row = df[(df[column_map["Latitude"]] == lat) & (df[column_map["Longitude"]] == lon)]
    if row.empty:
        return "No data found for this point."

    r = row.iloc[0].fillna("")

    def field(label):
        val = r.get(column_map.get(label, label), "")
        return html.P([
            html.Span(f"{label}: ", style={"fontWeight": "bold"}),
            html.Span(f"{val}")
        ], style={"fontSize": "0.85rem"})

    def ref_line(label):
        val = r.get(column_map.get(label, label), "")
        return html.P(f"{val}", style={"fontSize": "0.85rem"}) if val else None

    image_name = r.get("image name", "")
    image_element = html.Img(src=f"assets/{image_name}", style={"width": "100%", "marginBottom": "1rem"})
    
    return html.Div([
    
        html.H5("Project Overview and Loading Conditions", style={"fontSize": "1rem", "fontWeight": "bold", "marginTop": "1rem"}),
        image_element,
        field("Structures"),
        field("Location"),
        field("Soil Condition"),
        field("Construction Firm"),
        field("Total load (MN)"),
        field("Latitude"),
        field("Longitude"),

        html.Hr(), html.H5("Foundation Geometry and Pile Characteristics", style={"fontSize": "1rem", "fontWeight": "bold", "marginTop": "1rem"}),
        field("Foundation area (m2)"),
        field("Raft thickness"),
        field("Pile Length (m)"),
        field("Pile diameter (m)"),
        field("Pile numbers (n)"),
        field("Pile Spacing"),
        field("Instrumented Piles"),
        field("Pile Load (MN)"),

        html.Hr(), html.H5("Structural Response and Subsurface Conditions", style={"fontSize": "1rem", "fontWeight": "bold", "marginTop": "1rem"}),
        field("Max Settlement (mm)"),
        field("Eccentricity (e)"),
        field("H/B"),
        field("Buoyancy Force (MN)"),
        field("Floors Above Grade"),
        field("Basement Floors"),
        field("Foundation Level"),

        html.Hr(), html.H5("Instrumentation Monitoring and Piled Raft Load Transfer\u00a0Behavior", style={"fontSize": "1rem", "fontWeight": "bold", "marginTop": "1rem"}),
        field("Earth Pressure Cells"),
        field("Piezometers"),
        field("Extensometers"),
        field("Observed Piled raft coefficient"),

        html.Hr(), html.H5("References", style={"fontSize": "1rem", "fontWeight": "bold", "marginTop": "1rem"}),
        *[ref_line(f"Reference {i}") for i in range(1, 7) if r.get(column_map.get(f"Reference {i}"), "") != ""]
    ])

if __name__ == "__main__":
    app.run(port=8050)
