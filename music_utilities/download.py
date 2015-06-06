import django
import pafy
from threading import Thread
from dj.models import *

class Downloader(object):

    def __init__(self, title, youtube_url, request):
        self.title = title
        self.youtube_url = youtube_url
        self.request = request

    def download(self):
        download_thread = Thread(target=self.download_daemon,args=())
        download_thread.daemon = True
        download_thread.start() 

    def download_daemon(self):
        p = pafy.new(self.youtube_url)
        self.filename = p.getbestaudio().download()
        song = Song.objects.create(title=self.title,filename=self.filename)
        self.request.song = song
        self.request.status = 'DL'
 
