import dash
from dash import html, dcc, MATCH, ALL, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from PIL import Image
import dash_auth
import csv
from flask import request

VALID_USERNAME_PASSWORD_PAIRS = {}

with open('users.csv', mode='r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        username, password = row
        VALID_USERNAME_PASSWORD_PAIRS[username] = password

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

tasks = pd.read_csv('tasks.csv')
courses = tasks['Course'].unique()
initial_course = courses[0]
initial_tasks = tasks[tasks['Course'] == initial_course]
pil_img = Image.open("download.png")

header = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand('LEARNING MANAGEMENT SYSTEM', className='text-info'),
        html.A(dbc.NavbarBrand(html.Img(src=pil_img, height='30px'), className='ml-auto'), href='https://www.blend360.com/', style={'color': 'blue'}, target='_blank')
    ], fluid=True, style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
    color='light',
    light=True,
    className='mt-3'
)

footer = dbc.Container([
    dbc.Row([
        dbc.Col(['COPYRIGHT © 2023 | DEVELOPED BY ', html.A('Mdadilfarooq', href='https://github.com/Mdadilfarooq/', style={'color': 'blue'}, target='_blank')])
    ], justify='center', className='py-3')
], fluid=True, className='bg-light')

app.layout = html.Div([
    header,
    html.Hr(),
    html.Div(id='progress-container'),
    html.Hr(),
    dcc.Dropdown(
        id={'type': 'course-dropdown', 'index': 0},
        options=[{'label': course, 'value': course} for course in courses],
        clearable=False,
        value=courses[0],
        persistence=True,
        ),
    html.Hr(),
    html.Div(id={'type': 'table-container', 'index': 0}),
    dbc.Button(
        'SHOW | UPDATE PROGRESS',
        id={'type': 'update-button', 'index': 0},
        className="btn btn-info float-end",
        n_clicks=None
    ),
    dbc.Toast(
        "YOUR PROGRESS HAS BEEN RECORDED",
        id="popup",
        header="BLEND360 | LMS",
        is_open=False,
        icon='info',
        duration=3000,
        style={"position": "fixed", "top": 10, "right": 10, "width": 350}
    ),
    footer
    ],className='container')

@app.callback(
    Output({'type': 'table-container', 'index': MATCH}, 'children'),
    Input({'type': 'course-dropdown', 'index': MATCH}, 'value'),
)
def display_tasks(course):
    tasks = pd.read_csv('tasks.csv')
    course_tasks = tasks[tasks['Course'] == course]
    return dbc.Table([
        html.Thead([html.Tr([html.Th('TASK'), html.Th('COMPLETION')])]),
        html.Tbody([
            html.Tr(
                [
                    html.Td(html.A(f'{task}', href=f'{url}', style={'color': 'blue'}, target='_blank')),
                    html.Td(
                        dcc.Slider(
                            id={'type': 'slide', 'index': idx},
                            value=value,
                            min=0,
                            max=3,
                            step=1
                        )
                    )
                ]
            )
            for idx, task, url, value in zip(
                range(len(course_tasks['Task'])),
                course_tasks['Task'],
                course_tasks['URL'],
                course_tasks['Completion']
            )
        ])
    ], 
    className='mt-3 mb-3',
    striped=True
    )

@app.callback(
    Output('popup', 'is_open'),
    Output('progress-container', 'children'),
    Input({'type': 'update-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'course-dropdown', 'index': ALL}, 'value'),
    State({'type': 'slide', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def update_tasks(update_click, drop_value, slide_values):
    df = tasks[tasks['Course'] == drop_value[0]]
    df['Completion'] = slide_values
    tasks.update(df)
    tasks.to_csv('tasks.csv', index=False)
    progress = (sum(tasks['Completion'])/(len(tasks)*3))*100
    return True, dbc.Progress(
        label='{0:.2f} %'.format(progress),
        value=progress, 
        id="progress", 
        color='info', 
        animated=True, 
        striped=True, 
        style={"height": "30px"}
        )

if __name__ == '__main__':
    app.run(debug=True)