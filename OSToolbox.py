# OSToolbox
# Author: Tristan Sebens
# Contact: tristan.ng.sebens@gmail.com

import os

# Method that walks through a file tree recursively, looking for files with the specified extension.
# It then returns a list containing all files which mached the specified extension
# @param root = The root of the file tree to search through
# @param ext = The extension to look for
def FindFilesByExtension( root, ext ):
    AllFiles = os.walk( root, True, None, False )
    ReturnFiles = list()

    for entry in AllFiles:
        # entry is a tuple containing (path, directories, files)
        for file in entry[2]:
            ( layername, extension ) = os.path.splitext( file )
            if extension == ext:
                ReturnFiles.append( os.path.join( entry[0], file ) )

    return ReturnFiles
