from apiclient.discovery import build
import json



# api_key = 'AIzaSyBwQkEfKDpgADz1AXGytUl3GT-pqC9ihw4'
# youtube = build('youtube', 'v3', developerKey=api_key)
# channel_id = 'UCYLS9TSah19IsB8yyUpiDzg'

# # https://www.googleapis.com/youtube/v3/search?key=AIzaSyBwQkEfKDpgADz1AXGytUl3GT-pqC9ihw4&channelId=UC_x5XG1OV2P6uZZ5FSM9Ttw&part=snippet,id&order=date&maxResults=20

# videoList = []
# next_page_token = ''
# while next_page_token is not None:
#     request = youtube.search().list(
#                         channelId=channel_id,
#                         part='snippet, id',
#                         order='date',
#                         maxResults=50,
#                         pageToken=next_page_token
#                     )
#     response = request.execute()

#     videos = response.get('items', [])

#     if not videos:
#         break

#     videoList.extend(videos)
#     next_page_token = response.get('nextPageToken')

# with open(f'C:\\Users\\AdilFarooq\\OneDrive - Blend 360\\Desktop\\BLEND360\\connectors\\data\\{channel_id}.json', 'w') as f:
#     f.write('[')
#     for i, video in enumerate(videoList):
#         json.dump(video, f)
#         if i != len(videoList) - 1:
#             f.write(',\n')
#     f.write(']')
