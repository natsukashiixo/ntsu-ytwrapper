import os
from datetime import datetime
import googleapiclient.discovery
import pytz
import isodate
from ntsuwrap import YoutubeTokenBucket
from youtube_status import youtube_status

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
        return self.item_dict['snippet'].get('title')
    
    def get_publishtime(self, tz='UTC') -> datetime:
        '''tz variable takes a pytz supported timezone string.
        Defaults to UTC if not specified.'''
        yt_time = self.item_dict['snippet'].get('publishedAt', None)
        dt = datetime.strptime(yt_time, "%Y-%m-%dT%H:%M:%SZ")
        _tz = pytz.timezone(tz)
        localized_dt = _tz.localize(dt)
        return localized_dt
    
    def get_desc(self) -> str:
        return self.item_dict['snippet'].get('description')
    
    def get_thumbnail(self) -> str:
        '''object
        Valid key values are:
        default – The default thumbnail image. The default thumbnail for a video – or a resource that refers to a video, such as a playlist item or search result – is 120px wide and 90px tall. The default thumbnail for a channel is 88px wide and 88px tall.
        medium – A higher resolution version of the thumbnail image. For a video (or a resource that refers to a video), this image is 320px wide and 180px tall. For a channel, this image is 240px wide and 240px tall.
        high – A high resolution version of the thumbnail image. For a video (or a resource that refers to a video), this image is 480px wide and 360px tall. For a channel, this image is 800px wide and 800px tall.
        standard – An even higher resolution version of the thumbnail image than the high resolution image. This image is available for some videos and other resources that refer to videos, like playlist items or search results. This image is 640px wide and 480px tall.
        maxres – The highest resolution version of the thumbnail image. This image size is available for some videos and other resources that refer to videos, like playlist items or search results. This image is 1280px wide and 720px tall.'''
        return self.item_dict['snippet'].get('thumbnails')
     #use decorators or something to indicate quality
    
    def get_ch_id(self) -> str:
        return self.item_dict['snippet'].get('channelId')
    
    def get_ch_title(self) -> str:
        return self.item_dict['snippet'].get('channelTitle')
    
    def get_tags(self) -> list:
        return self.item_dict['snippet'].get('tags')
    
    def get_categoryID(self) -> str:
        return self.item_dict['snippet'].get('categoryID')
        #youtube doesn't seem to have much love for this functionality tbh
    
    def is_livestream(self) -> bool:
        if not self.item_dict['snippet'].get('liveBroadcastContent') == 'none':
            return True
        return False
    
    def currently_live(self) -> bool:
        if self.item_dict['snippet'].get('liveBroadcastContent') == 'live':
            return True
        return False
     #youtube tells you this in a string, not a bool btw
    
    def is_upcoming(self):
        if self.item_dict['snippet'].get('liveBroadcastContent') == 'upcoming':
            return True
        return False

    def default_audio_lang(self) -> str:
        return self.item_dict['snippet'].get('defaultAudioLanguage')
     #not sure if i even need this, i18n mentioned in the docs

    #items[0]contentDetails
    def get_duration(self) -> int:
        yt_dur = self.item_dict['contentDetails'].get('duration')
        sec = isodate.parse_duration(yt_dur).total_seconds()
        return sec

    def allowed_countries(self) -> list:
        return self.item_dict['contentDetails'].get('regionRestriction').get('allowed', [])
    
    def blocked_countries(self) -> list:
        return self.item_dict['contentDetails'].get('regionRestriction').get('blocked', [])
    
    def is_age_restricted(self) -> bool:
        chk_restrict = self.item_dict['contentDetails'].get('contentRating').get('ytRating', 'N/A')
        if chk_restrict == 'ytAgeRestricted':
            return True
        return False    

    #items[0]status
    def get_reject_reason(self) -> str:
        return self.item_dict['status'].get('rejectionReason')
    
    def is_embeddable(self) -> bool:
        return self.item_dict['status'].get('embeddable')
        #do i need to transform this? tests will probably tell me this
    
    def is_publicstatsviewable(self) -> bool:
        return self.item_dict['status'].get('publicStatsViewable')
     # do i even need this? views and likes are always accessible even if this is false

    #items[0]statistics
    def get_views(self) -> int:
        return self.item_dict['statistics'].get('viewCount')
    
    def get_likes(self) -> int:
        return self.item_dict['statistics'].get('likeCount')
    
    def get_commentcount(self) -> int:
        return self.item_dict['statistics'].get('commentCount')
     #low prio, can't think of how it's useful atm

    #items[0]player
    def get_embedframe(self) -> str:
        self.item_dict['player'].get('embedHtml')
    # they're talking about me needing to set the aspect ratio in my request in the docs, not sure if i should
    
    def get_embed_height(self) -> int:
        self.item_dict['player'].get('embedHeight')
     # only exists if specified in request
    
    def get_embed_width(self) -> int:
        self.item_dict['player'].get('embedWidth')
     # only exists if specified in request

    #items[0]suggestions
    
    def get_suggested_tags(self) -> list:
        self.item_dict['suggestions'].get('tagSuggestions')
    

    #items[0]liveStreamingDetails
    def is_livestream(self) -> bool:
        if not self.item_dict.get('liveStreamingDetails'):
            #eventually raise custom exception
            return False
        return True
    
    def get_scheduled_start(self, tz='UTC') -> datetime:
        '''tz variable takes a pytz supported timezone string.
        Defaults to UTC if not specified.'''
        yt_time = self.item_dict['liveStreamingDetails'].get('scheduledStartTime', None)
        dt = datetime.strptime(yt_time, "%Y-%m-%dT%H:%M:%SZ")
        _tz = pytz.timezone(tz)
        localized_dt = _tz.localize(dt)
        return localized_dt
    
    def get_scheduled_end(self, tz='UTC') -> datetime:
        '''tz variable takes a pytz supported timezone string.
        Defaults to UTC if not specified.'''
        yt_time = self.item_dict['liveStreamingDetails'].get('scheduledEndTime', None)
        dt = datetime.strptime(yt_time, "%Y-%m-%dT%H:%M:%SZ")
        _tz = pytz.timezone(tz)
        localized_dt = _tz.localize(dt)
        return localized_dt
    
    def get_actual_start(self, tz='UTC') -> datetime:
        '''tz variable takes a pytz supported timezone string.
        Defaults to UTC if not specified.'''
        yt_time = self.item_dict['liveStreamingDetails'].get('actualStartTime', None)
        dt = datetime.strptime(yt_time, "%Y-%m-%dT%H:%M:%SZ")
        _tz = pytz.timezone(tz)
        localized_dt = _tz.localize(dt)
        return localized_dt
    
    def get_actual_end(self, tz='UTC') -> datetime:
        '''tz variable takes a pytz supported timezone string.
        Defaults to UTC if not specified.'''
        yt_time = self.item_dict['liveStreamingDetails'].get('actualEndTime', None)
        dt = datetime.strptime(yt_time, "%Y-%m-%dT%H:%M:%SZ")
        _tz = pytz.timezone(tz)
        localized_dt = _tz.localize(dt)
        return localized_dt
    
    def get_ccv(self) -> int:
        return self.item_dict['liveStreamingDetails'].get('concurrentViewers')
    