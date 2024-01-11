import os
from datetime import datetime
import googleapiclient.discovery
import pytz
from ntsuwrap import YoutubeTokenBucket
from youtube_status import youtube_status

def relay_from_playlist(playlist_id: str, API_KEY: str) -> list | None:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=50
    )
    raw_response = request.execute()
    
    #print(raw_response)

    if not raw_response.get('nextPageToken'):
        videoID_list = []
        for item in raw_response['items']:
            #from pprint import pprint
            #pprint(item, indent=4)
            vid_id = item['contentDetails']['videoId']
            videoID_list.append(vid_id)
        return videoID_list
    else:
        print('Relay is currently out of scope of the project. Exiting')
        return      # No time to implement today, relay starts tomorrow
    

class PlaylistItemsDotList:
    def __init__(self, api_key: str, playlist_id: str, bucket: YoutubeTokenBucket):
        # these should basically never change between classes
        self.api_key = api_key
        self.bucket = bucket
        # these ones change so be careful with copy paste
        self.TOKENCOST = 1
        self.playlist_id = playlist_id

        def _get_response() -> list:
            full_list = []
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

            api_service_name = "youtube"
            api_version = "v3"
            DEVELOPER_KEY = api_key

            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey = DEVELOPER_KEY)

            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id, #unsure if this one supports csv
                maxResults=50
            )
            while request: #got this from stackoverflow so who knows
                yt_response = request.execute()
                page_data = yt_response['items']
                full_list.extend(page_data)
                request = youtube.search().list_next(
      request, yt_response)
            
            return full_list

        if youtube_status() and self.bucket.take(self.TOKENCOST):
            self.yt_response = _get_response()

    def first_item(self) -> dict:
        return self.yt_response[0] if self.yt_response else {}

    def item_by_index(self, x: int) -> dict:
        return self.yt_response[x] if self.yt_response else {}

    def item_by_snippet_kwp(self, keyword: str, value) -> dict:
        for i, item in enumerate(self.yt_response):
            if item.get('snippet', {}).get(keyword) == value:
                return item
        print(f'key value pair {keyword}: {value} not found')
        return {}

    def all_items(self) -> list:
        return self.yt_response

class ParsePlaylistItem:
    def __init__(self, item_dict) -> None:
        self.item_dict = item_dict
    
    #item[i]snippet
    def get_vid_playlist_addtime(self, tz='UTC') -> datetime:
        '''tz variable takes a pytz supported timezone string.
        Defaults to UTC if not specified.'''
        yt_time = self.item_dict['snippet'].get('publishedAt', None)
        dt = datetime.strptime(yt_time, "%Y-%m-%dT%H:%M:%SZ")
        _tz = pytz.timezone(tz)
        localized_dt = _tz.localize(dt)
        return localized_dt
    
    def get_vid_playlist_adduser(self) -> str:
        return self.item_dict['snippet'].get('channelID')
         # gets which user added the video to the playlist, returns a channelID, not sure if i need this?
    
    def get_vid_title(self) -> str:
        return self.item_dict['snippet'].get('title')
        
    def get_vid_desc(self) -> str:
        return self.item_dict['snippet'].get('description')
        
    def get_vid_thumbnails(self) -> str:
        return self.item_dict['snippet'].get('thumbnails')
         #decorator magic once again
    
    def get_playlist_owner(self) -> str:
        return self.item_dict['snippet'].get('channelTitle')
        
    def get_vid_owner_title(self) -> str:
        return self.item_dict['snippet'].get('videoOwnerChannelTitle')
        
    def get_vid_owner_id(self) -> str:
        return self.item_dict['snippet'].get('videoOwnerChannelId')
        
    def get_vid_index(self) -> int:
        return self.item_dict['snippet'].get('position')
         #placement in playlist, starts at index 0
    
    def get_vid_id(self) -> str:
        return self.item_dict['snippet'].get('resourceId').get('videoID')
        #snippet.resourceId.videoID
         #docs here are confusing, seem to imply that you can add non-videos to a playlist which feels illegal (livestreams should still be considered videos on youtubes end)

    #item[x]contentDetails
    def get_vid_id_bckp(self) -> str:
        return self.item_dict['contentDetails'].get('videoID')
         #this is the one i've used before with playlists that contain livestreams, in case previous function doesn't work
    def get_vid_publishtime(self, tz='UTC') -> datetime:
        '''tz variable takes a pytz supported timezone string.
        Defaults to UTC if not specified.'''
        yt_time = self.item_dict['contentDetails'].get('videoPublishedAt', None)
        dt = datetime.strptime(yt_time, "%Y-%m-%dT%H:%M:%SZ")
        _tz = pytz.timezone(tz)
        localized_dt = _tz.localize(dt)
        return localized_dt
    
