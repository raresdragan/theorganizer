## The Organizer
## A python (3.7) movie collection organiser
## by Rares Dragan (www.raresdragan.com) (https://github.com/raresdragan)

import os
import re
import sys
import traceback
import requests
import json
import urllib.request
import imdbpie
import time
import glob
import logging
import config as cfg


# Include parse arguments modules
import argparse

# setup imdb connection via imdbpie

from imdbpie import ImdbFacade
imdb = ImdbFacade()
from six.moves.urllib.request import urlopen
from csv import reader
from datetime import datetime
imdb_list_array = []

from tmdbv3api import TMDb
from tmdbv3api import Movie



# Kodi file formats: AVI, MPEG, WMV, ASF, FLV, MKV/MKA (Matroska), QuickTime, MP4, M4A, AAC, NUT, Ogg, OGM, RealMedia RAM/RM/RV/RA/RMVB, 3gp, VIVO, PVA, NUV, NSV, NSA, FLI, FLC, DVR-MS, WTV, TRP and F4V
video_extensions        = [
                            '.avi'
                            ,'.mpeg'
                            ,'.mpg'
                            ,'.wmv'
                            ,'.mov'
                            ,'.mp4'
                            ,'.mkv'
                            ,'.m4v'
                            ,'.3gp'
                            ,'.iso'
                            ]

movie_title_specials    = [
                            '('
                            ,')'
                            ,'['
                            ,']'
                            ]

movie_title_splitter    = [
                            '2160p'
                            ,'1080i'
                            ,'1080p'
                            ,'720p'
                            ,'480p'
                            ,'4k'
                            ,'7Gb'
                            ,'6Gb'
                            ,'4Gb'
                            ,'2Gb'
                            ,'1GB'
                            ,'BluRay'
                            ,'Blu-Ray'
                            ,'BRrip'
                            ,'BDrip'
                            ,'BDRemux'
                            ,'DVD Rip'
                            ,'DVDrip'
                            ,'dvdrip'
                            ,'DVD-R'
                            ,'HDDVDRip'
                            ,'Webrip'
                            ,'xvid'
                            ,'DivX'
                            ,'VHSRip'
                            ,'PROPER'
                            ,'REMASTERED'
                            ,'x264'
                            ,'H264'
                            ,'x265'
                            ,'H265'
                            ,'HD'
                            ,'HDRip'
                            ,'HDTV'
                            ,'dvdrip'
                            ,'Eng'
                            ,'('
                            ,')'
                            ,'['
                            ,']'
                            ,'{'
                            ,'}'
                            ,'-'
                            ,'Criterion Collection'
                            ,'Criterion 1080p'
                            ,'REPACK'
                            ,'Complete Restored Edition'
                            ,'Collectors Edition'
                            ,'Special Collectors Edition'
                            ,'Uncut Version'
                            ,'Directors Cut'
                            ,'Director\'s Cut'
                            ,'Criterion'
                            ,'READNFO'
                            ,'SUBBED'
                            ]
movie_title_resolutions    = {'2160p': '2160p'
                            ,'1080i': '1080p'
                            ,'1080p': '1080p'
                            ,'1080': '1080p'
                            ,'720p': '720p'
                            ,'480p': '480p'
                            ,'4k': '2160p'
                            ,'BluRay': '1080p'
                            ,'Blu-Ray': '1080p'
                            ,'BRRIP': '1080p'
                            ,'BDRIP': '1080p'
                            ,'BDRemux': '1080p'
                            ,'DVDrip': '480p'
                            ,'DVD-R': '480p'
                            ,'DVDR': '480p'
                            ,'DVD': '480p'
                            ,'WEBrip': '480p'
                            }

video_file_hires_table     = {'2160p': 9663676416 # 9 Gigabytes = 9663676416 Bytes
                            ,'1080p': 6442450944 # 6 Gigabytes = 6442450944 Bytes
                            ,'720p': 4294967296 # 4 Gigabytes = 4294967296 Bytes
                            ,'480p': 1073741824 # 1 Gigabytes = 1073741824 Bytes
                            }



import unicodedata

def strip_accents(text):

    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text)

def string_found(needle, hay):
   needle = " " + needle.strip() + " "
   hay = " " + hay.strip() + " "
   return hay.find(needle)

# parse imdb website
# fetch watchlist for given imdb_user_id
# return bidimensional array: list_id, list_name
# ==============================================================================

def get_imdb_user_lists(imdb_user_id):

    url = 'https://www.imdb.com/user/%s/lists' % (imdb_user_id)


    logging.info("Grabbing %s user's lists from imdb.com" % imdb_user_id)
    logging.info("" + url)

    response = urlopen(url)
    body = response.read()


    # ATTENTION !!!
    # WARNING !!!
    # This needs to be updated if the imdb site will change its HTML code !!!

    ID_SIGNATURE_START = '    <a class="list-name" href="/list/'
    ID_SIGNATURE_END = '</a>'

    the_ids = []
    for line in body.splitlines():
        line = str(line)
        if (ID_SIGNATURE_START in line):
            found = line[line.find(ID_SIGNATURE_START)+len(ID_SIGNATURE_START):len(line)-len(ID_SIGNATURE_END)-1]
            logging.debug('Found list: ' + found)
            obj = found.split('/">')
            the_ids.append(obj)


    logging.debug('Fetching user lists completed!')
    logging.debug(the_ids)

    return the_ids




# parse imdb website
# fetch list content for a given imdb_list_id

def get_imdb_list_movies(imdb_list_id):

    if imdb_list_id != None:
        url='https://www.imdb.com/list/'+imdb_list_id+'/export?ref_=ttls_exp'
    else:
        return

    logging.info('Fetching movies from imdb list export file: '+url)

    response = urllib.request.urlopen(url)
    body = response.read()

    if cfg.verbose:
        logging.debug('csv file:')
        logging.debug(body)
        logging.debug('---')

    # parse some data

    the_ids = []
    # skip the first line (header) with [1:]
    for line in body.splitlines()[1:]:

        line = line.decode('latin-1')
        if cfg.verbose:
            logging.debug(line)

        array = line.split(',')
        found = array[1]

        if cfg.verbose:
            logging.debug('Found id: ' + found)

        if re.match("^tt\d+", found):
            the_ids.append(found)

    if cfg.verbose:
        logging.debug('Fetching movies from list completed!')
        logging.debug(the_ids)

    return the_ids


