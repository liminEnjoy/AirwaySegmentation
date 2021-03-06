#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
########################################################################################

from Common.ErrorMessages import *
import numpy as np
import shutil
import glob
import datetime
import time
import csv
import os
import re


# operations in working directory: mkdir, cp, mv...
def makedir(pathname):
    pathname = pathname.strip()
    pathname = pathname.rstrip("\\")
    isExists = os.path.exists(pathname)
    if not isExists:
        os.makedirs(pathname)
        return True
    else:
        return False

def removedir(pathname):
    os.remove(pathname)

def removefile(filename):
    os.remove(filename)

def makelink(filesrc, linkdest):
    os.symlink(filesrc, linkdest)

def realpathlink(filename):
    return os.path.realpath(filename)

def copydir(dirsrc, dirdest):
    shutil.copyfile(dirsrc, dirdest)

def copyfile(filesrc, filedest):
    shutil.copyfile(filesrc, filedest)

def movedir(pathsrc, pathdest):
    os.rename(pathsrc, pathdest)

def movefile(filesrc, filedest):
    os.rename(filesrc, filedest)

def joinpathnames(pathname, filename):
    return os.path.join(pathname, filename)

def basename(filename):
    return os.path.basename(filename)

def dirnamepathfile(filename):
    return os.path.dirname(filename)

def ospath_splitext_recurse(filename):
    #account for extension that are compound: i.e. '.nii.gz'
    basename, extension = os.path.splitext(filename)
    if extension == '':
        return (basename, extension)
    else:
        sub_basename, sub_extension = ospath_splitext_recurse(basename)
        return (sub_basename, sub_extension + extension)

def filenamenoextension(filename, use_recurse_splitext=True):
    if use_recurse_splitext:
        return ospath_splitext_recurse(basename(filename))[0]
    else:
        return os.path.splitext(filename)[0]

def filenamepathnoextension(filename, use_recurse_splitext=True):
    if use_recurse_splitext:
        return ospath_splitext_recurse(filename)[0]
    else:
        return os.path.splitext(filename)[0]

def filenameextension(filename, use_recurse_splitext=True):
    if use_recurse_splitext:
        return ospath_splitext_recurse(filename)[1]
    else:
        return os.path.splitext(filename)[1]
# ------------------------------------


# find files in working directory
def isExistdir(pathname):
    return os.path.exists(pathname)

def isExistfile(filename):
    return os.path.exists(filename)

def listFilesDir(pathname):
    listfiles = os.listdir(pathname)
    return [joinpathnames(pathname, file) for file in listfiles]

def listLinksDir(pathname):
    listfiles = listFilesDir(pathname)
    return [file for file in listfiles if os.path.islink(file)]

def findFilesDir(filenames):
    return sorted(glob.glob(filenames))

def findFilesDir(filespath, filenames):
    return sorted(glob.glob(joinpathnames(filespath, filenames)))

def findFilesDirAndCheck(filespath, filenames):
    listFiles = findFilesDir(filespath, filenames)
    num_files = len(listFiles)
    if (num_files == 0):
        message = 'no files \'%s\' found in dir \'%s\'' %(filenames, filespath)
        CatchErrorException(message)
    return listFiles
# ------------------------------------


# input / output data in disk
def readDictionary_numpy(filename):
    return np.load(filename).item()

def readDictionary_csv(filename):
    if filenameextension(filename, use_recurse_splitext=False) != '.csv':
        message = 'need \'.csv\' to save dictionary'
        CatchErrorException(message)
    else:
        with open(filename, 'r') as fin:
            reader = csv.reader(fin)
            return dict(reader)

def saveDictionary(filename, dictionary):
    saveDictionary_numpy(filename, dictionary)

def readDictionary(filename):
    return readDictionary_numpy(filename)

def saveDictionary_numpy(filename, dictionary):
    np.save(filename, dictionary)

def saveDictionary_csv(filename, dictionary):
    if filenameextension(filename, use_recurse_splitext=False) != '.csv':
        message = 'need \'.csv\' to save dictionary'
        CatchErrorException(message)
    else:
        with open(filename, 'w') as fout:
            writer = csv.writer(fout)
            for key, value in dictionary.items():
                writer.writerow([key, value])
# ------------------------------------


# manipulate / convert python data types
def isOddIntegerVal(val):
    return val % 2 == 1
def isEvenIntegerVal(val):
    return val % 2 == 0

def isBiggerTuple(var1, var2):
    return all((v_1 > v_2) for (v_1, v_2) in zip(var1, var2))

def isSmallerTuple(var1, var2):
    return all((v_1 < v_2) for (v_1, v_2) in zip(var1, var2))

def isEqualTuple(var1, var2):
    return all((v_1 == v_2) for (v_1, v_2) in zip(var1, var2))

