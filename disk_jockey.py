from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from django.db.models import Q
from dj.models import *
from threading import Thread
import time, logging, os
import pexpect, pafy
import api_keys

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
#   https://cloud.google.com/console
DEVELOPER_KEY = api_keys.dev_key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


requested  = Q(status='RE')
downloaded = Q(status='DD')
playing    = Q(status='PL')

LOGFILE = '/home/pi/Music/rpidj/logs/dj.log'
FORMAT  = '[%(asctime)s %(levelname)s] %(message)s'
log = logging.getLogger('disk_jockey')
handler = logging.FileHandler(LOGFILE)
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

class Downloader(object):

    def __init__(self, title, youtube_id, request):
        self.title = title
        self.youtube_id = youtube_id
        self.request = request
        self.request.status = 'DL'
        self.request.save()

    def download(self):
        download_thread = Thread(target=self.download_daemon,args=())
        download_thread.daemon = True
        download_thread.start() 

    def download_daemon(self):
        url = 'http://www.youtube.com/watch?v={}'.format(self.youtube_id)
        p = pafy.new(url)
        filename = "/home/pi/Music/rpidj/songs/{}.m4a".format(self.youtube_id)
        self.filename = p.getbestaudio().download(filepath=filename)
        song = Song.objects.create(title=self.title,filename=self.filename)
        self.request.song = song
        self.request.status = 'DD'
        self.request.save() 


class Player(object):

    def __init__(self,request):
        self.request = request
        self.playing = False
    
    def play(self):
        self.playing = True
        self.request.status = 'PL'
        self.request.save()
        player_thread = Thread(target=self.player_daemon,args=())
        player_thread.daemon = True
        player_thread.start()

    def player_daemon(self):
        global log
        filename = self.request.song.filename
        command = "omxplayer {}".format(filename) 
        self.child = pexpect.spawn(command)
        self.child.expect(pexpect.EOF,timeout=None)
        log.info('Done playing: {}'.format(self.request.song.title))
        self.request.status = 'PD'
        self.request.save()
        os.system("rm {}".format(filename))
        self.playing = False 
      

def youtube_search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)
    
    search = youtube.search().list(
      q=query,
      part='id,snippet',
      type='video',
      maxResults=1
    ).execute()
    
    youtube_id = search['items'][0]['id']['videoId']
    title = search['items'][0]['snippet']['title']
    return (youtube_id, title)   




def main():
    global log
    while True:
        top_song = Request.objects.filter(downloaded).order_by('requested')
        top_request = Request.objects.filter(requested).order_by('requested')
        if top_song or top_request: 
            if top_song and not Request.objects.filter(playing):
                top_song = top_song[0]
                player = Player(top_song)
                player.play()
                log.info("Playing song: {}".format(top_song.song.title))
            if top_request:
                top_request = top_request[0]
                youtube_id, title = youtube_search(top_request.request_text)
                dldr = Downloader(title,youtube_id,top_request)
                dldr.download()
                log.info("Downloading song: {}".format(title))
        
        time.sleep(1)


if __name__ == "__main__":
    # clean up any playing songs caused by a potential crash:
    for r in Request.objects.filter(playing):
        r.status = 'PD' #mark as played
        r.save() 
    main()