# parsing idb website
# return a list with all user's movies by collections

def get_imdb_user_movies(imdb_user_id):

        global imdb_list_array

        logging.info("Getting watchlist movies from IMDB for user: " + imdb_user_id)
        # get all user public lists
        # obtain list id and list name

        listids = get_imdb_user_lists(cfg.imdb_user_id)

        # obtain movieids array for each list

        for onelist in listids:
            imdbids = get_imdb_list_movies(onelist[0])
            q = [None] * 3
            q[0] = onelist[0]
            q[1] = onelist[1]
            q[2] = imdbids
            imdb_list_array.append(q)

        # Now we have the complete database of list ids including movies
        if cfg.verbose:
            for line in imdb_list_array:
                logging.debug('\n'.join(map(str, line)))


# generate an XML tags for the movie
# by searching the movie in my iMDB movies lists

def get_movie_tags(imdb_movie_id):

    global imdb_list_array
    the_tags = ""

    logging.info('Generating movie <tags> for: ' + imdb_movie_id)

    if cfg.verbose:
        logging.debug('The IMDB lists array looks like this:')
        logging.debug(imdb_list_array)

    logging.info('Searching for the movie in the imdb lists...')

    count = 0
    for list in imdb_list_array:
        for id in list[2]:
            if cfg.verbose:
                logging.debug('Checking id: ' + id)
            if id == imdb_movie_id:
                if cfg.verbose:
                    logging.debug(' Found '+ id +' movie in:')
                    logging.debug(list[0])
                    logging.debug(list[1])
                    logging.debug(list[2])
                the_tags += "\n<tag>" + str(list[1]) + "</tag>"
                count += 1

    logging.info('Found the movie in '+str(count)+' imdb lists!')
    if cfg.verbose:
        logging.debug('The <tags> for: ' + imdb_movie_id + ' are: ')
        logging.debug(the_tags)

    return the_tags


# get a decently clean movie title from a messy release folder names
# ==============================================================================


def get_movie_resolution(video_file_name):


    for key in movie_title_resolutions:
        if key.lower() in video_file_name.lower():
            return str(movie_title_resolutions[key])
            break

    return None

# get a decently clean movie title from a messy release folder names
# ==============================================================================

def get_clean_name_by_name(the_movie_name):

    logging.info('Cleaning up name: '+the_movie_name)
    name, ext = os.path.splitext(the_movie_name)
    the_movie_name  = name
    logging.debug(the_movie_name)


    # replace everything that is not letter or number
    #the_movie_name = re.sub('[^A-Za-z0-9]+', ' ', the_movie_name)
    # but keep accented letters french / etc
    the_movie_name = re.sub('[^ ^\-^(^)^\[^\]^{^}^A-Za-z0-9À-ÖØ-öø-ÿЀ-ӿ]+', ' ', the_movie_name)
    the_movie_name = the_movie_name.lstrip().rstrip()

    logging.debug(the_movie_name)

    for replacer in movie_title_specials:
        the_movie_name = the_movie_name.replace(replacer, ' '+replacer+' ')

    double_space = True
    while double_space:
        if ('  ' in the_movie_name):
            double_space = True
            the_movie_name = the_movie_name.replace('  ', ' ')
        else:
            double_space = False

    the_movie_name = the_movie_name.lstrip().rstrip()

    split_pos = 0

    # remove first hyphen if after a year: e.g. 1997 -
    if re.match("^[0-9]{4} - (.*?)$", the_movie_name):
        the_movie_name = the_movie_name.replace(' - ',' ',1)

    # prepare name for splitter word checking
    the_movie_name = ' '+the_movie_name+' '

    # find all subtext that marking the end of the movie name part (e.g. DVDRIP 720P)
    for splitter in movie_title_splitter:
        tmp_pos = the_movie_name.lower().find(' '+splitter.lower()+' ')
        if (tmp_pos >0 and (split_pos == 0 or tmp_pos < split_pos)):
                split_pos = tmp_pos

    if split_pos !=0:
        the_movie_name = the_movie_name[: split_pos]

    # get rid of the last special chars like ()
    the_movie_name = re.sub('[^A-Za-z0-9À-ÖØ-öø-ÿЀ-ӿ]+', ' ', the_movie_name)
    the_movie_name = the_movie_name.lstrip().rstrip()


    logging.info("Clean movie name: " + the_movie_name)
    return the_movie_name



# Get imdb details using local imdbpie library
# ==============================================================================

def get_imdb_details_by_search_via_imdbpie(search):

    logging.info('Searching via Imdbpie: ')
    logging.info(search)


    # perform search

    try:
        imdb_search = imdb.search_for_title(search)
    except:
        logging.error('Cannot perform imdbpie search!')
        return None

    logging.debug('Search result list:')
    logging.debug(imdb_search)



    # get movie year from searching
    # if year is found at the beginning or at the end ..

    year = None

    if re.search("^[1-9]\d{3,} ", search):
        year = search[:4]
        search = search[4:]
        logging.debug('Found year at the start of the search:'+year)
        logging.debug('Shortened search:'+search)

    else:
        if re.search(" [1-9]\d{3,}$", search):
            year = search[len(search)-4:]
            search = search[:len(search)-4]
            logging.debug('Found year at the end of the search:'+year)
            logging.debug('Shortened search:'+search)

    # inititalise some magic stuff
    first_imdb_object = True
    magic_sort = []
    search = strip_accents(search)

    # only feature films !!! ??? !!!
    imdb_object = [x for x in imdb_search if x.type=='feature']
    #imdb_object = imdb_search

    for i in range(len(imdb_object)):

        sort=0

        logging.debug('#'+str(i))
        logging.debug('---')
        logging.debug('Search result object #'+str(i))
        logging.debug(imdb_object[i])

        if first_imdb_object == True:
            sort +=1
            first_imdb_object = False
            logging.debug('First object gets priority!: '+str(sort))


        if imdb_object[i].title.strip().lower() == search.strip().lower():
            sort+=1
            logging.debug('Exact matching name gets priority!: '+str(sort))


        if year:
            if str(imdb_object[i].year) == str(year):
                logging.debug('Found matching year!: '+year)
                sort +=2

        for word in imdb_object[i].title.split(' '):
            logging.debug(word.lower()+'|?|'+search.lower())
            if string_found(word.lower(),search.lower()) >=0:
                logging.debug('Found matching word in movie title!: '+word)
                sort +=1
            else:
                sort -=1


        logging.debug('Magic priority:'+str(sort))
        logging.debug(' ')
        magic_sort.append(sort)

    # time to sort by my own magic
    logging.debug('Magic index:')
    magic_index = 0
    if magic_sort:
        magic_index = magic_sort.index(max(magic_sort))
    logging.debug(magic_index)
    #ut.sort(key=lambda x: x.count, reverse=True)


    if  imdb_object:
        logging.debug('Done. Returning.')
        logging.debug(imdb_object[magic_index])
        return imdb_object[magic_index]
    else:
        return None








