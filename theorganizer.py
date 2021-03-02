## The Organizer
## A python movie collection organiser
## by Rares Dragan (www.raresdragan.com) (https://github.com/raresdragan)

import os
import re

import sys
import traceback
import requests
import json

import imdbpie

import config as cfg

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
                            ,'DVDrip'
                            ,'DVD-R'
                            ,'Webrip'
                            ,'PROPER'
                            ,'REMASTERED'
                            ,'dvdrip'
                            ,'Eng'
                            ,'_'
                            ,' - '
                            ]
movie_title_resolutions    = {'2160p': '2160p'
                            ,'1080i': '1080p'
                            ,'1080p': '1080p'
                            ,'1080': '1080p'
                            ,'720p': '720p'
                            ,'4k': '2160p'
                            ,'BluRay': '1080p'
                            ,'Blu-Ray': '1080p'
                            ,'BRRIP': '1080p'
                            ,'BDRIP': '1080p'
                            ,'DVDrip': '480p'
                            ,'DVD-R': '480p'
                            ,'WEBrip': '480p'
                            }

# setup imdb connection via imdbpie

from imdbpie import ImdbFacade
imdb = ImdbFacade()


# get a decently clean movie title from a messy release folder names
# ==============================================================================


def get_movie_resolution(video_file_name):


    for key in movie_title_resolutions:
        if key.lower() in video_file_name.lower():
            return movie_title_resolutions[key]
            break

    return

# get a decently clean movie title from a messy release folder names
# ==============================================================================

def get_name_by_folder(folderpath):

    folderpath = folderpath.decode("utf-8")
    folder, the_movie_name = os.path.split(folderpath)

    for replacer in movie_title_specials:
        the_movie_name = the_movie_name.replace(replacer, ' ')

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

    print("\tDetected movie name: " + the_movie_name.encode("ascii", errors="ignore"))
    return the_movie_name



# Get imdb details using local imdbpie library
# ==============================================================================

def get_imdb_details_by_search_via_imdbpie(search):

    try:
        imdb_search = imdb.search_for_title(search)
        if cfg.verbose:
            print(imdb_search)
        # only return the first result
        for imdb_object in imdb_search:
            if cfg.verbose:
                print(imdb_object)
            return imdb_object
            break
    except:
        return None


# Get imdb details using local imdbpie library
# ==============================================================================
def get_imdb_details_by_id_via_imdbpie(imdb_id):

    imdb_object = imdb.get_title(imdb_id)
    return imdb_object


# ==============================================================================
def get_imdb_details_by_search_via_rapidapi(search):


    print("\tGet IMDB details by name: " + search.encode("utf-8"))

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
            print("\tGot IMDB id: " + d['id'])
            return d
    except:
        return None

