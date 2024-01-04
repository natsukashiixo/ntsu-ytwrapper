import requests

def youtube_status():
    try:
        response = requests.get("https://www.youtube.com")
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        return False