def init_tmdb():
    global tmdb
    global tmdb_movie
    global cfg

    tmdb = TMDb()
    tmdb.api_key = cfg.tmdb_api_key
    tmdb.external_source='imdb_id'
    tmdb_movie = Movie()

# Get imdb details using online tmdb api
# ==============================================================================
def get_imdb_details_by_search_via_tmdb(search):

    global cfg
    imdb_object = {}

    url ='https://api.themoviedb.org/3/search/movie?query='+urllib.parse.quote(search)+'&api_key='+cfg.tmdb_api_key+'&language=en-US&include_adult=false&append_to_response=trailers'
    logging.info(url)

    response = urlopen(url)
    body = response.read()
    data = json.loads(body)

    if cfg.verbose:
        logging.debug(data)

    imdb_object = data['results'][0]

    if cfg.verbose:
        logging.debug('First search result:')
        logging.debug(imdb_object)

    return imdb_object


# Get imdb details using online tmdb api
# ==============================================================================
def get_imdb_details_by_id_via_tmdb(imdb_id):

    global cfg
    imdb_object = {}

    url ='https://api.themoviedb.org/3/find/'+imdb_id+'?api_key='+cfg.tmdb_api_key+'&language=en-US&external_source=imdb_id'
    response = urlopen(url)
    body = response.read()
    data = json.loads(body)

    try:
        imdb_object['original_title']= data['movie_results'][0]['original_title']
        imdb_object['title'] = data['movie_results'][0]['title']
    except:
        return None

    if cfg.verbose:
        logging.debug(imdb_object)


    return imdb_object


# Get imdb details using local imdbpie library
# ##############################################################################
def get_imdb_details_by_id_via_imdbpie(imdb_id):

    imdb_object = imdb.get_title(imdb_id)
    return imdb_object





# ##############################################################################
def get_imdb_details_by_search_via_rapidapi(search):

    logging.info('Searching via rapidapi: ')
    logging.info(search)

    # perform search

    url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/search/" + search

    headers = {
        'x-rapidapi-key': cfg.x_rapidapi_key,
        'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com"
        }

    try:
        response = requests.request("GET", url, headers=headers)
        # get movie data from json
        data = json.loads(response.text)
        imdb_object = data['titles']
    except:
        logging.error('Cannot perform rapidapi search!')
        return None


    logging.debug('Search results list:')
    logging.debug(imdb_object)


    # get movie year from searching
    # if year is found at the beginning or at the end ..

    year = None

    if re.search("^[1-9]\d{3,} ", search):
        year = search[:4]
        search = search[4:]
        logging.debug('Found year at the start of the search:'+year)
        logging.debug('Shortened search:'+search)

    else:
        if re.search(" [1-9]\d{3,}$", search):
            year = search[len(search)-4:]
            search = search[:len(search)-4]
            logging.debug('Found year at the end of the search:'+year)
            logging.debug('Shortened search:'+search)

    # inititalise some magic stuff
    first_imdb_object = True
    magic_sort = []
    search = strip_accents(search)


    # get info for the first movie in the json
    for i in range(len(imdb_object)):

        sort=0
        logging.debug('#'+str(i))
        logging.debug('---')
        logging.debug('Search result object #'+str(i))
        logging.debug(imdb_object[i])


        if first_imdb_object == True:
            sort +=1
            first_imdb_object = False
            logging.debug('First object gets priority!: '+str(sort))


        if imdb_object[i]['title'].strip().lower() == search.strip().lower():
            sort+=1
            logging.debug('Exact matching name gets priority!: '+str(sort))


        for word in imdb_object[i]['title'].split(' '):
            logging.debug(word.lower()+'|?|'+search.lower())
            if string_found(word.lower(),search.lower()) >=0:
                logging.debug('Found matching word in movie title!: '+word)
                sort +=1
            else:
                sort -=1
            logging.debug(sort)


        logging.debug('Magic priority:'+str(sort))
        logging.debug(' ')
        magic_sort.append(sort)



    # time to sort by my own magic
    logging.debug('Magic index:')
    magic_index = 0
    if magic_sort:
        magic_index = magic_sort.index(max(magic_sort))
    logging.debug(magic_index)
    #ut.sort(key=lambda x: x.count, reverse=True)


    if  imdb_object:
        logging.debug('Done. Returning.')
        logging.debug(imdb_object[magic_index])
        return imdb_object[magic_index]
    else:
        return None



# get imdb object by search using rapidapi
# ##############################################################################

