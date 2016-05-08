from django.db import models

class Request(models.Model):
    MAX_DL_ATTEMPTS = 5
    STATUS_CHOICES = (
        ( 'RE', 'REQUESTED'),
        ( 'DL', 'DOWNLOADING'),
        ( 'DD', 'DOWNLOADED'),
        ( 'PL', 'PLAYING'),
        ( 'PD', 'PLAYED'),
        ( 'CN', 'CANCELLED'),
        ( 'FD', 'FAILED'),
    )    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    request_text = models.CharField(max_length=512)
    # store 5 ids in an space separated string
    # in case one fails (i.e. has ads)
    # NOTE: If MAX_DL_ATTEMPTS increases, change max length
    # each youtube id is 11 chars, at least 11*attempts
    youtube_ids = models.CharField(max_length=128) 
    dl_attempts = models.IntegerField(default=0)
    title = models.CharField(max_length=256) 
    requested_by = models.CharField(max_length=16,null=True)
    requested = models.DateTimeField(auto_now_add=True)
    played = models.DateTimeField(null=True)
    song = models.CharField(max_length=128,null=True)

    def __unicode__(self):
        if len(self.title)<15:
            return self.title
        else:
            return self.title[:12]+"..."

