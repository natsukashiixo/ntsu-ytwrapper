import os
from datetime import datetime
import googleapiclient.discovery
import pytz
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

class VideosDotList:
    def __init__(self, api_key: str, video_id: str, bucket: YoutubeTokenBucket):
        # these should basically never change between classes
        self.api_key = api_key
        self.bucket = bucket
        # these ones change so be careful with copy paste
        self.TOKENCOST = 1
        self.video_id = video_id

        def _get_response() -> list: # contents of this function should change between classes but name can be the same
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
            api_service_name = "youtube"
            api_version = "v3"
            DEVELOPER_KEY = self.api_key
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey = DEVELOPER_KEY)

            request = youtube.videos().list(
                part="snippet,statistics,contentDetails,topicDetails,status,localizations,suggestions,player,liveStreamingDetails", # these are all the public parts
                id=self.video_id, #p sure this takes a csv string of max 50 elements
                # this class is just for 1 video though
                maxResults=50
            )
            yt_response = request.execute()
            return yt_response

        if youtube_status() and self.bucket.take(self.TOKENCOST):
            self.yt_response = _get_response()
    
    def first_item(self) -> dict:
        return self.yt_response['items'][0] if self.yt_response else {}

    def item_by_index(self, x: int) -> dict:
        return self.yt_response['items'][x] if self.yt_response else {}

    def item_by_snippet_kwp(self, keyword: str, value) -> dict:
        for i, item in enumerate(self.yt_response.get('items', [])):
            if item.get('snippet', {}).get(keyword) == value:
                return item
        print(f'key value pair {keyword}: {value} not found')
        return {}
    
    def all_items(self) -> list:
        return self.yt_response.get('items', [])
    
class ParseVideoItem: #might only need this one and then do some checks if people are trying to get livestreamdata from uploaded videos
    def __init__(self, item_dict) -> None:
        self.item_dict = item_dict

    #items[0]snippet
    def get_title(self) -> str:
        return self.item_dict['snippet'].get('')
        pass
    def get_publishtime(self) -> datetime:
        return self.item_dict['snippet'].get('')
        pass # convert str to datetime object
    def get_desc(self) -> str:
        return self.item_dict['snippet'].get('')
        pass
    def get_thumbnail(self) -> str:
        return self.item_dict['snippet'].get('')
        pass #use decorators or something to indicate quality
    def get_ch_id(self) -> str:
        return self.item_dict['snippet'].get('')
        pass
    def get_ch_title(self) -> str:
        return self.item_dict['snippet'].get('')
        pass
    def get_tags(self) -> list:
        return self.item_dict['snippet'].get('')
        pass
    def get_categoryID(self) -> int:
        return self.item_dict['snippet'].get('')
        pass
    def is_livestream(self) -> bool:
        return self.item_dict['snippet'].get('')
        pass #should not be None, if None you're using the wrong class
    def currently_live(self) -> bool:
        return self.item_dict['snippet'].get('')
        pass #youtube tells you this in a string, not a bool btw
    def default_audio_lang(self) -> str:
        return self.item_dict['snippet'].get('')
        pass #not sure if i even need this, i18n mentioned in the docs

    #items[0]contentDetails
    def get_duration(self) -> int:
        self.item_dict['contentDetails'].get('')
        pass #convert to int in seconds probs
    def allowed_countries(self) -> list:
        self.item_dict['contentDetails'].get('')
        #contentDetails.regionrestriction.allowed[]
        pass
    def blocked_countries(self) -> list:
        self.item_dict['contentDetails'].get('')
        #contentDetails.regionrestriction.allowed[]
        pass
    def is_age_restricted(self) -> bool:
        self.item_dict['contentDetails'].get('')
        #contentDetails.contentRating.ytRating
        pass

    #items[0]status
    def get_reject_reason(self) -> str:
        self.item_dict['status'].get('')
        pass
    def is_embeddable(self) -> bool:
        self.item_dict['status'].get('')
        pass
    def is_publicstatsviewable(self) -> bool:
        self.item_dict['status'].get('')
        pass # do i even need this? views and likes are always accessible even if this is false

    #items[0]statistics
    def get_views(self) -> int:
        self.item_dict['statistics'].get('')
        pass
    def get_likes(self) -> int:
        self.item_dict['statistics'].get('')
        pass
    def get_commentcount(self) -> int:
        self.item_dict['statistics'].get('')
        pass #low prio, can't think of how it's useful atm

    #items[0]player
    def get_embedframe(self) -> str:
        self.item_dict['player'].get('')
        pass # they're talking about me needing to set the aspect ratio in my request in the docs, not sure if i should
    def get_embed_height(self) -> int:
        self.item_dict['player'].get('')
        pass # only exists if specified in request
    def get_embed_width(self) -> int:
        self.item_dict['player'].get('')
        pass # only exists if specified in request

    #items[0]suggestions
    def get_suggested_tags(self) -> list:
        self.item_dict['suggestions'].get('')
        pass

    #items[0]liveStreamingDetails
    #all time related ones need str -> datetime parsing
    def is_livestream(self) -> bool:
        if not self.item_dict.get('liveStreamingDetails'):
            #eventually raise custom exception
            return False
        return True
    def get_scheduled_start(self) -> datetime:
        self.item_dict['liveStreamingDetails'].get('')
        pass
    def get_scheduled_end(self) -> datetime:
        self.item_dict['liveStreamingDetails'].get('')
        pass
    def get_actual_start(self) -> datetime:
        self.item_dict['liveStreamingDetails'].get('')
        pass
    def get_actual_end(self) -> datetime:
        self.item_dict['liveStreamingDetails'].get('')
        pass
    def get_ccv(self) -> int:
        self.item_dict['liveStreamingDetails'].get('')
        pass