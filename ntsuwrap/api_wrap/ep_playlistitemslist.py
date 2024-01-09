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

        def _get_response() -> list: # first function where checking for nextpagetoken is mandatory
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

    #each item in a playlist is its own dict in a list stored in 'items', should i just return lists with no keyword pairing and pray?
    
    #item[i]snippet
    def get_vid_playlist_addtime(response) -> datetime:
        pass # convert str -> datetime
    def get_vid_playlist_adduser(response) -> str:
        pass # gets which user added the video to the playlist, returns a channelID, not sure if i need this?
    def get_vid_title(response) -> str:
        pass
    def get_vid_desc(response) -> str:
        pass
    def get_vid_thumbnails(response) -> str:
        pass #decorator magic once again
    def get_playlist_owner(response) -> str:
        pass
    def get_vid_owner_title(response) -> str:
        pass
    def get_vid_owner_id(response) -> str:
        pass
    def get_vid_index(response) -> int:
        pass #placement in playlist, starts at index 0
    def get_vid_id(response) -> str:
        #snippet.resourceId.videoID
        pass #docs here are confusing, seem to imply that you can add non-videos to a playlist which feels illegal (livestreams should still be considered videos on youtubes end)

    #item[x]contentDetails
    def get_vid_id_bckp(response) -> str:
        pass #this is the one i've used before with playlists that contain livestreams, in case previous function doesn't work
    def get_vid_publishtime(response) -> datetime:
        pass # str -> datetime conversion pls
    
