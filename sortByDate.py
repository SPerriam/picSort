#!/Users/gramasamy/virtualenv/pSort/bin/python
# author: Gowthaman Ramasamy
# contact:
# to execute this script from anywhere
import sys, os
sys.path.append('/Users/gramasamy/djcode/picSort/')
import time
from os import path
from os import walk
from os.path import basename
from collections import defaultdict

import shutil
import argparse
import imghdr
import hashlib
import exifread
import datetime
####################################################################
#
# Argument handling
#
####################################################################
def argparse():
    import argparse
    parser = argparse.ArgumentParser(description='Uploads Expression Analysis data to Experiment model and its pals.')
    parser.add_argument('--basepath',  required=True, help='Base path for the parent directory which contains all the pictures.\n')
    parser.add_argument('--destination',  required=True, help='Base path for the directory to place sorted files\n')
    parser.add_argument('--debug', required=False, default=False, type=bool)
    parser.add_argument('--version', '-v',  action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    return args


####################################################################
#
# functions
#
####################################################################
args = argparse()
basepath = args.basepath
destination = args.destination
print basepath
print destination

def get_filetype(filepath):
    '''
    finds file type
    :param filepath: full path of an file
    :return: type of the image file. If not an image file return "notImage"
    '''
    fileType = imghdr.what(filepath)
    if not fileType:
        fileType = "notImage"
    return fileType

def get_exif_value(fullFilePath, exifKey):
    '''
    gets the value for an exif tag (for an image file)
    :param fullFilePath: input file path
    :param exifKey: the exif tag for which values need to be parsed
    :return: value for the exif tag; TagNotFound if that is not found.
    '''
    # Open image file for reading (binary mode)
    file = open(fullFilePath, 'rb')
    tags = exifread.process_file(file, details=False, stop_tag=exifKey.split(" ")[1])
    if exifKey in tags:
        return (tags[exifKey])
    else:
        return "TagNotFound"

####################################################################
#
# main
#
####################################################################

'''create a lits of absolute paths for all the file under a base directory'''
filePaths = []
for (dirpath, dirnames, filenames) in walk(basepath):
    for filename in filenames:
        fullFilePath = os.path.join(dirpath, filename)
        filePaths.append(fullFilePath)

data = defaultdict(dict)

'''Create a folder for "un dated" pictures'''
undatedDir = os.path.join(args.destination, "undatedPictures")
if not os.path.exists(undatedDir):
    os.makedirs(undatedDir)


'''collect file attributes for each of the files (path)'''
for fullFilePath in filePaths:
    fullFileType = get_filetype(fullFilePath)
    dateOriginal = "NA"
    dateDigitized = "NA"
    if fullFileType != 'notImage':
        if get_exif_value(fullFilePath, 'EXIF DateTimeOriginal') != "TagNotFound":
            dated = datetime.datetime.strptime(str(get_exif_value(fullFilePath, 'EXIF DateTimeOriginal')), '%Y:%m:%d %H:%M:%S')
            #if not dated:
            #    dated = datetime.datetime.strptime(str(get_exif_value(fullFilePath, 'EXIF DateTimeDigitized')), '%Y:%m:%d %H:%M:%S')

            '''Create duplicate bin if not there already'''
            destinationDir = os.path.join(args.destination,  str(dated.year), str(dated.month).zfill(2), str(dated.day).zfill(2))
            if not os.path.exists(destinationDir):
                os.makedirs(destinationDir)
            shutil.copy(fullFilePath, destinationDir)

        else:
            '''copy to 'undated' folder'''
            shutil.copy(fullFilePath, undatedDir)
