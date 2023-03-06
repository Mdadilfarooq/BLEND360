import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from apiclient.discovery import build
from apiclient.errors import HttpError
import csv
import re
from dotenv import load_dotenv
import os

load_dotenv()

url_pattern = r"(http|https)://(www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]+)"
youtube = build('youtube', 'v3', developerKey=os.getenv("api_key"))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])

header = dbc.Navbar(
    dbc.Container([
        html.Div([
            dbc.NavbarBrand('SOCIAL MEDIA CONNECTOR', className='text-info', style={'font-weight': 'bold'}),
        ]),
        html.Div([
            dbc.Col(
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("HOME", href="#"),
                        dbc.DropdownMenuItem("YOUTUBE", href="#"),
                        dbc.DropdownMenuItem("LINKEDIN", href="#")
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

app.layout = html.Div([
    header,
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col(dbc.Input(id="channel-id", placeholder="ENTER CHANNEL ID", type="text"), width= 10),
            dbc.Col(dbc.Button('RETRIEVE VIDEOS', id='get_videos', color='info', n_clicks=None, disabled = False, style={'display': 'inline-block', 'width':'100%'}), width = 2)
        ])
    ]),
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col(dcc.Dropdown(id="videos", multi=True))
        ], class_name='mt-3'),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id="comment-properties", multi=True), width= 10),
            dbc.Col(dbc.Button('RETRIEVE COMMENTS', id='get_comments', color='info', n_clicks=None, disabled = False, style={'display': 'inline-block', 'width':'100%'}), width = 2)
        ], class_name='mt-3')
    ], id='videos-container', style={'display':'none'}),
    dbc.Toast(
        id="popup",
        header="BLEND360 | SMC",
        is_open=False,
        dismissable = True,
        style={"position": "fixed", "top": 10, "right": 10, "width": 350, "opacity": 1}
    ),
    html.Hr(),
    footer
], className='container')

# @app.callback(
#     Output('popup', 'children'),
#     Output('popup', 'icon'),
#     Output('popup', 'is_open'),
#     Output('video-url', 'value'),
#     Input('trigger', 'n_clicks'),
#     State('video-url', 'value'),
#     prevent_initial_call=True
# )
# def build_csv(trigger, videoUrl):
#     if re.match(url_pattern, videoUrl):
        
#         comment_idx = 1
#         video_id = re.findall(url_pattern, videoUrl)[0][2]

#         comments = []
#         next_page_token = ''
#         while next_page_token is not None:
#             try:
#                 request = youtube.commentThreads().list(
#                     part='snippet, replies',
#                     videoId=video_id,
#                     maxResults=100,
#                     pageToken=next_page_token,
#                     textFormat='plainText'
#                 )
#                 response = request.execute()
#             except HttpError as e:
#                 return f'AN ERROR OCCURED: {e}', 'danger', True, ''

#             for item in response['items']:
#                 try:
#                     comment = item['snippet']['topLevelComment']['snippet']
#                     idx = comment_idx
#                     comment_data = {
#                         'index': idx,
#                         'timestamp': comment['publishedAt'],
#                         'username': comment['authorDisplayName'],
#                         'comment': comment['textDisplay'],
#                         'likes': comment['likeCount'],
#                         'replycount': item['snippet']['totalReplyCount']
#                     }
#                     comments.append(comment_data)

#                     if item['snippet']['totalReplyCount'] > 0:
#                         reply_page_token = ''
#                         reply_idx = 1
#                         while reply_page_token is not None:
#                             try:
#                                 reply_request = youtube.comments().list(
#                                     part='snippet',
#                                     parentId=item['id'],
#                                     maxResults=100,
#                                     pageToken=reply_page_token,
#                                     textFormat='plainText'
#                                 )
#                                 reply_response = reply_request.execute()
#                             except HttpError as e:
#                                 return f'AN ERROR OCCURED: {e}', 'danger', True, ''

#                             for reply in reply_response['items']:
#                                 idx = f'{comment_idx}[{reply_idx}]'
#                                 reply_idx += 1
#                                 reply_data = {
#                                     'index': idx,
#                                     'timestamp': reply['snippet']['publishedAt'],
#                                     'username': reply['snippet']['authorDisplayName'],
#                                     'comment': reply['snippet']['textDisplay'],
#                                     'likes': reply['snippet']['likeCount'],
#                                     'replycount': 0
#                                 }
#                                 comments.append(reply_data)
#                             reply_page_token = reply_response.get('nextPageToken', None)

#                     comment_idx += 1      
#                 except KeyError:
#                     return f'COMMENT MISSING DATA: {item}', 'danger', True, ''
                
#             next_page_token = response.get('nextPageToken', None)

#         try:
#             with open(f'C:\\Users\\AdilFarooq\\OneDrive - Blend 360\\Desktop\\BLEND360\\connectors\\data\\{video_id}.csv', mode='w', newline='', encoding='utf-8') as file:
#                 fieldnames = ['index', 'timestamp', 'username', 'comment', 'likes', 'replycount']
#                 writer = csv.DictWriter(file, fieldnames=fieldnames)
#                 writer.writeheader()
#                 for comment in comments:
#                     writer.writerow(comment)
#         except IOError as e:
#             return f'Error writing to file: {e}', 'danger', True, ''
        
#         return 'RETRIVED SUCCESSFULLY', 'success', True, ''
    
#     else:
#         return f'INVALID URL: {videoUrl}', 'warning', True, ''

if __name__ == '__main__':
    app.run(debug=True)
