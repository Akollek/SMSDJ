from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from dj.models import *



def index(request):
    return render(request, 'dj/index.html')

def song_list(request):
    pass

@csrf_exempt
def request_song(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('')
    
    Request.objects.create(
        status = 'RE',
        request_text = request.POST['Body'],
        requested_by = request.POST['From']
        )

    return HttpResponse('')
