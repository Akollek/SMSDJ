from music_utilities.download import Downloader
from music_utilities.youtube_search import youtube_search
from dj.models import *
from django.db.models import Q
import time

def main():
    q = Q(status='RE')
    while True:
        # get oldest request
        top_request = Request.objects.filter(q).order_by('-requested')
        if top_request:
            top_request = top_request[0]
            url, title = youtube_search(top_request.request_text)
            dldr = Downloader(title,url,top_request)
            dldr.download()
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()

