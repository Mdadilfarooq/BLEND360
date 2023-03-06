import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SKETCHY])
server = app.server

header = dbc.Navbar(
    dbc.Container([
        html.Div([
            dbc.NavbarBrand('SOCIAL MEDIA CONNECTOR', className='text-info', style={'font-weight': 'bold'}),
        ]),
        html.Div([
            dbc.Col(
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("HOME", href="/"),
                        dbc.DropdownMenuItem("YOUTUBE", href="/youtube"),
                        dbc.DropdownMenuItem("LINKEDIN", href="/linkedin")
                    ],
                    nav=True,
                    in_navbar=True,
                    label="NAVIGATE",
                )
            ),
            html.Span(style={'border-left': '3px solid gray', 'height': '30px', 'margin': '0 10px'}),
            dbc.Col(
                html.A(
                    dbc.NavbarBrand(html.Img(src='assets/download.png', height='40px'), className='ml-auto'), 
                    href='https://www.blend360.com/', 
                    target='_blank',
                ),
                width='auto'
            )
        ], className='d-flex align-items-center')
    ]),
    color='light',
    light=True,
    className='mt-3'
)

footer = dbc.Container([
    dbc.Row([
        dbc.Col(['COPYRIGHT © 2023 | DEVELOPED BY ', html.A('Mdadilfarooq', href='https://github.com/Mdadilfarooq/', style={'color': 'blue'}, target='_blank')])
    ], justify='center', className='py-3')
    ], fluid=True, style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'position': 'fixed', 'bottom': 0})

app.layout = dbc.Container([
    header,
    html.Hr(),
    dash.page_container,
    html.Hr(),
    footer
], className='container')

if __name__ == "__main__":
    app.run(debug=True)