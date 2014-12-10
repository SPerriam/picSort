#!/Users/gramasamy/virtualenv/pSort/bin/python

# to execute this script from anywhere
import sys, os
sys.path.append('/Users/gramasamy/djcode/ngsdb03/')
import time
from os import path
from collections import defaultdict
from os.path import basename
####################################################################
#
# Functions
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
# main
#
####################################################################
args = argparse()
basepath = args.basepath
print basepath

from os import walk
import imghdr
import md5

def get_filetype(filepath):
    fileType = imghdr.what(filepath)
    if not fileType:
        fileType = "notImage"
    return fileType

import hashlib
def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()

import exifread
def get_exif_value(fullFilePath, exifKey):
    # Open image file for reading (binary mode)
    file = open(fullFilePath, 'rb')
    tags = exifread.process_file(file, details=False, stop_tag=exifKey.split(" ")[1])
    if exifKey in tags:
        return (tags[exifKey])
    else:
        return "NoValueExist"

def isduplicate(path1, path2):
    file1 = open(path1, 'rb')
    file2 = open(path2, 'rb')
    tags1 = exifread.process_file(file1, details=False)
    tags2 = exifread.process_file(file2, details=False)
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
    #print(tags1['EXIF DateTimeOriginal'], tags2['EXIF DateTimeOriginal'])
    #print(tags2['EXIF DateTimeOriginal'])
    #if tags1['EXIF DateTimeOriginal'] != tags2['EXIF DateTimeOriginal']:
    #    areTheySame = 'NO'

    return areTheySame

f = []
for (dirpath, dirnames, filenames) in walk(basepath):
    for filename in filenames:
        fullFilePath = os.path.join(dirpath, filename)
        f.append(fullFilePath)

data = defaultdict(dict)

for fullFilePath in f:
    #print fullFilePath
    fullFileType = get_filetype(fullFilePath)
    sha = hashfile(open(fullFilePath, 'rb'), hashlib.sha256())
    dateOriginal = "NA"
    dateDigitized = "NA"
    if fullFileType != 'notImage':
        dateOriginal = get_exif_value(fullFilePath, 'EXIF DateTimeOriginal')
        dateDigitized = get_exif_value(fullFilePath, 'EXIF DateTimeDigitized')
        #print(dateOriginal)
        #print(dateDigitized)
        #print(fullFileType)
        #print(type(dateOriginal))
        data[fullFilePath]['sha']=sha
        data[fullFilePath]['dateOriginal']=dateOriginal
        data[fullFilePath]['dateDigitized']=dateDigitized
        data[fullFilePath]['fullFileType']=fullFileType
        data[fullFilePath]['fileSize']=os.path.getsize(fullFilePath)
        data[fullFilePath]['fileName']=os.path.basename(fullFilePath)


# Create duplicate bin if not there already
if not os.path.exists(args.duplicatebin):
    os.makedirs(args.duplicatebin)

#find duplicates
import shutil
seen = defaultdict(dict)
for path, exifdic in data.items():
    sha = data[path]['sha']
    if sha in seen:
        reallyDuplicate = isduplicate(path, seen[sha])
        if reallyDuplicate == 'YES':
            print("duplicate:%s=>%s;%s=>%s" %(os.path.basename(path), os.path.basename(seen[sha]), path, seen[sha]))
            shutil.copy(path, args.duplicatebin)
            shutil.copy(seen[sha], args.duplicatebin)
    else:
        seen[sha]=path
