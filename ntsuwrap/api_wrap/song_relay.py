import os

import googleapiclient.discovery

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