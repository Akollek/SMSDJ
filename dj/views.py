from django.shortcuts import render


def song_list(request):
    return render(request, 'dj/song_list.html')
