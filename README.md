# The Organizer
## A python movie collection organiser
## by Rares Dragan (@raresdragan, www.raresdragan.com)


## HOW TO USE This

$ python3 theorganizer.py --help                                         
usage: theorganizer.py [-h] [--cleanup] [--duplicates] [--process] [--noalert]
                       [--notags] [--onlytags] [--verbose] [--folder FOLDER]
                       [--move MOVE]

optional arguments:
  -h, --help            show this help message and exit
  --cleanup, -c         Perform a folder cleanup, removing all special folder
                        markings ($ # @ !)
  --duplicates, -d      Mark all duplicate movies with 'DUPLICATE'
  --process, -p         Do imdb folders processing.
  --noalert, -n         Don't do any folder alerts renaming (no !@#$ in the
                        folder names).
  --notags, -t          Don't do the initial tags checking
  --onlytags, -o        Only process tags updates. Nothing else.
  --verbose, -v         Verbose mode. Display debug messages
  --folder FOLDER, -f FOLDER
                        Define main movies folder (containing movies in sub-
                        folders)
  --move MOVE, -m MOVE  Define destination movies folder. Move all folders
                        from Main folder to destination while taking care of
                        duplicates renaming



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
- if imdb_id in found in nfo <> imdb_id grabbed online just prefixes the folder with !!!  

## VERSION HISTORY


### v.0.1.0 @ 2021-03-15
- midnight version
- --duplicates really works for basefolder now (--folder) and is marking duplicates with DUPLICATE
- ca't remember what else is new but a lot is new

### v.0.0.9 @ 2021-03-14
- major updates
- command line arguments for cleanup noprocessing and folder name
- fixed renaming issues on exfat (case insensitive ccrashed the rename)
- on copy / move marking duplicates with DUPLICATE
- -- cleanup performs folder cleanup (removes pre markings (!@#$)

### v.0.0.8 @ 2021-03-07
- do nothing, just a simple rename if no video file detected
- also grab resolution from original folder name
- compare imdb_id in nfo with imdb_id grabbed online and alert !!! if different
- implemeted new API from https://developers.themoviedb.org/3
- getting the english name is now much much better

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
