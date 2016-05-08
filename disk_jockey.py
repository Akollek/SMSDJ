from __future__ import unicode_literals
from django.db.models import Q
from django.utils import timezone
from dj.models import *
from threading import Thread
from firebase import firebase
import time, logging, os, sys, atexit
import pexpect, youtube_dl
import api_keys
# import itunes


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

FRONTEND = False

if FRONTEND:
    playing_fb = firebase.FirebaseApplication(api_keys.firebase_url, None)

class Downloader(object):

    options = {
        'format': 'bestaudio/best',
        'extractaudio' : True, 
        'outtmpl': '/tmp/songs/%(id)s',
    }

    def __init__(self, request):
        if not os.path.exists('/tmp/songs/'):
            os.mkdir('/tmp/songs/')
        self.request = request
        self.request.status = 'DL'
        self.request.save()

    def download(self):
        # if we've tried more than the max, or more than the IDs we have, fail
        if (self.request.dl_attempts >= min(Request.MAX_DL_ATTEMPTS,len(self.request.youtube_ids.split(' ')))):
            log.info("Failed to download {} after {} attempts".format(self.request.request_text,self.request.dl_attempts))
            self.request.status = 'FD' # failed
            self.request.save()
            return

        download_thread = Thread(target=self.download_daemon,args=())
        download_thread.daemon = True
        download_thread.start() 

    def download_daemon(self):
        youtube_id = self.request.youtube_ids.split(' ')[self.request.dl_attempts]
        log.info("Downloading song: {} ({})".format(self.request.title,youtube_id))
        url = 'http://www.youtube.com/watch?v={}'.format(youtube_id)
        with youtube_dl.YoutubeDL(self.options) as ydl:
            errs = ydl.download([url])
        if errs == 0:
            self.request.song = '/tmp/songs/{}'.format(youtube_id)
            self.request.dl_attempts += 1
            self.request.status = 'DD'
        else:
            self.request.status = 'FD' #failed
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
        if FRONTEND:
            firebase_id = playing_fb.post('playing/', self.request.title)['name']
        filename = self.request.song
        # display artwork:
        #try:
            # wake up screen
            #os.system('sudo chmod 666 /dev/tty1')
            #os.system('echo  "\033[9;0]" >/dev/tty1')
            #artwork = itunes.search_album(self.request.title)[0].get_artwork()['100']
            #os.system('wget {}'.format(artwork))
            #art = pexpect.spawn('fim {}'.format(artwork.split('/')[-1]))
            ## zoom out
            #for _ in xrange(5):
            #    art.sendline('-')
            #art.sendline('q')
            #os.system('rm {}'.format(artwork.split('/')[-1]))
        #except (KeyError, IndexError):
        #    pass
        try:
            with open('/dev/tty1','w') as f:
                f.write('Playing {} requested by {}\n'.format(
                    self.request.title, 
                    self.request.requested_by
            ))
        except:
            pass
        command = "omxplayer {}".format(filename) 
        self.child = pexpect.spawn(command)
        try:
            self.child.expect('Audio codec') # this is printed if file successfully starts to play
        except pexpect.EOF:
            try:
                with open('/dev/tty1','w') as f:
                    f.write("Failed to play, queueing for redownload\n")
            except:
                pass
            log.info('Failed to play: {}, redownloading'.format(self.request.title))
            self.request.status = 'RE' # reset to requested
            self.request.save()
            if FRONTEND:
                playing_fb.delete('playing/',firebase_id)
      #      os.system("rm {}".format(filename))
            self.playing = False
            return
        self.child.expect(pexpect.EOF,timeout=None)
        log.info('Done playing: {}'.format(self.request.title))
        if FRONTEND:
            playing_fb.delete('playing/',firebase_id)
        self.request.status = 'PD'
        self.request.save()
       # os.system("rm {}".format(filename))
        self.playing = False
      

def main():
    global log
    log.info("DJ started")
    while True:
        top_song = Request.objects.filter(downloaded).order_by('requested')
        top_request = Request.objects.filter(requested).order_by('requested')
        if top_song or top_request: 
            if top_song and not Request.objects.filter(playing):
                top_song = top_song[0]
                player = Player(top_song)
                player.play()
                log.info("Playing song: {}".format(top_song.title))

                # update the firebase queue
                time.sleep(0.1) # make sure the song actually started playing
                requests = list(Request.objects.filter(status__in=['RE','DL','DD']).order_by("requested"))

                if FRONTEND:
                   queue = map(lambda x: x.title, requests)
                   fb = firebase.FirebaseApplication(api_keys.firebase_url,None)
                   q = fb.get('queue/',None)
                   if q:
                       for k in q.keys():
                           fb.delete('queue/', k)
                   fb.post('queue/',queue)

             # don't download more than 10 songs in advance and don't download more than two at a time
            if top_request and top_request.count()<=10 and Request.objects.filter(status='DL').count()<=2:
                top_request = top_request[0]
                dldr = Downloader(top_request)
                dldr.download()
        
        time.sleep(1)

def cleanup():
    # clean up any playing songs caused by a potential crash:
    for r in Request.objects.filter(playing):
        #os.system("rm {}".format(r.song))
        r.status = 'CN' #mark as played
        r.save() 
    
    # turn off existing songs:
    os.system("ps aux | awk '/omxplayer/ {print $2;}' | xargs kill")    
    if FRONTEND:
       for k in playing_fb.get('playing/',None).keys():
           playing_fb.delete('playing',k)

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