def get_imdb_details_by_id_via_rapidapi(imdb_id):

    logging.info("Get IMDB details by id via rapidapi: " + imdb_id)

    url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/" + imdb_id

    headers = {
        'x-rapidapi-key': cfg.x_rapidapi_key,
        'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers)

    if cfg.verbose:
        logging.debug(response.text)

    # get movie data from json
    data = json.loads(response.text)

    try:
        return data

    except:
        return None





# Get imdb details using local imdbpie and second by rapidapi library
# ##############################################################################

def get_imdb_id_by_name(folderpath, supposed_id):

    imdb_id = None
    first_imdb_id = None
    second_imdb_id = None
    grabbed_imdb = False

    # no need to decode in python 3
    if sys.version_info.major != 3:
        folderpath = folderpath.decode("utf-8")

    folder, the_movie_name = os.path.split(folderpath)

    logging.info("First: Searching movie via imdbpie")
    search_name = get_clean_name_by_name(the_movie_name)
    first_imdb_object = get_imdb_details_by_search_via_imdbpie(search_name)

    if cfg.verbose:
        logging.debug(first_imdb_object)

    if first_imdb_object != None:
        first_imdb_id     = first_imdb_object.imdb_id
        imdb_id = first_imdb_id
        grabbed_imdb = True
        logging.info("Found imdb_movie_id: " + first_imdb_id)

    logging.info("Second: Searching movie via rapidapi")
    second_imdb_object = get_imdb_details_by_search_via_rapidapi(search_name)

    if cfg.verbose:
        logging.debug(second_imdb_object)

    if second_imdb_object != None:
        second_imdb_id     = second_imdb_object['id']
        logging.info("Found imdb_movie_id: " + second_imdb_id)
        if grabbed_imdb == False:
            imdb_id = second_imdb_id
            grabbed_imdb = True

    # decide between the two imdb ids
    # if imdb ids are different choose the second_imdb_id

    if (first_imdb_id != None and second_imdb_id != None and supposed_id != None and second_imdb_id == supposed_id) or (first_imdb_id == None and second_imdb_id != None):
        # prioritise scond found id
        # if second id is the supposed id (found in the nfo)
        imdb_id = second_imdb_id
    else:
        imdb_id = first_imdb_id


    if imdb_id == None:
        logging.info("Cannot grab imdb id from online IMDB data")

    return imdb_id





# find single files and move them to folders
# ##############################################################################

def fix_orphan_files(basepath):

    global video_extensions
    logging.info('Fixing orphan files in: '+basepath)

    os.chdir(basepath)

    # get the list of video files
    video_files_grabbed = []
    for ext in video_extensions:
        video_files_grabbed.extend(glob.glob('*'+ext))
        video_files_grabbed.extend(glob.glob('*'+ext.upper()))

    if cfg.verbose:
        logging.debug(video_files_grabbed)


    # process all video files
    for file in video_files_grabbed:
        extra_files = glob.glob(os.path.splitext(file)[0]+'.*')

        logging.info('\nFile: \t'+file)
        logging.info('=============================================================================')

        # create temp folder path
        file_path = os.path.join(basepath, file)
        tmp_folder_path = os.path.join(basepath, os.path.splitext(file)[0]+' '+str(time.time()))
        os.mkdir(tmp_folder_path)

        # move file to temp folder
        os.rename(os.path.join(basepath, file),os.path.join(tmp_folder_path, file))
        logging.info('Moved video file to: ' + file)

        for extra_file in extra_files:
            if extra_file != file and extra_file not in video_files_grabbed:
                os.rename(os.path.join(basepath, extra_file),os.path.join(tmp_folder_path, extra_file))
                logging.info('Moved extra file: '+extra_file)


        # rename tmp folder
        new_folder_path = os.path.join(basepath, os.path.splitext(file)[0])
        try:
            os.rename(tmp_folder_path, new_folder_path)
        except:
            os.rename(tmp_folder_path, new_folder_path+' '+str(time.time()))


        logging.info('Created new movie folder: '+new_folder_path)




# Cleanup movie folde names (remove !@#$)
# ##############################################################################

def folder_cleanup(my_basepath):

    marked_failed = False
    logging.info("Performing markings cleanup for movies folder: " + my_basepath)

    # start in basedir
    for fn in os.listdir(my_basepath):

        folderpath = os.path.join(my_basepath, fn)

        if not os.path.isdir(folderpath):
            continue # Not a directory

        logging.info('Cleaning folder name: ' + fn)


        # if folder is special ### type just ignore it

        if fn[: 2] == '$ ' or fn[: 2] == '# ' or fn[: 2] == '@ ' or fn[: 2] == '! ':
            logging.debug("Found special "+fn[: 2]+" folder path. Trying to clean it up.")

            new_folderpath = os.path.join(my_basepath, fn[2:])
            logging.debug('New folder name: ' + new_folderpath)

            # trying to rename folder while minding duplicates

            duplicate_folderpath = new_folderpath+' DUPLICATE '+str(time.time())
            tmp_folderpath = new_folderpath+' TMP '+str(time.time())

            try:
                os.rename(folderpath, tmp_folderpath)
                folderpath = tmp_folderpath
                os.rename(tmp_folderpath, new_folderpath)
                marked_folder = True
                #keep for next stage (movie rename)
                folderpath = new_folderpath
            except:
                try:
                    os.rename(folderpath, duplicate_folderpath)
                    new_folderpath = duplicate_folderpath
                    marked_folder = True
                    #keep for next stage (movie rename)
                    folderpath = new_folderpath
                except:
                    marked_folder = False
                    marked_failed = True

    if not marked_failed:
        logging.info('Folder markings cleanup succesfull!')
    else:
        logging.warning('Failed to cleanup all folder markings!')


# Safe rename of files or folders
# ##############################################################################

def safe_rename(folderpath,new_folderpath):

    # trying to rename folder while minding duplicates

    logging.debug('Renaming!')
    logging.debug('Old folder name: ' + folderpath)
    logging.debug('New folder name: ' + new_folderpath)

    try:
        tmp_folderpath = new_folderpath+' - TMP '+str(time.time())
        os.rename(folderpath, tmp_folderpath)
        folderpath = tmp_folderpath
        os.rename(tmp_folderpath, new_folderpath)
        return True
    except:

        if  ' - DUPLICATE' not in new_folderpath:
            new_folderpath = new_folderpath+' - DUPLICATE'
            safe_rename(folderpath,new_folderpath)
            return True
        else:
            duplicate_folderpath = new_folderpath+' '+str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            try:
                os.rename(folderpath, duplicate_folderpath)
                new_folderpath = duplicate_folderpath
                return True
            except:
                return False


# Find and mark duplicate movies in the main folder
# ##############################################################################


def check_duplicates(my_basepath):

    global video_extensions
    nfo_file = None
    nfo_found = False
    count_renamed = 0

    movies=[]


    marked_failed = False
    logging.info("Performing duplicates check for movies folder: " + my_basepath)

    # start in basedir
    for folder_name in os.listdir(my_basepath):

        folderpath = os.path.join(my_basepath, folder_name)

        if not os.path.isdir(folderpath):
            continue # Not a directory

        logging.info('Checking folder: ' + folder_name)

        os.chdir(folderpath)

        # get the list of video files
        video_files_grabbed = []
        for ext in video_extensions:
            video_files_grabbed.extend(glob.glob('*'+ext))
            video_files_grabbed.extend(glob.glob('*'+ext.upper()))

        video_files_grabbed.sort(key=lambda f: os.lstat(f).st_size, reverse=True)

        logging.debug('Video files found:')
        logging.debug(video_files_grabbed)


        video_found = False
        # get the first video file in the list (the biggest size)
        for video_file in video_files_grabbed:
            if video_file:
                video_found = True
                break

        logging.debug(os.path.splitext(video_file)[0]+'.nfo'+'|')
        nfo_files = glob.glob('*.nfo')

        logging.debug('Nfo files found:')
        logging.debug(nfo_files)

        nfo_found = False
        for nfo_file in nfo_files:
            if nfo_file == os.path.splitext(video_file)[0]+'.nfo':
                logging.debug('Found nfo file: '+nfo_file)
                nfo_found = True
                break


        if not video_found:
            logging.warning('Warning: Can\'t find video file!')
            logging.warning('Marking folder: ! '+folder_name)

            safe_rename(folderpath,os.path.join(my_basepath, '! '+folder_name))
            continue



        if not nfo_found:
            logging.warning('Warning: Can\'t find nfo file!')
            logging.warning('Marking folder: ! '+folder_name)
            safe_rename(folderpath,os.path.join(my_basepath, '! '+folder_name))
            continue



        # get nfo file contents
        nfo_filepath = os.path.join(folderpath, nfo_file)

        imdb_id = get_id_by_nfo(nfo_filepath)


        if imdb_id:
            found_imdb = True
            logging.debug("Found nfo IMDB id: "+imdb_id)
            logging.debug("In folder: "+folderpath)

            obj={}
            obj['id'] = imdb_id
            obj['path'] = folderpath
            movies.append(obj)

    logging.debug(movies)


    seen_titles = set()
    duplicates = []
    for obj in movies:
        if obj['id'] not in seen_titles:
            seen_titles.add(obj['id'])
        else:
            duplicates.append(obj['id'])

    logging.debug('Movies:')
    logging.debug(movies)

    logging.debug('Duplicates:')
    logging.debug(duplicates)


    # if folder is special ### type just ignore it
    for duplicate in duplicates:
        for movie in movies:

            if movie['id'] == duplicate and ' DUPLICATE' not in movie['path']:

                logging.debug('!!!')
                logging.debug(duplicate)

                renamed_ok = safe_rename(movie['path'], movie['path']+' - DUPLICATE')


                if renamed_ok:
                    count_renamed+=1
                else:
                    marked_failed = True

    logging.info('Duplicate movies found: '+ str(len(duplicates)))
    logging.info('Duplicate movies renamed: '+ str(count_renamed))

    if not marked_failed:
        logging.info('All duplicates marked succesfully!')
    else:
        logging.warning('Failed to mark all duplicates!')



# Update an existing nfo file with a new XML
# ##############################################################################


def update_nfo(filepath,the_xml):


    found_xml = False
    found_multiple_xml = False

    # reding nfo file content
    with open(filepath, "rt", encoding="utf-8", errors="ignore") as f:

        try:
            nfo = f.read()
            f.close()
        except:
            logging.warning('Cannot open nfo file!')


    if ('<movie>' in nfo):

        if cfg.verbose:
            logging.debug("NFO FILE:--------")
            logging.debug(nfo)
        # check if <movie> xml exists!
        regex = "<movie>[\s\S]*?<\/movie>"
        matches = re.findall(regex, nfo)

        for old_xml in matches:
            logging.info("Great news: Found movie XML tags in nfo !!!")
            if found_xml != True:
                found_xml = True

            else:
                found_multiple_xml = True
                logging.warning("Bad news: Found multiple movie XML tags in nfo !!!")


    if (found_xml == False):

        logging.warning('nfo file without movie XML info !!!')
        # edit nfo file and add <movie><tag> info

        logging.info("Adding movies XML to existing nfo file: " + os.path.basename(filepath))
        # open the input file in write mode
        # write xml in front of the nfo text
        f = open(filepath, "wt")
        nfo = the_xml + '\n' + nfo
        f.write(nfo)
        f.close()

    else:

        # first check if force rewrire is enabled
        if (cfg.force_rewrite_xml == True):

            logging.info("Updating movie XML to existing nfo file: " + os.path.basename(filepath))
            #open the input file in write mode
            f = open(filepath, "wt")
            #overrite the input file with the resulting data
            nfo = nfo.replace(old_xml, the_xml)
            f.write(nfo)
            #close the file
            f.close()





# Search the nfo file for an IMDB id and return it (or None)
# ##############################################################################


def get_id_by_nfo(filepath):

    # reding nfo file content
    with open(filepath, "rt", encoding="utf-8", errors="ignore") as f:

        try:
            nfo = f.read()
        except:
            nfo = None
            found_nfo = False
            found_broken_nfo = True


    # check for IMDB link and IMDB code in file
    if nfo != None and (('imdb' in nfo) or ('IMDB' in nfo)):

        # regexp searching for something like http://www.imdb.com/title/tt0064030
        regex = "((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)"

        imdb_link = ""
        matches = re.findall(regex, nfo)
        for match in matches:
            if ('imdb' in match):
                imdb_link = match
                idmatches = re.findall("tt\d+", imdb_link)
                for idmatch in idmatches:
                    imdb_id = idmatch
                    return imdb_id
                    break


    return None


# Moving all folder contents
# while making sure not to overwrite duplicate movies
# ##############################################################################

def move_folder_contents(my_basepath,my_destination):

    marked_failed = False

    logging.info("Moving movie folders")
    logging.info(" from:\t" + my_basepath)
    logging.info(" to:\t" + my_destination)

    # start in basedir
    for fn in os.listdir(my_basepath):

        folderpath = os.path.join(my_basepath, fn)

        if not os.path.isdir(folderpath):
            continue # Not a directory

        logging.info('Moving folder name: ' + fn)

        new_folderpath = os.path.join(my_destination, fn)

        folder_renamed = safe_rename(folderpath,new_folderpath)

        if folder_renamed:
            folderpath = new_folderpath
        else:
            marked_failed = True

    if not marked_failed:
        logging.info('Moved all folders succesfully!')
    else:
        logging.warning('Failed to move all folders!')







# process files in folderpath
# if nfo is found, parse it for IMDB link
# if no imdb link is found add one
# if no nfo is found create one
# ##############################################################################

def process_movie_folder(folderpath):

    video_file_name = ""
    imdb_id = ""
    nfo_imdb_id = ""
    imdb_link = ""
    imdb_title = ""
    imdb_title_en = ""
    imdb_image = ""
    imdb_year = ""
    found_nfo = False
    found_xml = False
    found_video = False
    found_imdb = False
    found_multiple_videos = False
    found_multiple_xml = False
    found_multiple_nfo = False
    grabbed_imdb = False
    grabbed_imdb_uncertain = False
    imdb_uncertain = False
    found_broken_nfo = False
    movie_id_by_file = None
    movie_id_by_folder = None
    grabbed_imdb_id = None
    renamed_folder = False
    renamed_failed = False
    marked_folder = False
    marked_failed = False

    # if folder is special ### type just ignore it
    if cfg.ignore_special_folders:
        tfolder, tname = os.path.split(folderpath)
        if tname[: 2] == '$ ' or tname[: 2] == '# ' or tname[: 2] == '@ ' or tname[: 2] == '! ':
            logging.info("Found special "+tname[: 2]+" folder path. Exiting without processing it.")
            return

    # GET VIDEO FILE !!!
    # first get video file name (for later use)

    # list files in the current working directory and sorted by
    # file size (largest to smallest)
    os.chdir(folderpath)
    files = os.listdir(folderpath)

    files.sort(key=lambda f: os.lstat(f).st_size, reverse=True)

    found_video = False
    for file in files:
        for extension in video_extensions:
            if ((file.endswith(extension) or file.endswith(extension.upper())) and not file.startswith('.')):
                if found_video != True:
                    video_file_name = file
                    logging.info('Found video file: '+file)
                    found_video = True
                else:
                    found_multiple_videos = True

    if found_video == False:
        logging.warning('No video file found!')

    if found_multiple_videos == True:
        logging.warning('Multimple video files found!')

    # GET NFO FILE(S) !!!
    # now check all files in the folder for nfo file

    os.chdir(folderpath)
    found_nfo == False

    nfo_files = []
    nfo_files = glob.glob('*.nfo')
    nfo_files.extend(glob.glob('*.NFO'))

    logging.debug('nfo_files:')
    logging.debug(nfo_files)

    if len(nfo_files)<=0:
        logging.warning('Warning: No nfo files found')

    if len(nfo_files)>1:
        found_multiple_nfo = True
        logging.warning('Warning: Found multiple nfo files! ('+os.path.basename(folderpath)+')')

    if len(nfo_files)>=1:

        found_nfo = True
        nfo_file = nfo_files[0]
        logging.info('Found nfo file: '+nfo_file)

        # get nfo file contents
        nfo_filepath = os.path.join(folderpath, nfo_file)

        imdb_id = get_id_by_nfo(nfo_filepath)

        if imdb_id:
            found_imdb = True
            logging.info("Found nfo IMDB id: "+imdb_id)


    # if no video and no nfo and no xml then Exiting

    if (found_video == False and found_imdb == False):
        logging.warning("No video, no imdb in nfo: just rename to !!! and exit ")


    # GRABBING IMDB_ID !!!
    # done processing nfo file
    # if no IMDB data was found in nfo try to find it online
    # only if video file exists
    # even if the imdb_id was already found in nfo, perform the search anyway
    # in order to later compare the results

    if found_video == True:

        # grab IMDB link by folder name
        # also send imdb_id found in nfo to compare it
        logging.info('###')
        logging.info("Searching IMDB link by folder name: ")
        logging.info(folderpath)
        movie_id_by_folder = get_imdb_id_by_name(folderpath,imdb_id)

        # grab IMDB link by file name
        # also send imdb_id found in nfo to compare it
        if found_video == True:
            logging.info('###')
            logging.info("Searching IMDB link by file name: ")
            logging.info(video_file_name)
            movie_id_by_file = get_imdb_id_by_name(video_file_name,imdb_id)

        # compare two movie ids
        # prioritize the id that matched the imdb_id (nfo_imdb_id)

        if (movie_id_by_folder != None and movie_id_by_file!= None and imdb_id != None and movie_id_by_file == imdb_id) or (movie_id_by_folder == None and movie_id_by_file!= None):
                grabbed_imdb_id = movie_id_by_file
                grabbed_imdb = True
        else:
            if movie_id_by_folder != None:
                grabbed_imdb_id = movie_id_by_folder
                grabbed_imdb = True
            else:
                grabbed_imdb = False

        if movie_id_by_folder!= movie_id_by_file:
            logging.warning("Warning! Grabbed different IMDB ids from folder and file: ")
            logging.info("By folder:"+str(movie_id_by_folder)+' '+folderpath)
            logging.info("By file:"+str(movie_id_by_file)+' '+video_file_name)
            grabbed_imdb_uncertain = True



    if imdb_id and grabbed_imdb_id:
        if imdb_id != grabbed_imdb_id:
            imdb_uncertain = True
            logging.warning("WARNING! Online grabbed IMDB id <> nfo found IMDB id !!!")


    # choose the final imdb_id
    if not found_imdb:
        if grabbed_imdb:
            imdb_id = grabbed_imdb_id



    # if i have the imdb_id then let's get more info

    if found_imdb or grabbed_imdb:

        imdb_object = get_imdb_details_by_id_via_imdbpie(imdb_id)
        imdb_object_rapidapi = get_imdb_details_by_id_via_rapidapi(imdb_id)
        imdb_object_tmdb = get_imdb_details_by_id_via_tmdb(imdb_id)

        if imdb_object != None:
            imdb_id     = imdb_object.imdb_id
            imdb_title  = imdb_object.title.lstrip().rstrip()

            imdb_link   = 'https://www.imdb.com/title/'+imdb_id+'/'
            if imdb_object.image:
                imdb_image  = imdb_object.image.url
            imdb_year   = imdb_object.year
            # remember to mark grabbed_imdb = True
            # not sure grabbed info is correct so force a manual check
            logging.info("Grabbed IMDBpie code: " + imdb_id)
            logging.info("Grabbed IMDBpie link: " + imdb_link)
            logging.info("Grabbed IMDBpie title: " + imdb_title)


        imdb_title_en = ""

        if imdb_object_tmdb != None:
            tmdb_title_en = imdb_object_tmdb['title']
            tmdb_title_en = tmdb_title_en.lstrip().rstrip()
            tmdb_title_original = imdb_object_tmdb['original_title']
            tmdb_title_original = tmdb_title_original.lstrip().rstrip()
            logging.info("Grabbed tmdb english title: " + tmdb_title_en)
            logging.info("Grabbed tmdb original title: " + tmdb_title_original)

            if tmdb_title_en.lower() != imdb_title.lower():
                imdb_title_en = tmdb_title_en

        # if first  different than second then second must be english version :)
        if (imdb_title_en != ""):
            imdb_title = imdb_title + ' ('+imdb_title_en+')'




    # prepare the tags
    if imdb_id != None:
        the_tags = get_movie_tags(imdb_id)

    # prepare the xml code with IMDB and tags and everything

    the_xml = "<movie>"

    if imdb_id != None:
        the_xml += "\n<imdb>"+imdb_link+"</imdb>"
        the_xml += "\n<uniqueid type=\"\" default=\"true\">"+imdb_id+"</uniqueid>"
        if imdb_title != "":
            the_xml += "\n<title>"+imdb_title+"</title>"
        if imdb_year !="":
            the_xml += "\n<year>"+str(imdb_year)+"</year>"
        if the_tags != "":
            the_xml += the_tags
    the_xml += "\n</movie>"

    if sys.version_info.major != 3:
            the_xml = the_xml.encode('utf-8').strip()


    # writing to nfo file
    # check for <movie> and <tag>
    # file exists
    if found_nfo == True:

        update_nfo(nfo_filepath,the_xml)

    else:

        if found_video:

            # no nfo file found, try to create one
            logging.info('Couldn\'t find nfo file. Creating new nfo file!')

            # rename
            pre, ext = os.path.splitext(video_file_name)
            nfo_file = pre + '.nfo'
            nfo_file_path = os.path.join(folderpath, nfo_file)
            f = open(nfo_file_path, "wt")
            f.write(the_xml)
            f.close()

            # no nfo file found, try to create one
            logging.info('Wrote new nfo file:' +  os.path.basename(nfo_file))



    poster_file = "poster.jpg"

    # final cleanup
    # if nfo filename is different than the video file rename it
    if found_video:

        nfo_pre, nfo_ext = os.path.splitext(nfo_file)
        vid_pre, vid_ext = os.path.splitext(video_file_name)
        poster_file = vid_pre+'-poster.jpg'

        if (nfo_pre != vid_pre):
            logging.info('Comparing nfo and video names:')
            logging.info(nfo_pre)
            logging.info(vid_pre)
            old_nfo_path = os.path.join(folderpath, nfo_file)
            new_nfo_path = os.path.join(folderpath, vid_pre+'.nfo')
            nfo_file = vid_pre+'.nfo'
            logging.info('nfo and video file names are different: Renaming nfo')
            logging.info('from: \t' + os.path.basename(old_nfo_path))
            logging.info('to: \t' + os.path.basename(new_nfo_path))
            if (old_nfo_path != new_nfo_path):
                # use intermediary name to be able to rename this.file1080 to This.File1080
                safe_rename(old_nfo_path, new_nfo_path)

        if imdb_image:
            # download poster image to current folder
            pfolder, pname = os.path.split(imdb_image)
            r = requests.get(imdb_image, allow_redirects=True)
            open(poster_file, 'wb').write(r.content)
            logging.info("Writing poster file: "+pname)




    # time to rename the folder
    # renaming the movie folder
    # only if some video file exists !!!

    if not imdb_uncertain and found_video and (cfg.do_folder_renaming and (found_imdb or grabbed_imdb)):

        logging.info('Clean renaming enabled.')

        clean_name = imdb_title
        invalid = '<>:"/\|?*'
        for char in invalid:
	           clean_name = clean_name.replace(char, '')

        if sys.version_info.major != 3:
            clean_name = clean_name.encode("utf-8")

        clean_name = str(imdb_year)+' - '+str(clean_name)

        video_resolution = get_movie_resolution(video_file_name)

        if video_resolution != None:
            clean_name += ' - ' + video_resolution
            logging.info("Found movie resolution by file: " + video_resolution)
        else:
            video_resolution = get_movie_resolution(os.path.basename(folderpath))
            if video_resolution:
                clean_name += ' - ' + video_resolution
                logging.info("Found movie resolution by folder: " + video_resolution)


        # get video file size and use it in folder name to mark lowres

        if cfg.do_mark_lowres == True and video_resolution != None:
            video_path = os.path.join(folderpath, video_file_name)
            video_size = os.path.getsize(video_path)
            logging.info('Video file size: ' + str(video_size))

            for key in video_file_hires_table:
                if key.lower() in video_resolution.lower():
                    hires = video_file_hires_table[key]
                    if video_size < hires:
                        clean_name += ' - LOWRES'
                    break


        folder, old_name = os.path.split(folderpath)
        new_folderpath = os.path.join(folder, clean_name)
        logging.info('Old folder name versus new folder name:')
        logging.info("From: \t" + folderpath)
        logging.info("To: \t" + new_folderpath)


        # only if the paths are different !!!
        # try to rename the folder
        # if the folder already exists (duplicate movies)
        # add a timestamp at the end of the folder name

        if (folderpath != new_folderpath):

            logging.info('Old and new names are different. Renaming!')

            renamed_folder = safe_rename(folderpath, new_folderpath)

            if renamed_folder:
                folderpath = new_folderpath
            else:
                renamed_failed = True

            if renamed_folder:
                logging.info('Renamed movie folder to: '+new_folderpath)
            else:
                logging.info('Failed to rename movie folder to: '+new_folderpath)

        else:
            logging.info('No need to rename the movie folder: '+new_folderpath)



    # mark the folder with ### in the front of the name
    # if an empty nfo file was created
    # or if no XML tags were added
    # or
    # mark the folder with !!! in front of the name
    # if no video in folder
    # or if multiple video files were detected

    alerting = '$ '

    if (found_nfo == False
        or found_imdb == False
        or found_xml == False):
        alerting = '# '

    if (found_video == False
        or found_multiple_videos == True
        or found_multiple_xml == True
        or found_multiple_nfo == True
        or found_broken_nfo == True
        or grabbed_imdb_uncertain == True):
        alerting = '@ '

    if (found_video == False
        or imdb_uncertain == True
        or renamed_failed == True
        or (found_imdb == False and grabbed_imdb== False)):
        alerting = '! '

    # some basic alerting
    if found_video == False:
        logging.warning('Warning: Video file not found!')
    if (found_imdb == False and grabbed_imdb == False):
        logging.warning('Warning: Can\'t find imdb id in nfo or online')
    if renamed_failed == True:
        logging.warning('Warning: Rename failed!')
    if imdb_uncertain == True:
        logging.warning('Warning: Imdb ID found in nfo different that search!!')

    if (cfg.do_folder_alerting and alerting):

        logging.warning('Marking the folder name with alert: '+alerting)
        folder, old_name = os.path.split(folderpath)
        new_name = old_name
        new_name = alerting+old_name
        new_folderpath = os.path.join(folder, new_name)


        # only if the paths are different !!!
        # try to rename the folder
        # if the folder already exists (duplicate movies)
        # add a timestamp at the end of the folder name

        if (folderpath != new_folderpath):

            logging.info('Renaming folder!')
            logging.info('From:\t '+folderpath)
            logging.info('To:\t '+new_folderpath)

            marked_folder = safe_rename(folderpath, new_folderpath)

            if marked_folder:
                folderpath = new_folderpath
            else:
                marked_failed = True


            if marked_folder:
                logging.info('Marked movie folder to: '+new_folderpath)
            else:
                logging.info('Failed to mark movie folder to: '+new_folderpath)


        else:
            logging.info('No need to mark the folder: '+new_folderpath)





# process all folders in the given filepath
# ##############################################################################


def process_main_folder(my_basedir):

    logging.info("Processing movies folder: " + my_basedir)

    # start in basedir
    for fn in os.listdir(my_basedir):

        if not os.path.isdir(os.path.join(my_basedir, fn)):
            continue # Not a directory

        logging.info('')
        logging.info('')
        logging.info('Folder: \t' + fn)
        logging.info('################################################################################')

        # process the folder
        folderpath = os.path.join(cfg.basedir, fn)
        process_movie_folder(folderpath)







# Now let's do someting cool
# ##############################################################################


try:


    # enable / setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(cfg.logging_file),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger()

    # Get full command-line arguments
    full_cmd_arguments = sys.argv

    # Keep all but the first
    argument_list = full_cmd_arguments[1:]

    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add long and short argument
    parser.add_argument("--cleanup", "-c", help="Perform a folder cleanup, removing all special folder markings ($ # @ !)",action="store_true")
    parser.add_argument("--duplicates", "-d", help="Mark all duplicate movies with 'DUPLICATE'",action="store_true")

    parser.add_argument("--process", "-p", help="Do imdb folders processing.",action="store_true")
    parser.add_argument("--noalert", "-n", help="Don't do any folder alerts renaming (no !@#$ in the folder names).",action="store_true")
    parser.add_argument("--notags", "-t", help="Don't do the initial tags checking",action="store_true")
    parser.add_argument("--onlytags", "-o", help="Only process tags updates. Nothing else.",action="store_true")
    parser.add_argument("--verbose", "-v", help="Verbose mode. Display debug messages",action="store_true")

    parser.add_argument("--folder", "-f", help="Define main movies folder (containing movies in sub-folders)")
    parser.add_argument("--move", "-m", help="Define destination movies folder. Move all folders from Main folder to destination while taking care of duplicates renaming")

    # Read arguments from the command line
    args = parser.parse_args()

    if args.verbose:
        cfg.verbose = True

    if cfg.verbose:
        logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    logging.info('')
    logging.info('')
    logging.info('Running: The Organizer')
    logging.info('=============================================================================')
    logging.info(''+datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    logging.info('Received command line arguments:')
    logging.info(argument_list)

    # perform actions by arguments

    if args.folder:
        cfg.basedir = args.folder

    if args.noalert:
        cfg.do_folder_alerting = False

    if args.onlytags:
        cfg.onlytags = True


    if args.cleanup:
        folder_cleanup(cfg.basedir)

    if args.duplicates:
        check_duplicates(cfg.basedir)

    if args.move:
        move_folder_contents(cfg.basedir,args.move)

    # no special cleanup, perform normal routine
    if args.process:

        # find all files outside folders and move them to nicely named folders
        fix_orphan_files(cfg.basedir)


        if not args.notags:
            # first we have to grab all user movies from lists / categories
            # will use this later for tags
            get_imdb_user_movies(cfg.imdb_user_id)

        # and now let's process and clean the movies folder
        process_main_folder(cfg.basedir)






except Exception as e:
    errors = True
    logging.error('[ERROR] %s' % e)
    traceback.print_exc()
