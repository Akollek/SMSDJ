from django.db import models

class Request(models.Model):
    STATUS_CHOICES = (
        ( 'RE', 'REQUESTED'),
        ( 'DL', 'DOWNLOADED'),
        ( 'PL', 'PLAYING'),
        ( 'PD', 'PLAYED')
    )    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    request_text = models.CharField(max_length=300)
    requested_by = models.CharField(max_length=10)
    requested = models.DateTimeField(auto_now_add=True)
    played = models.DateTimeField(null=True)
    song = models.ForeignKey('Song', null=True)

class Song(models.Model):
    title = models.CharField(max_length=200)
    filepath = models.CharField(max_length=100)
