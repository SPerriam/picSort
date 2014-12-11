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

####################################################################
#
# Argument handling
#
####################################################################
def argparse():
    import argparse
    parser = argparse.ArgumentParser(description='Uploads Expression Analysis data to Experiment model and its pals.')
    parser.add_argument('--basepath',  required=True, help='Base path for the parent directory which contains all the pictures.\n')
    parser.add_argument('--duplicatebin',  required=True, help='Base path for the directory to dump the duplicates\n')
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
print basepath


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

def hashfile(afile, hasher, blocksize=65536):
    '''
    creates sha hash (aka md5) for a file
    :param afile: any file to get the sha (aka md5) value for
    :param hasher: algorithm to be used to generate the hash
    :param blocksize: read size
    :return: sha key for the file
    '''
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()

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

def isduplicate(path1, path2):
    '''
    checks if two files are same by several means
    :param path1: path for file 1
    :param path2: path for file 2
    :return: YES/NO
    '''

    areTheySame = 'YES'

    # is sha same
    sha1 = hashfile(open(path1, 'rb'), hashlib.sha256())
    sha2 = hashfile(open(path2, 'rb'), hashlib.sha256())
    if sha1 != sha2:
        areTheySame = 'NO'
    # is size same
    size1 = os.path.getsize(path1)
    size2 = os.path.getsize(path2)
    if size1 != size2:
        areTheySame = 'NO'

    # have same DateTimeOriginal
    # file1 = open(path1, 'rb')
    # file2 = open(path2, 'rb')
    # tags1 = exifread.process_file(file1, details=False)
    # tags2 = exifread.process_file(file2, details=False)
    # print(tags1['EXIF DateTimeOriginal'], tags2['EXIF DateTimeOriginal'])
    # print(tags2['EXIF DateTimeOriginal'])
    # if tags1['EXIF DateTimeOriginal'] != tags2['EXIF DateTimeOriginal']:
    #     areTheySame = 'NO'

    return areTheySame


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

'''collect file attributes for each of the files (path)'''
for fullFilePath in filePaths:
    fullFileType = get_filetype(fullFilePath)
    sha = hashfile(open(fullFilePath, 'rb'), hashlib.sha256())
    dateOriginal = "NA"
    dateDigitized = "NA"
    if fullFileType != 'notImage':
        dateOriginal = get_exif_value(fullFilePath, 'EXIF DateTimeOriginal')
        dateDigitized = get_exif_value(fullFilePath, 'EXIF DateTimeDigitized')
        data[fullFilePath]['sha']=sha
        data[fullFilePath]['dateOriginal']=dateOriginal
        data[fullFilePath]['dateDigitized']=dateDigitized
        data[fullFilePath]['fullFileType']=fullFileType
        data[fullFilePath]['fileSize']=os.path.getsize(fullFilePath)
        data[fullFilePath]['fileName']=os.path.basename(fullFilePath)


'''Create duplicate bin if not there already'''
if not os.path.exists(args.duplicatebin):
    os.makedirs(args.duplicatebin)

'''find duplicates'''
seen = defaultdict(dict)
for path, exifdic in data.items():
    sha = data[path]['sha']
    if sha in seen:
        reallyDuplicate = isduplicate(path, seen[sha])
        if reallyDuplicate == 'YES':
            ''' if duplicate copy all the files to duplicate bin'''
            print("duplicate:%s=>%s;%s=>%s" %(os.path.basename(path), os.path.basename(seen[sha]), path, seen[sha]))
            shutil.copy(path, args.duplicatebin)
            shutil.copy(seen[sha], args.duplicatebin)
    else:
        seen[sha]=path
