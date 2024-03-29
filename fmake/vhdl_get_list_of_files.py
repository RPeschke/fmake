import os
import fnmatch, re
from fmake.generic_helper import  vprint
from pathlib import Path



def getListOfFiles(dirName, Pattern = '*.*',CaseSensitive=False):
    # create a list of file and sub directories 
    # names in the given directory 
    regex = fnmatch.translate(Pattern)
    Include_regEX = re.compile(regex)
    listOfFile = os.listdir(dirName)

    allFiles = list()
    file_path = Path(dirName + '/.fmakeignore')
    if file_path.exists():
        vprint(5)(".fmakeignore found in  ", dirName)
        return allFiles
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        fullPathUnix = fullPath.replace("\\","/")
        fullPathUnix_com = fullPathUnix
        if CaseSensitive == False:
            fullPathUnix_com = fullPathUnix.lower()
            Pattern =Pattern.lower()
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath,Pattern, CaseSensitive)
        elif Include_regEX.match(fullPathUnix_com) :
            allFiles.append(fullPathUnix)
                
    return allFiles