def sumTwoTuples(var1, var2):
    return tuple(a+b for (a,b) in zip(var1, var2))

def substractTwoTuples(var1, var2):
    return tuple(a-b for (a,b) in zip(var1, var2))

def str2bool(strin):
    return strin.lower() in ('yes', 'true', 't', '1')

def str2tupleint(strin):
    return tuple([int(i) for i in strin.rsplit(',')])

def str2tuplefloat(strin):
    return tuple([float(i) for i in strin.rsplit(',')])

def list2str(list):
    return "_".join(str(i) for i in list)

def tuple2str(tuple):
    return "_".join(str(i) for i in list(tuple))

def splitListInChunks(list, sizechunck):
    listoflists = []
    for i in range(0, len(list), sizechunck):
        listoflists.append( list[i:i+sizechunck] )
    return listoflists

def flattenOutListOfLists(list):
    return reduce(lambda el1, el2: el1 + el2, list)

def mergeTwoListsIntoDictoinary(list1, list2):
    new_dict = {}
    map(lambda key, val: new_dict.update({key: val}), list1, list2)
    return new_dict

def findElementsSubstringInListStrings(list, pattern):
    return [elem for elem in list if pattern in elem]

def findCommonElementsTwoLists_Option1(list1, list2):
    if len(list1) == 0 or len(list2) == 0:
        return False
    elif type(list1[0]) != type(list2[0]):
        return False
    else:
        list_common_elems = []
        for elem1 in list1:
            if elem1 in list2:
                list_common_elems.append(elem1)
        #endfor
        return list_common_elems

def findCommonElementsTwoLists_Option2(list1, list2):
    if len(list1) == 0 or len(list2) == 0:
        return False
    elif type(list1[0]) != type(list2[0]):
        return False
    else:
        setlist1 = set([tuple(elem) for elem in list1])
        setlist2 = set([tuple(elem) for elem in list2])
        return list([elem for elem in setlist1 & setlist2])
# ------------------------------------


# timers
def getdatetoday():
    today = datetime.date.today()
    return (today.month, today.day, today.year)

def gettimenow():
    now = datetime.datetime.now()
    return (now.hour, now.minute, now.second)

class WallClockTime(object):
    def __init__(self):
        self.start_time = time.time()
    def compute(self):
        return time.time() - self.start_time
# ------------------------------------


# others util
def parseListarg(args):
    return args.replace('[','').replace(']','').split(',')

def getFileExtension(formatoutfile):
    if formatoutfile=='dicom':
        return '.dcm'
    elif formatoutfile=='nifti':
        return '.nii'
    elif formatoutfile=='nifti_gz':
        return '.nii.gz'
    elif formatoutfile=='numpy':
        return '.npy'
    elif formatoutfile=='numpy_gzbi':
        return '.npz'
    elif formatoutfile=='numpy_gz':
        return '.npy.gz'
    elif formatoutfile=='hdf5':
        return '.hdf5'
    else:
        return False

def getSubstringPatternFilename(filename, substr_pattern):
    return re.search(substr_pattern, filename).group(0)

def findFileWithSamePrefix(source_file, list_infiles, prefix_pattern=None):
    if not prefix_pattern:
        #find the pattern prefix in 'source_file'
        prefix = source_file.split('_')[0]
        prefix_pattern = ''.join(['[0-9]' if s.isdigit() else s for s in prefix])

    prefix_casename = getSubstringPatternFilename(source_file, prefix_pattern)
    for iterfile in list_infiles:
        if prefix_casename in iterfile:
            return iterfile
    #endfor
    message = 'not found file with same prefix in \'%s\' in list files: \'%s\'' %(source_file, list_infiles)
    CatchErrorException(message)

def findListFilesWithSamePrefix(source_file, list_infiles, prefix_pattern=None):
    if not prefix_pattern:
        #find the pattern prefix in 'source_file'
        prefix = source_file.split('_')[0]
        prefix_pattern = ''.join(['[0-9]' if s.isdigit() else s for s in prefix] + ['_'])

    prefix_casename = getSubstringPatternFilename(source_file, prefix_pattern)
    list_out_files = []
    for iterfile in list_infiles:
        if prefix_casename in iterfile:
            list_out_files.append(iterfile)
    #endfor
    if len(list_out_files)==0:
        message = 'not found files with same prefix in \'%s\' in list files: \'%s\'' % (source_file, list_infiles)
        CatchErrorException(message)
    else:
        return list_out_files

def getIndexOriginImagesFile(images_file, beginString='images', firstIndex='0'):
    pattern = beginString + '-[0-9]*'
    if bool(re.match(pattern, images_file)):
        index_origin = int(re.search(pattern, images_file).group(0)[-2:])
        return index_origin - int(firstIndex)
    else:
        return False
# ------------------------------------
