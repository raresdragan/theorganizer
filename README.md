# The Organizer
## A python movie collection organiser
## by Rares Dragan (@raresdragan, www.raresdragan.com)

## WHEN TO USE THIS
- If you have an archive of movies and the folder names are quite messy
- If you are using **Kodi** or **Plex** or **AppleTV** and it keeps wrongly identifying some of your movies
- If you have OCD like I do

## WHAT IT DOES
- this script takes a base folder e.g. /media/multimedia/movies/
- goes through this main folder searching for movie folders
- detects the movie name by folder name
- connects to IMDB and grabs some movie info
- creates the IMDB XML into the existing nfo file or in a new nfo file
- clean renames the movie folder like this: YYYY - The Movie Name - 1080p

## TODO
- will detect the movie in a personal IMDB collection (e.g. THE CLASSICS)
- will assign a nfo XML tag based on the detected IMDB collection

## VERSION HISTORY

### v.0.0.5 @ 2021-03-02
- added gitignore rules similar to ones suggested here: https://gist.github.com/octocat/9257657
- thought about adding this to my empty 100 years old git account

### v.0.0.4 @ 2021-03-01
- added grabbing iMDB info from rapidapi
- using https://rapidapi.com/hmerritt/api/imdb-internet-movie-database-unofficial
- added grabbing iMDB info from imdbpie (alternative to rapidapi)
- movie search in dual sources: if movie can't be found via imdbpie try rapidapi
- some code cleanup

### v.0.0.3 @ 2021-02-27
- got into some depressive moment
- thought I should fix it by coding and remembered my python experiment
- started from scratch
- added XML tagging based on https://kodi.wiki/view/NFO_files/Movies

### v.0.0.2 @ 2020-06-21
- managed to put some code together
- grabbing some watchlist content from https://www.imdb.com/list/...

### v.0.0.1 @ 2020-06-20
- just thought about learning some python coding
- did nothing yet
