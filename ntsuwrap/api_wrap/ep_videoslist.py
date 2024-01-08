import os
import csv
from pathlib import Path
from io import BytesIO
from datetime import datetime

import requests
import googleapiclient.discovery
import pytz
from PIL import Image

from ntsuwrap import YoutubeTokenBucket
from youtube_status import youtube_status

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

class VideosDotListSingleUpload:
    def __init__(self, api_key: str, channel_id: str, bucket: YoutubeTokenBucket):
        # these should basically never change between classes
        self.api_key = api_key
        self.bucket = bucket
        # these ones change so be careful with copy paste
        #self.TOKENCOST = 1
        #self.channel_id = channel_id

        def _get_response(): # contents of this function should change between classes but name can be the same
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
            api_service_name = "youtube"
            api_version = "v3"
            DEVELOPER_KEY = self.api_key
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey = DEVELOPER_KEY)

            request = youtube.videos().list(
                part="snippet,statistics,contentDetails,topicDetails,status,localizations,suggestions,player", # these are all the public parts
                id=self.channel_id, #p sure this takes a csv string of max 50 elements
                # this class is just for 1 video though
                maxResults=50
            )
            yt_response = request.execute()
            return yt_response

        if youtube_status() and self.bucket.take(self.TOKENCOST):
            self.yt_response = _get_response()

    #items[0]snippet
    def get_title(response):
        pass
    def get_publishtime(response):
        pass # convert str to datetime object
    def get_desc(response):
        pass
    def get_thumbnail(response):
        pass #use decorators or something to indicate quality
    def get_ch_title(response):
        pass
    def get_tags(response):
        pass
    def get_categoryID(response):
        pass
    def is_livestream(response):
        pass #should be None, if not None you're using the wrong class
    def default_audio_lang(response):
        pass #not sure if i even need this

    #items[0]contentDetails
    def get_duration(response):
        pass
    def allowed_countries(response):
        #contentDetails.regionrestriction.allowed[]
        pass
    def blocked_countrues(response):
        #contentDetails.regionrestriction.allowed[]
        pass
    def is_age_restricted(response):
        #contentDetails.contentRating.ytRating
        pass

    #items[0]status
    def get_reject_reason(response):
        pass
    def is_embeddable(response):
        pass
    def is_publicstatsviewable(response):
        pass # do i even need this? views and likes are always accessible even if this is false

    #items[0]statistics
    def get_views(response):
        pass
    def get_likes(response):
        pass
    def get_commentcount(response):
        pass #low prio, can't think of how it's useful atm

    #items[0]player
    def get_embedframe(response):
        pass # they're talking about me needing to set the aspect ratio in my request in the docs, not sure if i should
    def get_embed_height(response):
        pass # only exists if specified in request
    def get_embed_width(response):
        pass # only exists if specified in request

    #items[0]suggestions
    def get_suggested_tags(response):
        pass
    