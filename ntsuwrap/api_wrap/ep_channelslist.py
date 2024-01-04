import os

import googleapiclient.discovery

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