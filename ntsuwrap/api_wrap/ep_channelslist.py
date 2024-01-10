import os
from datetime import datetime
from typing import Any
import googleapiclient.discovery
import pytz
from ntsuwrap import YoutubeTokenBucket
from youtube_status import youtube_status

class ChannelsDotList:
    def __init__(self, api_key: str, channel_id: str, bucket: YoutubeTokenBucket):
        # these should basically never change between classes
        self.api_key = api_key
        self.bucket = bucket
        # these ones change so be careful with copy paste
        self.TOKENCOST = 1
        self.channel_id = channel_id

        def _get_response() -> list: # contents of this function should change between classes but name can be the same
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
            api_service_name = "youtube"
            api_version = "v3"
            DEVELOPER_KEY = self.api_key
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey = DEVELOPER_KEY)

            request = youtube.channels().list(
                part="snippet,statistics,contentDetails,topicDetails,status,brandingSettings,localizations", # these are all the public parts
                id=self.channel_id,
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


class ParseChannels:
    def __init__(self, item_dict) -> None:
        self.item_dict = item_dict
    #items[0]snippet
    def get_name(response) -> str:
        pass
    def get_desc(response) -> str:
        pass
    def get_url(response) -> str:
        pass
    def get_createtime(response) -> datetime:
        pass #needs str to timestamp conversion
    def get_pfp(response) -> str:
        pass #use constructors to decide which one to get?
        #like object.get_pfp(response).high ?
    
    #items[0]statistics
    def get_subscribers(response) -> str or int:
        if response['items'][0]['statistics'].get('hiddenSubscriberCount') == True:     #unsure about this but I think a raw "if" just checks if the element exists or not
            return "HiddenFromView"
        else:
            subcount = int(response['items'][0]['statistics'].get('subscriberCount', 'N/A'))
        return subcount
    def get_vidcount(response) -> int:
        pass

    #items[0]status
    def get_privacystatus(response) -> str:
        pass
