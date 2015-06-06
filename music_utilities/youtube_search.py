from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from music_utilities import api_keys

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
#   https://cloud.google.com/console
DEVELOPER_KEY = api_keys.dev_key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)
    
    search = youtube.search().list(
      q=query,
      part='id,snippet',
      type='video',
      maxResults=1
    ).execute()
    
    url = 'http://www.youtube.com/watch?v={}'.format(search['items'][0]['id']['videoId'])
    title = search['items'][0]['snippet']['title']
    return (url, title)   



