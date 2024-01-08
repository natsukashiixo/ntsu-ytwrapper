import os

import googleapiclient.discovery

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
    

class PlaylistItemsDotListSingle:
    def __init__(self, api_key: str, playlist_id: str, bucket: YoutubeTokenBucket):
        # these should basically never change between classes
        self.api_key = api_key
        self.bucket = bucket
        # these ones change so be careful with copy paste
        self.TOKENCOST = 1
        self.playlist_id = playlist_id

        def _get_response(): # contents of this function should change between classes but name can be the same
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
            yt_response = request.execute()
            return yt_response

        if youtube_status() and self.bucket.take(self.TOKENCOST):
            self.yt_response = _get_response()