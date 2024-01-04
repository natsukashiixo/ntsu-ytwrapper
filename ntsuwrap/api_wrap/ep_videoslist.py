import os
import csv
from pathlib import Path
from io import BytesIO
from datetime import datetime

import requests
import googleapiclient.discovery
import pytz
from PIL import Image

def poll_livestream(video_id: str, API_KEY: str, csv_path: str) -> bool:
    jst = pytz.timezone('Asia/Tokyo')
    
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().list(
        part="snippet,liveStreamingDetails,statistics",
        id=video_id
    )
    raw_response = request.execute()

    csv_file = Path(csv_path)
    
    if not csv_file.is_file():
        with open(csv_file, 'a', newline='') as csvIO:
            writer = csv.writer(csvIO)
            writer.writerow(['ChannelID','ChannelName','Subscribers','VideoID','CurrentLikes','TimestampJST','CCV'])    # Set up superchat tracking in the future?
    
    channel_id = raw_response['items'][0]['snippet']['channelId']
    channel_name = raw_response['items'][0]['snippet']['channelTitle']
    current_subcribers = get_subscribers(channel_id, API_KEY)
    current_likes = int(raw_response['items'][0]['statistics']['likeCount'])
    if raw_response['items'][0]['liveStreamingDetails'].get('concurrentViewers'):
        ccv = int(raw_response['items'][0]['liveStreamingDetails']['concurrentViewers'])
    else:
        ccv = "NaN"

    with open(csv_file, 'a', newline='') as csvIO:
        writer = csv.writer(csvIO)
        writer.writerow([channel_id,channel_name,current_subcribers,video_id,current_likes,datetime.now(jst),ccv])

    currently_live = raw_response['items'][0]['snippet']['liveBroadcastContent']
    if not currently_live == 'live':
        return False
    else:
        return True

def get_thumbnail_and_start_time_livestream(video_id: str, get_thumbnail: bool, thumbnail_folder: str, API_KEY: str) -> datetime:
    ''' This might seem random but I'm simply trying to be conservative with token use.
    Thumbnail only gets saved if it doesn't exist. Filename is simply channelID_videoID.jpg

    Returns a timezone-aware datetime object in UTC time (unless youtube changes it)'''

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().list(
        part="snippet,liveStreamingDetails",
        id=video_id
    )
    raw_response = request.execute()
    channel_id = raw_response['items'][0]['snippet']['channelId']
    thumbnail_url = raw_response['items'][0]['snippet']['thumbnails']['maxres']['url']
    start_timestamp = raw_response['items'][0]['liveStreamingDetails']['scheduledStartTime']
    # save hires video thumbnail if it doesn't exist

    thumb_response = requests.get(thumbnail_url)
    thumb_image = Image.open(BytesIO(thumb_response.content))
    thumb_save_path = fr'./{thumbnail_folder}/{channel_id}_{video_id}.jpg' #    should probably abspath thumbnail folder path tbh
    if not Path(thumb_save_path).is_file():
        thumb_image.save(thumb_save_path)
    
    return start_timestamp

def get_thumbnail_and_start_time_video(video_id: str, thumbnail_folder: str, API_KEY: str) -> datetime:
    ''' This might seem random but I'm simply trying to be conservative with token use.
    Thumbnail only gets saved if it doesn't exist. Filename is simply channelID_videoID.jpg

    Returns a timezone-aware datetime object in UTC time (unless youtube changes it)'''

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().list(
        part="snippet,liveStreamingDetails",
        id=video_id
    )
    raw_response = request.execute()
    channel_id = raw_response['items'][0]['snippet']['channelId']
    thumbnail_url = raw_response['items'][0]['snippet']['thumbnails']['maxres']['url']
    if raw_response['items'][0].get('liveStreamingDetails'):    
        start_timestamp = raw_response['items'][0]['liveStreamingDetails']['scheduledStartTime']
        # save hires video thumbnail if it doesn't exist
    else:
        start_timestamp = raw_response['items'][0]['snippet']['publishedAt']

    thumb_response = requests.get(thumbnail_url)
    thumb_image = Image.open(BytesIO(thumb_response.content))
    thumb_save_path = fr'./{thumbnail_folder}/{channel_id}_{video_id}.jpg' #    should probably abspath thumbnail folder path tbh
    if not Path(thumb_save_path).is_file():
        thumb_image.save(thumb_save_path)
    
    return start_timestamp

def poll_video(video_id: str, API_KEY: str) -> tuple:
    ''' Takes videoID of a youtube video.
    Returns tuple(channel_id, channel_name, current_subcribers, video_id, current_likes, current_views, jst_timestamp)'''
    jst = pytz.timezone('Asia/Tokyo')
    
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    raw_response = request.execute()
    
    channel_id = raw_response['items'][0]['snippet']['channelId']
    channel_name = raw_response['items'][0]['snippet']['channelTitle']
    current_subcribers = get_subscribers(channel_id, API_KEY)   #   I think this function is bugged so im not sure if i should use it
    current_likes = int(raw_response['items'][0]['statistics'].get('likeCount'))
    current_views = int(raw_response['items'][0]['statistics'].get('viewCount'))
    jst_timestamp = datetime.now(jst)

    return	channel_id, channel_name, current_subcribers, video_id, current_likes, current_views, jst_timestamp

    