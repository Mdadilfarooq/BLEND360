import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)

dash.register_page(
    __name__,
    path='/'
)

layout = html.Div([
    dbc.Row(html.Img(src="assets/underconstruction.png", alt="underconstruction", style={"width": "450px", "height": "auto"}), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
    dbc.Row(html.H1('UNDER CONSTRUCTION', style={'font-weight': 'bold'}), className='text-center text-info')
])
