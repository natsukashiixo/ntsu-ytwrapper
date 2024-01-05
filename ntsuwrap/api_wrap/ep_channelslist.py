import os
import googleapiclient.discovery
from ntsuwrap import YoutubeTokenBucket
from youtube_status import youtube_status

def get_subscribers(channel_id: str, API_KEY: str) -> int or str:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    raw_response = request.execute()

    if raw_response['items'][0]['statistics']['hiddenSubscriberCount'] == True:     #unsure about this but I think a raw "if" just checks if the element exists or not
        return "HiddenFromView"
    else:
        subcount = int(raw_response['items'][0]['statistics']['subscriberCount'])
        return subcount
    
def getall_channels_dot_list(channel_id: str, API_KEY: str, *args) -> tuple:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.channels().list(
        part="snippet,statistics,contentDetails,topicDetails,status,brandingSettings,localizations", # these are all the public parts
        id=channel_id, #p sure this takes a csv string of max 50 elements
        # but most likely I won't put in logic for handling multiple channels in this function.
        maxResults=50
    )
    raw_response = request.execute()

class ChannelsDotListSingle:
    def __init__(self, api_key: str, channel_id: str, bucket: YoutubeTokenBucket):
        # these should basically never change between classes
        self.api_key = api_key
        self.bucket = bucket
        # these ones change so be careful with copy paste
        self.TOKENCOST = 1
        self.channel_id = channel_id

        def _get_response(): # contents of this function should change between classes but name can be the same
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
            api_service_name = "youtube"
            api_version = "v3"
            DEVELOPER_KEY = self.api_key
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey = DEVELOPER_KEY)

            request = youtube.channels().list(
                part="snippet,statistics,contentDetails,topicDetails,status,brandingSettings,localizations", # these are all the public parts
                id=self.channel_id, #p sure this takes a csv string of max 50 elements
                # but most likely I won't put in logic for handling multiple channels in this function.
                maxResults=50
            )
            yt_response = request.execute()
            return yt_response

        if youtube_status() and self.bucket.take(self.TOKENCOST):
            self.yt_response = _get_response()

    def get_subscribers(response) -> str or int:
        if response['items'][0]['statistics'].get('hiddenSubscriberCount') == True:     #unsure about this but I think a raw "if" just checks if the element exists or not
            return "HiddenFromView"
        else:
            subcount = int(response['items'][0]['statistics'].get('subscriberCount', 'N/A'))
        return subcount
