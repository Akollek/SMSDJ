from django.db import models

class Request(models.Model):
    STATUS_CHOICES = (
        ( 'RE', 'REQUESTED'),
        ( 'DL', 'DOWNLOADING'),
        ( 'DD', 'DOWNLOADED'),
        ( 'PL', 'PLAYING'),
        ( 'PD', 'PLAYED'),
        ( 'CN', 'CANCELLED')
    )    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    request_text = models.CharField(max_length=300)
    youtube_id = models.CharField(max_length=20) 
    title = models.CharField(max_length=200) 
    requested_by = models.CharField(max_length=10,null=True)
    requested = models.DateTimeField(auto_now_add=True)
    played = models.DateTimeField(null=True)
    song = models.CharField(max_length=100,null=True)

    def __unicode__(self):
        if len(self.title)<15:
            return self.title
        else:
            return self.title[:12]+"..."

