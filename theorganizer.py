## The Organizer
## A python movie collection organiser
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
                            ".avi"
                            ,".mpeg"
                            ,".mpg"
                            ,".wmv"
                            ,".mov"
                            ,".mp4"
                            ,".mkv"
                            ,".3gp"
                            ,".iso"
                            ]

movie_title_specials    = [
                            '.'
                            ,'#'
                            ,'!'
                            ,'['
                            ,']'
                            ,'_'
                            ]

movie_title_splitter    = [
                            '2160p'
                            ,'1080i'
                            ,'1080p'
                            ,'720p'
                            ,'4k'
                            ,'BluRay'
                            ,'Blu-Ray'
                            ,'BRrip'
                            ,'BDrip'
                            ,'BDRemux'
                            ,'DVDrip'
                            ,'dvdrip'
                            ,'DVD-R'
                            ,'Webrip'
                            ,'xvid'
                            ,'PROPER'
                            ,'REMASTERED'
                            ,'x264'
                            ,'HDTV'
                            ,'dvdrip'
                            ,'Eng'
                            ,'('
                            ,')'
                            ,'['
                            ,']'
                            ,'_'
                            ,' - '
                            ,'Criterion Collection'
                            ,'Criterion 1080p'
                            ,'REPACK'
                            ,'Complete Restored Edition'
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


# parse imdb website
# fetch watchlist for given imdb_user_id
# return bidimensional array: list_id, list_name
# ==============================================================================

def get_imdb_user_lists(imdb_user_id):

    url = 'https://www.imdb.com/user/%s/lists' % (imdb_user_id)


    logging.info("\tGrabbing %s user's lists from imdb.com" % imdb_user_id)
    logging.info("\t" + url)

    response = urlopen(url)
    body = response.read()


    logging.debug(body)

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


    logging.debug('\tFetching user lists completed!')
    logging.debug(the_ids)

    return the_ids




# parse imdb website
# fetch list content for a given imdb_list_id

def get_imdb_list_movies(imdb_list_id):

    if imdb_list_id != None:
        url='https://www.imdb.com/list/'+imdb_list_id+'/export?ref_=ttls_exp'
    else:
        return

    logging.info('\tFetching movies from imdb list export file: '+url)

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
        logging.debug('\tFetching movies from list completed!')
        logging.debug(the_ids)

    return the_ids


# parsing idb website
# return a list with all user's movies by collections

def get_imdb_user_movies(imdb_user_id):

        global imdb_list_array

        logging.info("\tGetting watchlist movies from IMDB for user: " + imdb_user_id)
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

    logging.info('\tGenerating movie <tags> for: ' + imdb_movie_id)

    if cfg.verbose:
        logging.debug('The IMDB lists array looks like this:')
        logging.debug(imdb_list_array)

    logging.info('\tSearching for the movie in the imdb lists...')

    count = 0
    for list in imdb_list_array:
        for id in list[2]:
            if cfg.verbose:
                logging.debug('\tChecking id: ' + id)
            if id == imdb_movie_id:
                if cfg.verbose:
                    logging.debug('\t Found '+ id +' movie in:')
                    logging.debug(list[0])
                    logging.debug(list[1])
                    logging.debug(list[2])
                the_tags += "\n<tag>" + str(list[1]) + "</tag>"
                count += 1

    logging.info('\tFound the movie in '+str(count)+' imdb lists!')
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

    for replacer in movie_title_specials:
        the_movie_name = the_movie_name.replace(replacer, ' ')

    # replace everything that is not letter or number
    the_movie_name = re.sub('[^A-Za-z0-9]+', ' ', the_movie_name)

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
    if re.match("^[0-9]{4} - (.*?)$", the_movie_name) or  re.match("^[0-9]{4} - (.*?)$", the_movie_name):
        the_movie_name = the_movie_name.replace(' - ',' ',1)

    # find all subtext that marking the end of the movie name part (e.g. DVDRIP 720P)
    for splitter in movie_title_splitter:
        tmp_pos = the_movie_name.lower().find(splitter.lower())
        if (tmp_pos >0 and (split_pos == 0 or tmp_pos < split_pos)):
                split_pos = tmp_pos

    if split_pos !=0:
        the_movie_name = the_movie_name[: split_pos]


    logging.info("\tDetected movie name: " + the_movie_name)
    return the_movie_name



# Get imdb details using local imdbpie library
# ==============================================================================

def get_imdb_details_by_search_via_imdbpie(search):

    try:
        imdb_search = imdb.search_for_title(search)
        if cfg.verbose:
            logging.debug(imdb_search)
        # only return the first result
        for imdb_object in imdb_search:
            if cfg.verbose:
                logging.debug(imdb_object)
            return imdb_object
            break
    except:
        return None



# Get imdb details using local imdbpie and second by rapidapi library
# ==============================================================================
def get_imdb_id_by_name(folderpath):

    imdb_id = None
    first_imdb_id = None
    second_imdb_id = None
    grabbed_imdb = False

    # no need to decode in python 3
    if sys.version_info.major != 3:
        folderpath = folderpath.decode("utf-8")

    folder, the_movie_name = os.path.split(folderpath)

    logging.info("\tFirst: Searching movie via imdbpie")
    search_name = get_clean_name_by_name(the_movie_name)
    first_imdb_object = get_imdb_details_by_search_via_imdbpie(search_name)

    if cfg.verbose:
        logging.debug(first_imdb_object)

    if first_imdb_object != None:
        first_imdb_id     = first_imdb_object.imdb_id
        imdb_id = first_imdb_id
        grabbed_imdb = True
        logging.info("\tFound imdb_movie_id: " + first_imdb_id)

    logging.info("\tSecond: Searching movie via rapidapi")
    second_imdb_object = get_imdb_details_by_search_via_rapidapi(search_name)

    if cfg.verbose:
        logging.debug(second_imdb_object)

    if second_imdb_object != None:
        second_imdb_id     = second_imdb_object['id']
        logging.info("\tFound imdb_movie_id: " + second_imdb_id)
        if grabbed_imdb == False:
            imdb_id = second_imdb_id
            grabbed_imdb = True

    # decide between the two imdb ids
    # if imdb ids are different choose the second_imdb_id

    if (first_imdb_id != None and second_imdb_id != None and
    first_imdb_id != second_imdb_id):
        imdb_id = first_imdb_id


    if imdb_id == None:
        logging.info("\tCannot grab imdb id from online IMDB data")

    return imdb_id




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
# ==============================================================================
def get_imdb_details_by_id_via_imdbpie(imdb_id):

    imdb_object = imdb.get_title(imdb_id)
    return imdb_object


# ==============================================================================
def get_imdb_details_by_search_via_rapidapi(search):


    logging.info("\tGet IMDB details by search via rapidapi: " + search)

    url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/search/" + search

    headers = {
        'x-rapidapi-key': cfg.x_rapidapi_key,
        'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers)

    # get movie data from json
    data = json.loads(response.text)
    titles = data['titles']

    try:
        # get info for the first movie in the json
        for d in titles:
            logging.info("\tGot IMDB id: " + d['id'])
            return d
    except:
        return None

# get imdb object by search using rapidapi
# ==============================================================================
def get_imdb_details_by_id_via_rapidapi(imdb_id):

    logging.info("\tGet IMDB details by id via rapidapi: " + imdb_id)

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






# find single files and move them to folders
def fix_orphan_files(basepath):

    global video_extensions
    logging.info('\tFixing orphan files in: '+basepath)

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
        logging.info('\t=============================================================================')

        # create temp folder path
        file_path = os.path.join(basepath, file)
        tmp_folder_path = os.path.join(basepath, os.path.splitext(file)[0]+' '+str(time.time()))
        os.mkdir(tmp_folder_path)

        # move file to temp folder
        os.rename(os.path.join(basepath, file),os.path.join(tmp_folder_path, file))
        logging.info('\tMoved video file to: ' + file)

        for extra_file in extra_files:
            if extra_file != file and extra_file not in video_files_grabbed:
                os.rename(os.path.join(basepath, extra_file),os.path.join(tmp_folder_path, extra_file))
                logging.info('\tMoved extra file: '+extra_file)


        # rename tmp folder
        new_folder_path = os.path.join(basepath, os.path.splitext(file)[0])
        try:
            os.rename(tmp_folder_path, new_folder_path)
        except:
            os.rename(tmp_folder_path, new_folder_path+' '+str(time.time()))


        logging.info('\tCreated new movie folder: '+new_folder_path)

# process files in folderpath
# if nfo is found, parse it for IMDB link
# if no imdb link is found add one
# if no nfo is found create one

def process_movie_folder(folderpath):

    video_file_name = ""
    imdb_id = ""
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

    # if folder is special ### type just ignore it
    if cfg.ignore_special_folders:
        tfolder, tname = os.path.split(folderpath)
        if tname[: 2] == '# ' or tname[: 2] == '! ':
            logging.info("\tFound special "+tname[: 2]+" folder path. Exiting without processing it.")
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
                    logging.info('\tFound video file: '+file)
                    found_video = True
                else:
                    found_multiple_videos = True

    if found_video == False:
        logging.warning('\tNo video file found!')

    if found_multiple_videos == True:
        logging.warning('\tMultimple video files found!')

    # GET NFO FILE !!!
    # now check all files in the folder for nfo file

    for file in os.listdir(folderpath):

        os.chdir(folderpath)

        # one nfo file is enough
        if found_nfo == True:
            found_nfo_duplicate = True
            logging.warning('\tWarning: Found multiple nfo files!')
            break

        if file.endswith('.nfo') and not file.startswith('.'):

            found_nfo = True
            nfo_file = file
            logging.info('\tFound nfo file: '+file)

            # get nfo file contents
            filepath = os.path.join(folderpath, file)

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
                            break


            if (imdb_link != ""):
                found_imdb = True
                logging.info("\tFound nfo IMDB link: "+imdb_link)
                logging.info("\tFound nfo IMDB id: "+imdb_id)



    # if no video and no nfo and no xml then Exiting

    if (found_video == False and found_imdb == False):
        logging.warning("\tNo video, no imdb in nfo: just rename to !!! and exit ")


    # GRABBING IMDB_ID !!!
    # done processing nfo file
    # if no IMDB data was found in nfo try to find it online
    # only if video file exists
    # even if the imdb_id was already found in nfo, perform the search anyway
    # in order to later compare the results

    if found_video == True:

        # grab IMDB link by folder name
        logging.info("\tSearching IMDB link by folder name: "+folderpath)
        movie_id_by_folder = get_imdb_id_by_name(folderpath)

        # grab IMDB link by file name

        if found_video == True:
            logging.info("\tSearching IMDB link by file name: "+video_file_name)
            movie_id_by_file = get_imdb_id_by_name(video_file_name)

        # compare two movie ids

        if movie_id_by_folder != None:
            grabbed_imdb_id = movie_id_by_folder
            grabbed_imdb = True
        else:
            if movie_id_by_file!= None:
                grabbed_imdb_id = movie_id_by_file
                grabbed_imdb = True
            else:
                grabbed_imdb = False

        if movie_id_by_folder!= movie_id_by_file:
            logging.warning("\tWarning! Grabbed different IMDB ids from folder and file: ")
            if movie_id_by_folder != None:
                logging.info("\t"+movie_id_by_folder+' '+folderpath)
            if movie_id_by_file != None:
                logging.info("\t"+movie_id_by_file+' '+video_file_name)
            grabbed_imdb_uncertain = True



    if imdb_id and grabbed_imdb_id:
        if imdb_id != grabbed_imdb_id:
            imdb_uncertain = True
            logging.warning("\tWARNING! Online grabbed IMDB id <> nfo found IMDB id !!!")


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
            logging.info("\tGrabbed IMDBpie code: " + imdb_id)
            logging.info("\tGrabbed IMDBpie link: " + imdb_link)
            logging.info("\tGrabbed IMDBpie title: " + imdb_title)


        imdb_title_en = ""

        if imdb_object_tmdb != None:
            tmdb_title_en = imdb_object_tmdb['title']
            tmdb_title_en = tmdb_title_en.lstrip().rstrip()
            tmdb_title_original = imdb_object_tmdb['original_title']
            tmdb_title_original = tmdb_title_original.lstrip().rstrip()
            logging.info("\tGrabbed tmdb english title: " + tmdb_title_en)
            logging.info("\tGrabbed tmdb original title: " + tmdb_title_original)

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


        if ('<movie>' in nfo):

            if cfg.verbose:
                logging.debug("NFO FILE:--------")
                logging.debug(nfo)
            # check if <movie> xml exists!
            regex = "<movie>[\s\S]*?<\/movie>"
            matches = re.findall(regex, nfo)

            for old_xml in matches:
                logging.info("\tGreat news: Found movie XML tags in nfo !!!")
                if found_xml != True:
                    found_xml = True

                else:
                    found_multiple_xml = True
                    logging.warning("\tBad news: Found multiple movie XML tags in nfo !!!")


        if (found_xml == False):

            logging.warning('\tnfo file without movie XML info !!!')
            # edit nfo file and add <movie><tag> info

            logging.info("\tAdding movies XML to existing nfo file: " + os.path.basename(filepath))
            # open the input file in write mode
            # write xml in front of the nfo text
            f = open(filepath, "wt")
            nfo = the_xml + '\n' + nfo
            f.write(nfo)
            f.close()

        else:

            # first check if force rewrire is enabled
            if (cfg.force_rewrite_xml == True):

                logging.info("\tUpdating movie XML to existing nfo file: " + os.path.basename(filepath))
                #open the input file in write mode
                f = open(filepath, "wt")
                #overrite the input file with the resulting data
                nfo = nfo.replace(old_xml, the_xml)
                f.write(nfo)
                #close the file
                f.close()

    else:

        if found_video:

            # no nfo file found, try to create one
            logging.info('\tCouldn\'t find nfo file. Creating new nfo file!')

            # rename
            pre, ext = os.path.splitext(video_file_name)
            nfo_file = os.path.join(folderpath, pre + '.nfo')
            f = open(nfo_file, "wt")
            f.write(the_xml)
            f.close()

            # no nfo file found, try to create one
            logging.info('\tWrote new nfo file:' + nfo_file)



    poster_file = "poster.jpg"

    # final cleanup
    # if nfo filename is different than the video file rename it
    if found_video:

        nfo_pre, nfo_ext = os.path.splitext(nfo_file)
        vid_pre, vid_ext = os.path.splitext(video_file_name)
        poster_file = vid_pre+'-poster.jpg'

        if (nfo_pre != vid_pre):

            old_nfo_path = os.path.join(folderpath, nfo_file)
            new_nfo_path = os.path.join(folderpath, vid_pre+'.nfo')
            nfo_file = vid_pre+'.nfo'
            logging.info('\tnfo and video file names are different: Renaming nfo')
            logging.info('\tfrom: ' + old_nfo_path)
            logging.info('\tto: ' + new_nfo_path)
            os.rename(old_nfo_path, new_nfo_path)


        if imdb_image:
            # download poster image to current folder
            pfolder, pname = os.path.split(imdb_image)
            r = requests.get(imdb_image, allow_redirects=True)
            open(poster_file, 'wb').write(r.content)
            logging.info("\tWriting poster file: "+pname)




    # time to rename the folder
    # renaming the movie folder
    # only if some video file exists !!!

    if not imdb_uncertain and found_video and (cfg.do_folder_renaming and (found_imdb or grabbed_imdb)):

        clean_name = imdb_title
        invalid = '<>:"/\|?*'
        for char in invalid:
	           clean_name = clean_name.replace(char, '')

        if sys.version_info.major != 3:
            clean_name = clean_name.encode("utf-8")

        clean_name = str(imdb_year)+' - '+str(clean_name)

        logging.info("\tTrying to rename: " + clean_name)


        video_resolution = get_movie_resolution(video_file_name)

        if video_resolution != None:
            clean_name += ' - ' + video_resolution
            logging.info("\tFound movie resolution by file: " + video_resolution)
        else:
            video_resolution = get_movie_resolution(os.path.basename(folderpath))
            if video_resolution:
                clean_name += ' - ' + video_resolution
                logging.info("\tFound movie resolution by folder: " + video_resolution)


        # get video file size and use it in folder name to mark lowres

        if cfg.do_mark_hires == True and video_resolution != None:
            video_path = os.path.join(folderpath, video_file_name)
            video_size = os.path.getsize(video_path)
            logging.info('\tvideo file size: ' + str(video_size))

            for key in video_file_hires_table:
                if key.lower() in video_resolution.lower():
                    hires = video_file_hires_table[key]
                    if video_size < hires:
                        clean_name += ' - LOWRES'
                    break


        folder, old_name = os.path.split(folderpath)
        new_folderpath = os.path.join(folder, clean_name)
        logging.info("\tFrom: " + folderpath)
        logging.info("\tTo: " + new_folderpath)


        # only if the paths are different !!!
        # try to rename the folder
        # if the folder already exists (duplicate movies)
        # add a timestamp at the end of the folder name

        if (folderpath != new_folderpath):


            folderpath_time = os.path.getmtime(folderpath)
            folderpath_time = datetime.fromtimestamp(folderpath_time)
            dt_string = folderpath_time.strftime("%Y-%m-%d %H%M%S")

            try:
                os.rename(folderpath, new_folderpath)
                r = True
            except:
                os.rename(folderpath, new_folderpath+' '+dt_string)


            #keep for next stage (movie rename)
            folderpath = new_folderpath

            logging.info('\tClean renaming enabled.')
            logging.info('\tRenamed movie folder to: '+new_folderpath)
        else:
            logging.info('\tNo need to rename folder: '+new_folderpath)



    # mark the folder with ### in the front of the name
    # if an empty nfo file was created
    # or if no XML tags were added
    # or
    # mark the folder with !!! in front of the name
    # if no video in folder
    # or if multiple video files were detected


    alerting = None

    if (found_nfo == False
        or found_imdb == False
        or found_xml == False):

        alerting = '# '

    if (found_video == False
        or found_multiple_videos == True
        or found_multiple_xml == True
        or found_multiple_nfo == True
        or found_broken_nfo == True
        or grabbed_imdb_uncertain == True
        or imdb_uncertain == True

        or (found_imdb == False and grabbed_imdb== False)):
            alerting = '! '

    if (cfg.do_folder_alerting and alerting):

        folder, old_name = os.path.split(folderpath)
        new_name = old_name
        if (old_name[0:2] != '# ' and old_name[0:2] != '! '):
            new_name = alerting+old_name
        new_folderpath = os.path.join(folder, new_name)


        # only if the paths are different !!!
        # try to rename the folder
        # if the folder already exists (duplicate movies)
        # add a timestamp at the end of the folder name

        if (folderpath != new_folderpath):

            try:
                os.rename(folderpath, new_folderpath)

            except:
                new_folderpath = new_folderpath+' '+str(time.time())
                os.rename(folderpath, new_folderpath)

            #keep for next stage (movie rename)
            folderpath = new_folderpath

            logging.warning('\tUnsafe changes made, renaming movie folder to: ' + new_folderpath)
        else:
            logging.info('\tNo need to rename folder: '+new_folderpath)



# process all folders in the given filepath


def process_all_folders(my_basedir):

    logging.info("\tProcessing movies folder: " + my_basedir)

    # start in basedir
    for fn in os.listdir(my_basedir):

        if not os.path.isdir(os.path.join(my_basedir, fn)):
            continue # Not a directory

        logging.info('\nFolder: \t' + fn)
        logging.info('\t=============================================================================')
        # search for NFO file
        folderpath = os.path.join(cfg.basedir, fn)
        process_movie_folder(folderpath)

# Now let's do someting cool

try:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(cfg.logging_file),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger()
    if cfg.verbose:
        logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    logging.info('\tThe Organizer (python 3.7 script)')
    logging.info('\t'+datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    logging.info('\tProcessing movies folder: '+cfg.basedir+'\n')


    # testing
    #get_imdb_list_movies(None)
    # just testing
    #get_imdb_user_lists(cfg.imdb_user_id)
    #logging.debug(get_imdb_list_movies('ls098426190'))

    #rint(get_imdb_details_by_id_via_imdbpie('tt0050976'))
    #logging.info(get_imdb_details_by_id_via_rapidapi('tt0050976'))
    # logging.info(imdb_list_array)
    # the_tags = get_movie_tags('tt0064276')
    # logging.info(the_tags)

    #logging.info(get_imdb_id_by_name('The Pink Panther'))



    # init_tmdb()
    # get_imdb_details_by_id_via_tmdb('tt0053134')

    #get_imdb_details_by_search_via_tmdb('diaboliques')


    # find all files outside folders and move them to nicely named folders
    fix_orphan_files(cfg.basedir)

    # first we have to grab all user movies from lists / categories
    # will use this later for tags
    get_imdb_user_movies(cfg.imdb_user_id)

    # and now let's process and clean the movies folder
    process_all_folders(cfg.basedir)




except Exception as e:
    errors = True
    logging.info('[ERROR] %s' % e)
    traceback.print_exc()
