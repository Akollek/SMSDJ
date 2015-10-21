Raspberry Pi DJ
===============

[Example response](https://goo.gl/photos/pT7DaTcStSyZdNmr7)

Django site, queues song requests by SMS and provides an interface for managing the song queue.

### TODO ###

- Text a user back and inform them how many songs are in from on them in the queue, or if the song they requested is already in the queue
- Display the queue on the site
- Edit the queue on the site (eventually from a login section so only the house owner can edit the queue)
- Option to limit number of requests per number per night or time unit
- Option to block numbers from making requests
- Option to make requests from the site

#### BUGS ####
- if a song is requested to be played again, it cannot be downloaded since the file exists, but the player still tries to play it and hangs 
