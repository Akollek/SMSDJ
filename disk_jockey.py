from django.db.models import Q
from django.utils import timezone
from dj.models import *
from threading import Thread
import time, logging, os, sys, atexit
import pexpect, pafy
import api_keys

requested   = Q(status='RE')
downloading = Q(status='DL')
downloaded  = Q(status='DD')
playing     = Q(status='PL')

LOGFILE = '/home/pi/Music/rpidj/logs/dj.log'
FORMAT  = '[%(asctime)s %(levelname)s] %(message)s'
log = logging.getLogger('disk_jockey')
handler = logging.FileHandler(LOGFILE)
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

class Downloader(object):

    def __init__(self, request):
        if not os.path.exists('/tmp/songs/'):
            os.mkdir('/tmp/songs/')
        self.request = request
        self.request.status = 'DL'
        self.request.save()

    def download(self):
        download_thread = Thread(target=self.download_daemon,args=())
        download_thread.daemon = True
        download_thread.start() 

    def download_daemon(self):
        url = 'http://www.youtube.com/watch?v={}'.format(self.request.youtube_id)
        p = pafy.new(url)
        filename = "/tmp/songs/{}.m4a".format(self.request.youtube_id)
        self.request.song = p.getbestaudio().download(filepath=filename)
        self.request.status = 'DD'
        self.request.save() 


class Player(object):

    def __init__(self,request):
        self.request = request
        self.playing = False
    
    def play(self):
        self.playing = True
        self.request.status = 'PL'
        self.request.played = timezone.now()
        self.request.save()
        player_thread = Thread(target=self.player_daemon,args=())
        player_thread.daemon = True
        player_thread.start()

    def player_daemon(self):
        global log
        filename = self.request.song
        command = "omxplayer {}".format(filename) 
        self.child = pexpect.spawn(command)
        self.child.expect(pexpect.EOF,timeout=None)
        log.info('Done playing: {}'.format(self.request.title))
        self.request.status = 'PD'
        self.request.save()
        os.system("rm {}".format(filename))
        self.playing = False 
      

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
                log.info("Playing song: {}".format(top_song.title))
            if top_request and top_request.count()<=10: # don't download more than 10 songs in advance
                top_request = top_request[0]
                dldr = Downloader(top_request)
                dldr.download()
                log.info("Downloading song: {}".format(top_request.title))
        
        time.sleep(1)

def cleanup():
    # clean up any playing songs caused by a potential crash:
    for r in Request.objects.filter(playing):
        os.system("rm {}".format(r.song))
        r.status = 'CN' #mark as played
        r.save() 
    
    # turn off existing songs:
    os.system("ps aux | awk '/omxplayer/ {print $2;}' | xargs kill")    

if __name__ == "__main__":
    atexit.register(cleanup)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--clear-queue':
            log.info("Clearing queue")
            for r in Request.objects.filter(requested | downloaded | downloading):
                if r.song:
                    os.system("rm {}".format(r.song))
                r.status = 'CN'
                r.save()

    # clean up any playing songs caused by a potential crash:
    for r in Request.objects.filter(playing):
        r.status = 'CN' #mark as played
        r.save() 

    # turn off existing songs:
    os.system("ps aux | awk '/omxplayer/ {print $2;}' | xargs kill")    

    main()
