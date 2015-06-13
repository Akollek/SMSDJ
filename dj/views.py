from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import TwilioRestClient 
from dj.models import *
import api_keys
import ssl
import time

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
#   https://cloud.google.com/console
DEVELOPER_KEY = api_keys.dev_key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

twilio_client = TwilioRestClient(api_keys.ACCOUNT_SID, api_keys.AUTH_TOKEN)


def youtube_search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)
    try:
        search = youtube.search().list(
          q=query,
          part='id,snippet',
          type='video',
          maxResults=1
        ).execute()
    except ssl.SSLError:
        # Sometimes this throws an SSL error.
        # It seems to happen when there are
        # a lot of requests in a small time
        # periods, so hacky solution:
        time.sleep (0.5)
        return youtube_search(query)  
 
    try:
        youtube_id = search['items'][0]['id']['videoId']
        title = search['items'][0]['snippet']['title']
    except IndexError:
        # means no results
        return False, False
    return (youtube_id, title)   


def index(request):
    return render(request, 'dj/index.html')

def song_list(request):
    pass

@csrf_exempt
def request_song(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('')

    body = request.POST['Body']
    youtube_id, title = youtube_search(body)    
    requested_by = request.POST['From']

    if youtube_id and title:
        same_request = Request.objects.filter(status__in=['RE','DL','DD'], youtube_id = youtube_id)
        if not same_request:
            req = Request.objects.create(
                status = 'RE',
                youtube_id = youtube_id,
                title = title,
                requested_by = requested_by,
                request_text = body
                )
       
            index = Request.objects.filter(status__in=['RE','DL','DD']).count() - 1 
            message = "{title} has been added to the queue. There {be} {index} song{s} in front of it.".format(
                title=title,
                index=index,
                be = ['is','are'][index>1 or index == 0],
                s  = ['','s'][index>1 or index == 0])

        else:  
            req = same_request[0]
            index = list(Request.objects.filter(status__in=['RE','DL','DD']).order_by("requested")).index(req)
            message = "{title} is already in the queue. There {be} {index} song{s} in front of it.".format(
                title=title,
                index=index,
                be = ['is','are'][index>1 or index == 0],
                s  = ['','s'][index>1 or index == 0])
       
    else:
        message = "No matches found for \"{body}\"".format(body=body)
        
    twilio_client.messages.create(
        to=requested_by, 
        from_="+14387949893", 
        body=message,  
    ) 

    return HttpResponse('')
