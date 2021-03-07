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
- if no video file exists in the folder it just prefixes the folder with !!!  


## VERSION HISTORY


### v.0.0.8 @ 2021-03-07
- do nothing, just a simple rename if no video file detected
- also grab resolution from original folder name

### v.0.0.7 @ 2021-03-06
- get_imdb_list_movies will now get movies fron export csv instead of scraping
- all movies in the list are parsed this way
- new feature: when renaming folders keep in mind duplicate movies exists
- renamed folders might add a timestamp to mark duplicates
- new feature: grab (and compare) imdb movie id from both folder and file name
- folder rename: added english title in () after original title

### v.0.0.6 @ 2021-03-06
- converted the script code from python 2.7 to python 3.7
- significant improvements
- detects the movie in a personal IMDB collection (e.g. THE CLASSICS)
- assigns a nfo XML tag based on the detected IMDB collection
- added new code to grab imdb lists and movies in imdb lists for a imdb_user_id
- added get_movie_tags(imdb_movie_id) = generating tags xml for a movie_id
- known issues: get_imdb_list_movies will not get movies from multiple pages

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
