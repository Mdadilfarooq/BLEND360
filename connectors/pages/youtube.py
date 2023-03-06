import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
from apiclient.discovery import build
from functions.connectors import get_channel_data, get_video_data
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("api_key")
api_version = os.getenv("api_version")
api_service_name = os.getenv("api_service_name")
youtube = build(api_service_name, api_version, developerKey=api_key)

dash.register_page(
    __name__,
    path='/youtube'
)

layout = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col(dbc.Input(id="channel-id", placeholder="ENTER CHANNEL ID", type="text"), width= 10),
            dbc.Col(dbc.Button('RETRIEVE VIDEOS', id='get_videos', color='info', n_clicks=None, disabled = False, style={'display': 'inline-block', 'width':'100%'}), width = 2)
        ])
    ]),
    html.Div([
        dbc.Row([
            dbc.Col(dcc.Dropdown(id="videos", multi=True, style={'border-width': '2px', 'border-color': 'black'}), width = 10),
            dbc.Col(dbc.Button('RETRIEVE COMMENTS', id='get_comments', color='info', n_clicks=None, disabled = False, style={'display': 'inline-block', 'width':'100%'}), width = 2)
        ], class_name='mt-3')
    ], id='video-container', hidden=True),
    dbc.Toast(
        id="popup-channel",
        header="BLEND360 | SMC",
        is_open=False,
        dismissable = True,
        style={"position": "fixed", "top": 10, "right": 10, "width": 350, "opacity": 1}
    ),
    dbc.Toast(
        id="popup-video",
        header="BLEND360 | SMC",
        is_open=False,
        dismissable = True,
        style={"position": "fixed", "top": 10, "right": 10, "width": 350, "opacity": 1}
    )
])

@callback(
    Output('popup-channel', 'children'),
    Output('popup-channel', 'icon'),
    Output('popup-channel', 'is_open'),
    Output('videos', 'options'),
    Output('video-container', 'hidden'),
    Input('get_videos', 'n_clicks'),
    State('channel-id', 'value'),
    prevent_initial_call=True
)
def get_videos(trigger, channel_id):
    if not channel_id:
        return f'INVALID CHANNEL ID: {channel_id}', 'warning', True, [], True
    else:
        data = get_channel_data(channel_id, youtube)
        if not data[2]:
            return data[0], data[1], True, [], True
        else:
            return data[0], data[1], True, data[2], False
        
@callback(
    Output('popup-video', 'children'),
    Output('popup-video', 'icon'),
    Output('popup-video', 'is_open'),
    Input('get_comments', 'n_clicks'),
    State('videos', 'value'),
    prevent_initial_call = True
)
def get_comments(trigger, selected_videos):
    if not selected_videos:
        return 'PLEASE SELECT VIDEOS', 'warning', True
    else:
        for video_id in selected_videos:
            data = get_video_data(video_id, youtube)
            if data[1] == 'danger' or data[1] == 'warning':
                return data[0], data[1], True  
        return 'RETRIVED SUCCESSFULLY', 'success', True
