from apiclient.discovery import build
from apiclient.errors import HttpError
import json
import csv

def get_channel_data(channel_id, youtube):
    videos_list = []
    videos_json = []
    next_page_token = ''
    while next_page_token is not None:
        try:
            request = youtube.search().list(
                channelId=channel_id,
                part='snippet, id',
                maxResults=20,
                pageToken=next_page_token
            )
            response = request.execute()
        except HttpError as e:
            return f'AN ERROR OCCURED: {e}', 'danger', []
        
        videos_json.append(response.get('items'))

        for index in response['items']:
            if index["id"]["kind"] == "youtube#video":
                video = index['id']['videoId']
                videos_list.append(video)

        next_page_token = response.get('nextPageToken')

    try:
        with open(f'C:\\Users\\AdilFarooq\\OneDrive - Blend 360\\Desktop\\BLEND360\\connectors\\data\\{channel_id}.json', 'w') as f:
            json.dump(videos_json, f)
    except IOError as e:
        return f'Error writing to file: {e}', 'danger', videos_list
    
    return 'RETRIVED SUCCESSFULLY', 'success', videos_list

def get_video_data(video_id, youtube):
    comment_idx = 1
    comments = []
    comments_json = []
    replies_json = []
    next_page_token = ''
    while next_page_token is not None:
        try:
            request = youtube.commentThreads().list(
                part='snippet, replies',
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token
            )
            response = request.execute()
        except HttpError as e:
            return f'AN ERROR OCCURED: {e}', 'danger'
        
        comments_json.append(response.get('items'))
        
        for item in response['items']:
            try:
                comment = item['snippet']['topLevelComment']['snippet']
                idx = comment_idx
                comment_data = {
                    'index': idx,
                    'timestamp': comment['publishedAt'],
                    'username': comment['authorDisplayName'],
                    'comment': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'replycount': item['snippet']['totalReplyCount']
                }
                comments.append(comment_data)
                if item['snippet']['totalReplyCount'] > 0:
                    reply_page_token = ''
                    reply_idx = 1
                    while reply_page_token is not None:
                        try:
                            reply_request = youtube.comments().list(
                                part='snippet',
                                parentId=item['id'],
                                maxResults=100,
                                pageToken=reply_page_token,
                                textFormat='plainText'
                            )
                            reply_response = reply_request.execute()
                        except HttpError as e:
                            return f'AN ERROR OCCURED: {e}', 'danger'
                        
                        replies_json.append(reply_response.get('items'))

                        for reply in reply_response['items']:
                            idx = f'{comment_idx}({reply_idx})'
                            reply_idx += 1
                            reply_data = {
                                'index': idx,
                                'timestamp': reply['snippet']['publishedAt'],
                                'username': reply['snippet']['authorDisplayName'],
                                'comment': reply['snippet']['textDisplay'],
                                'likes': reply['snippet']['likeCount'],
                                'replycount': 0
                            }
                            comments.append(reply_data)
                        reply_page_token = reply_response.get('nextPageToken', None)
                comment_idx += 1
            except KeyError:
                return f'COMMENT MISSING DATA: {item}', 'danger'
        next_page_token = response.get('nextPageToken', None)

    try:
        with open(f'C:\\Users\\AdilFarooq\\OneDrive - Blend 360\\Desktop\\BLEND360\\connectors\\data\\{video_id}.csv', mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['index', 'timestamp', 'username', 'comment', 'likes', 'replycount']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for comment in comments:
                writer.writerow(comment)
    except IOError as e:
        return f'Error writing to file: {e}', 'danger'
    
    try:
        with open(f'C:\\Users\\AdilFarooq\\OneDrive - Blend 360\\Desktop\\BLEND360\\connectors\\data\\{video_id}(comments).json', 'w') as f:
            json.dump(comments_json, f)
    except IOError as e:
        return f'Error writing to file: {e}', 'danger'
    
    try:
        with open(f'C:\\Users\\AdilFarooq\\OneDrive - Blend 360\\Desktop\\BLEND360\\connectors\\data\\{video_id}(replies).json', 'w') as f:
            json.dump(replies_json, f)
    except IOError as e:
        return f'Error writing to file: {e}', 'danger'
    
    return 'RETRIVED SUCCESSFULLY', 'success'
