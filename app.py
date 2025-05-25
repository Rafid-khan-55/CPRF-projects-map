import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import plotly.express as px
import pandas as pd

# Load and clean data
df = pd.read_excel("Updated_CPRF_structure_data.xlsx")
df.columns = df.columns.str.strip()

# Create Scattergeo map figure
fig = px.scatter_geo(
    df,
    lat="Latitude",
    lon="Longitude",
    hover_name="Structures",
    projection="natural earth"
)
fig.update_traces(
    name="CPRF details & Soil condition Data",
    showlegend=True,
    marker=dict(size=30, color="rgb(240, 49, 49)", line=dict(width=2, color="white")),
    hovertemplate="%{hovertext}<extra></extra>"
)
fig.update_geos(
    showland=True,
    landcolor="rgb(217,217,217)",
    showcountries=True,
    showcoastlines=False,
    countrycolor="white",
    showframe=False,
    resolution=50
)
fig.update_layout(
    legend=dict(x=0.99, y=0.01, xanchor="right", yanchor="bottom"),
    margin=dict(l=0, r=0, t=0, b=0),
    autosize=True
)

# App setup
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Styles
SIDEBAR_STYLE = {
    "position": "fixed", "top": 0, "left": 0, "bottom": 0,
    "width": "25%", "padding": "2rem 1rem", "background-color": "#f8f9fa",
    "overflowY": "auto"
}
CONTENT_STYLE = {
    "margin-left": "25%", "padding": "2rem 1rem"
}

# Define UI sections and their fields
SECTIONS = [
    ("Project Overview and Loading Conditions", [
        "Structures", "Location", "Soil Condition",
        "Construction Firm", "Total load (MN)", "Latitude", "Longitude"
    ]),
    ("Foundation Geometry and Pile Characteristics", [
        "Foundation area (m2)", "Raft thickness (m)", "Pile Length (m)",
        "Pile diameter (m)", "Pile numbers (n)", "Pile Spacing",
        "Instrumented Piles", "Pile Load (MN)"
    ]),
    ("Structural Response and Subsurface Conditions", [
        "Max Settlement (mm)", "Eccentricity e (m)", "H/B",
        "Buoyancy Force (MN)", "Floors Above Grade", "Basement Floors",
        "Foundation Level (m)"
    ]),
    ("Instrumentation Monitoring and Piled Raft Load Transfer Behavior", [
        "Earth Pressure Cells", "Piezometers", "Extensometers",
        "Observed Piled raft coefficient"
    ]),
    ("References", [f"Reference {i}" for i in range(1, 7)])
]

# Layout
sidebar = html.Div([
    html.H2(
        "Foundation System Configuration and Performance Parameters",
        style={"fontSize": "1.3rem", "fontWeight": "bold"}
    ),
    html.Hr(),
    html.Div(id="marker-info", children="Click a marker to see details.", className="lead")
], style=SIDEBAR_STYLE)

content = html.Div(
    dcc.Graph(id='map-plot', figure=fig, style={"height": "90vh"}),
    style=CONTENT_STYLE
)

app.layout = html.Div([sidebar, content])

# Helper to render label/value lines
def make_paragraph(label, value, bold=True):
    children = []
    if bold:
        children.append(html.Span(f"{label}: ", style={"fontWeight": "bold"}))
    children.append(html.Span(value if value else "N/A"))
    return html.P(children, style={"fontSize": "0.85rem"})

@app.callback(
    Output("marker-info", "children"),
    Input("map-plot", "clickData")
)
def display_marker_info(clickData):
    if not clickData:
        return "Click a marker to see details."

    lat = clickData['points'][0]['lat']
    lon = clickData['points'][0]['lon']

    match = df[(df['Latitude'] == lat) & (df['Longitude'] == lon)]
    if match.empty:
        return "No data found for this point."
    r = match.iloc[0].fillna("")

    # Build detail sections
    children = []
    for title, fields in SECTIONS:
        children.append(html.H5(title, style={"fontSize": "1rem", "fontWeight": "bold", "marginTop": "1rem"}))
        if title == SECTIONS[0][0] and r.get("image name", ""):
            children.append(html.Img(
                src=f"assets/{r['image name']}",
                style={"width": "100%", "marginBottom": "1rem"}
            ))
        for f in fields:
            value = str(r.get(f, ""))
            if title == "References" and not value.strip():
                continue
            para = make_paragraph(f, value, bold=(title != "References"))
            children.append(para)
        children.append(html.Hr())

    return html.Div(children)

if __name__ == "__main__":
    app.run(port=8050)