# get imdb object by search using rapidapi
# ==============================================================================
def get_imdb_details_by_id_via_rapidapi(imdb_id):

    print("\tGet IMDB details by id: " + imdb_id)

    url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/" + imdb_id

    headers = {
        'x-rapidapi-key': cfg.x_rapidapi_key,
        'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers)

    print(response.text)

    # get movie data from json
    data = json.loads(response.text)

    try:
        return data

    except:
        return None


# process files in folderpath
# if nfo is found, parse it for IMDB link
# if no imdb link is found add one
# if no nfo is found create one

def process_movie_folder(folderpath):

    video_file_name = ""
    imdb_id = ""
    imdb_link = ""
    imdb_title = ""
    imdb_image = ""
    imdb_year = ""
    found_nfo = False
    found_xml = False
    found_video = False
    found_imdb = False
    found_many_videos = False
    grabbed_imdb = False


    # if folder is special ### type just ignore it
    if cfg.ignore_special_folders:
        tfolder, tname = os.path.split(folderpath)
        if tname[: 3] == "###":
            print("\tFound special "+tname[: 3]+" folder path. Exiting without processing it.")
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
            if (file.endswith(extension) and not file.startswith('.')):
                if found_video != True:
                    video_file_name = file
                    print('\tFound video file: '+file)
                    found_video = True
                else:
                    found_many_videos = True

    if found_video == False:
        print('\tNo video file found!')

    if found_many_videos == True:
        print('\tMultimple video files found!')

    # GET NFO FILE !!!
    # now check all files in the folder for nfo file
    for file in os.listdir(folderpath):

        os.chdir(folderpath)

        # one nfo file is enough
        if found_nfo == True:
            break

        if file.endswith('.nfo') and not file.startswith('.'):

            found_nfo = True
            nfo_file = file
            print('\tFound nfo file: '+file)

            # get nfo file contents
            filepath = os.path.join(folderpath, file)

            # reding nfo file content
            with open(filepath) as f:
                nfo = f.read()

            # check for IMDB link and IMDB code in file
            if ('imdb' in nfo) or ('IMDB' in nfo):

                # regexp searching for something like http://www.imdb.com/title/tt0064030
                regex = "\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"

                imdb_link = ""
                matches = re.findall(regex, nfo)
                for match in matches:
                    if ('imdb' in match):
                        imdb_link = match

                        # get IMDB code from IMDB link
                        tmp_index=imdb_link.rfind('/')
                        length = len(imdb_link)
                        imdb_id=imdb_link[tmp_index+1 :]


            if (imdb_link != ""):
                found_imdb = True
                print("\tFound IMDB link: "+imdb_link)
                print("\tFound IMDB code: "+imdb_id)


    # done processing nfo file
    # if no IMDB data was found in nfo try to find it online
    if found_imdb == False:

        # this is the fun part
        # grab IMDB link by folder name
        print("\tSearching IMDB link by folder name: "+folderpath)

        search_name = get_name_by_folder(folderpath)
        imdb_object = get_imdb_details_by_search_via_imdbpie(search_name)

        print(imdb_object)
        if imdb_object != None:
            imdb_id     = imdb_object.imdb_id
            grabbed_imdb = True
        else:
            print("\tFirst IMDB search failed. Trying second search method via API")
            imdb_object = get_imdb_details_by_search_via_rapidapi(search_name)
            if imdb_object != None:
                imdb_id     = imdb_object['id']
                grabbed_imdb = True
            else:
                grabbed_imdb = False
                print("\tCannot grab online IMDB data")



    # if i have the imdb_id then let's get more info

    if found_imdb or grabbed_imdb:

        imdb_object = get_imdb_details_by_id_via_imdbpie(imdb_id)

        if imdb_object != None:
            imdb_id     = imdb_object.imdb_id
            imdb_title  = imdb_object.title
            imdb_link   = 'https://www.imdb.com/title/'+imdb_id+'/'
            if imdb_object.image:
                imdb_image  = imdb_object.image.url
            imdb_year   = imdb_object.year
            # remember to mark grabbed_imdb = True
            # not sure grabbed info is correct so force a manual check
            print("\tGrabbed IMDB code: "+imdb_id)
            print("\tGrabbed IMDB link: "+imdb_link)




    # prepare the tags
    the_tags = "\n<tag>THE SPECIAL</tag>"

    # prepare the xml code with IMDB and tags and everything

    the_xml = "<movie>"
    the_xml += "\n<imdb>"+imdb_link+"</imdb>"
    the_xml += "\n<uniqueid type=\"\" default=\"true\">"+imdb_id+"</uniqueid>"
    if imdb_title != "":
        the_xml += "\n<title>"+imdb_title+"</title>"
    if imdb_year !="":
        the_xml += "\n<year>"+str(imdb_year)+"</year>"
    if the_tags != "":
        the_xml += the_tags
    the_xml += "\n</movie>"
    the_xml = the_xml.encode('utf-8').strip()


    # writing to nfo file
    # check for <movie> and <tag>
    # file exists
    if found_nfo == True:


        if ('<movie>' in nfo) and ('<tag>' in nfo):

            # check if <movie> xml exists!
            regex="<movie>[\s\S]*?<\/movie>"
            matches = re.findall(regex, nfo)

            for old_xml in matches:
                    found_xml = True
                    print("\tFound movie XML tags in nfo")


        if (found_xml == False):

            print('\tnfo file without movie XML info !!!')
            # edit nfo file and add <movie><tag> info

            print("\tAdding movies XML to existing nfo file: " + os.path.basename(filepath))
            # open the input file in write mode
            # write xml in front of the nfo text
            f = open(filepath, "wt")
            nfo = the_xml + '\n' + nfo
            f.write(nfo)
            f.close()

        else:

            # first check if force rewrire is enabled
            if (cfg.force_rewrite_xml == True):

                print("\tUpdating movie XML to existing nfo file: " + os.path.basename(filepath))
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
            print('\tCouldn\'t find nfo file. Creating new nfo file!')

            # rename
            pre, ext = os.path.splitext(video_file_name)
            nfo_file = os.path.join(folderpath, pre + '.nfo')
            f = open(nfo_file, "wt")
            f.write(the_xml)
            f.close()

            # no nfo file found, try to create one
            print('\tWrote new nfo file:' + nfo_file)



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
            print('\tnfo and video file names are different: Renaming nfo')
            print('\tfrom: ' + old_nfo_path)
            print('\tto: ' + new_nfo_path)
            os.rename(old_nfo_path, new_nfo_path)


    if imdb_image:
        # download poster image to current folder
        pfolder, pname = os.path.split(imdb_image)
        r = requests.get(imdb_image, allow_redirects=True)
        open(poster_file, 'wb').write(r.content)
        print("\tWriting poster file: "+pname)




    # time to rename the folder

    # renaming the movie folder


    if (cfg.do_folder_renaming and (found_imdb or grabbed_imdb)):

        clean_name = imdb_title
        invalid = '<>:"/\|?*'
        for char in invalid:
	           clean_name = clean_name.replace(char, '')
        #clean_name = re.sub(r'[^\w\s-]', '', clean_name)
        clean_name = clean_name.encode("utf-8")
        clean_name = str(imdb_year)+' - '+clean_name

        print("try to rename: " + clean_name)
        if video_file_name:
             clean_name += ' - '+get_movie_resolution(video_file_name)

        folder, old_name = os.path.split(folderpath)
        new_folderpath = os.path.join(folder, clean_name)
        print(folderpath)
        print(new_folderpath)
        os.rename(folderpath, new_folderpath)
        #keep for next stage (movie rename)
        folderpath = new_folderpath

        print('\tClean renaming enabled.')
        print('\tRenamed movie folder to: '+clean_name)


    # mark the folder with ### in the front of the name
    # if an empty nfo file was created
    # or if no XML tags were added
    # or if multiple video files were detected


    if (cfg.do_folder_alerting and (found_video == False or found_nfo == False or found_imdb == False or found_xml == False or found_many_videos == True)):

        folder, old_name = os.path.split(folderpath)
        new_name = old_name
        if (old_name[0:3] != '###'):
            new_name = "### "+old_name
        new_folderpath = os.path.join(folder, new_name)
        os.rename(folderpath, new_folderpath)
        #keep for next stage (movie rename)
        folderpath = new_folderpath

        print('\tUnsafe changes made, renaming movie folder to: ' + new_folderpath)




# process all folders in the given filepath


def process_all_folders(my_basedir):

    # start in basedir
    for fn in os.listdir(my_basedir):

        if not os.path.isdir(os.path.join(my_basedir, fn)):
            continue # Not a directory

        print('\nMovie: \t' + fn)
        print('\t=============================================================================')
        # search for NFO file
        folderpath = os.path.join(cfg.basedir, fn)
        process_movie_folder(folderpath)

# Now let's do someting cool

try:

    print('The Organizer')
    print('by Rares Dragan')
    print('Processing movies folder: '+cfg.basedir+'\n')

    #get_name_by_folder("1997 - Ip-Man The history - Eine Stadt DVDrip sucht 1080P einen Morder 1931")

    # get_movie_resolution("1997 - Ip-Man The history - Eine Stadt DVDrip sucht 1080P einen Morder 1931")
    #get_imdb_details_by_search_via_imdbpie("1960 Spartacus")

    #process_movie_folder("/media/multimedia/movies_temp/1931 - M - Eine Stadt sucht einen Mrder - 1080p")

    process_all_folders(cfg.basedir)


except Exception as e:
    errors = True
    print('[ERROR] %s' % e)
    traceback.print_exc()
