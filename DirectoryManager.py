# Directory Manager
# Author: Tristan Sebens 
# Contact: tristan.ng.sebens@gmail.com
import os
import BathyConfig


# Class used to manage the creation and administration of subdirectories. Each DirectoryManager maintains a single larger directory comprised of multiple subdirectories
# @param CurrentDirectory = The directory which this instance manages. Will contain a series of incrementally named subdirectories.
# @param FolderClassName = The default name of the subfolders. For example: If FolderClassName = 'shapes', then the subdirectories will be named 'shapes0', 'shapes1', 'shapes2', etc
# @param MaxFolderSize = The maximum size a folder can reach before a new one is created
class DirectoryManager( object ):
	# Initializer
    def __init__( self, Directory, FolderClassName=None, MaxFolderSize=None ):
		BathyConfig.ConditionalPrint( "Initializing DirectoryManager for %s. Max folder size is %s", ( Directory, MFS ) )
		self.DirectoryCounter = 0
		self.FolderClassName = FolderClassName
		self.Directory = Directory
		self.CurrentSubdirectory = os.path.join( self.Directory, FolderClassName + str( self.DirectoryCounter) )
		if MaxFolderSize == None: # If the maximum folder size wasn't specified, then we'll simply use the default as specified by BathyConfig
			self.MaxFolderSize = BathyConfig.MAX_FOLDER_SIZE
		else:
			self.MaxFolderSize = MaxFolderSize
		if self.FolderClassName != None:	
			self.MakeNewSubdirectory()
		
    # Returns the size of the current subdirectory    
    def GetCurrentSubdirectorySize( self ):
		return os.path.getsize( self.CurrentSubdirectory )
    
    # Create a new subdirectory to create files in. Automatically generates a unique name 
    def MakeNewSubdirectory( self ):
		BathyConfig.ConditionalPrint( "Creating new subdirectory in %s", self.Directory )
		self.CurrentSubdirectory = os.path.join( self.Directory, self.FolderClassName + str( self.DirectoryCounter ) ) # Generate a unique name for the new subdirectory
		self.DirectoryCounter += 1
		try:
			os.mkdir( self.CurrentSubdirectory )
			BathyConfig.ConditionalPrint( "Directory No.%s created successfully in %s.", ( self.DirectoryCounter - 1, self.Directory ) )
		except: # The directory already exists. TODO: Should be specific to a FileExistsError
			BathyConfig.ConditionalPrint( "Subdirectory already exists! Checking to see if directory is over size limit." )
			BathyConfig.ConditionalPrint( "Current subdirectory size for %s is %s.\nMax folder size is %s", ( self.Directory, os.path.getsize( self.CurrentSubdirectory ), self.MaxFolderSize ) )

			if self.GetCurrentSubdirectorySize() > self.MaxFolderSize: # If the directory already exists, we should first check to see if it's too big. If it isn't there's no need to make a new one
				BathyConfig.ConditionalPrint( "Directory too big. Creating new directory in %s", self.Directory )
				self.MakeNewSubdirectory() # If it is too big, however, then we do need to make a new one.
			else:
				BathyConfig.ConditionalPrint( "Current directory within limit. No need to make a new one." ) 	
        
    # Returns a directory to create files in. First checks to see if the current subdirectory has exceeded the MaxFolderSize.
    # If it has, then a new subdirectory is created, and that is the directory that is returned.
    def GetDirectory( self ):
        if self.GetCurrentSubdirectorySize() > self.MaxFolderSize:
            self.MakeNewSubdirectory()
        return self.CurrentSubdirectory

    # Returns a list of all files held in the directory tree managed by this DirectoryManager
    # @param EXTENSION = An optional parameter which allows you to specify an extension. If you do, only files with the specified extension will be returned
    def GetAllFiles( self, EXTENSION=None ):
		return FindFiles( self.Directory, EXTENSION )
		
			

# Given a filename, this method returns a filepath for a file with that name, such that the file is being written to the correct directory (according to those rules governing 
# directory creation for this particular instance of DirectoryManager)
def CreateFilePath( self, filename ):
    return os.path.join( self.GetDirectory, filename )

def GetDirectoryManagerForDirectory( Directory, FolderClassName, MaxFolderSize=None ):
    if os.path.isdir( Directory ):
        pass
    else:
        os.mkdir( Directory )
    DM = DirectoryManager( Directory, FolderClassName, MaxFolderSize )
    return DM

# Method that walks through a file tree recursively, looking for files.
# It then returns a list containing all files in the directory tree
# @param root = The root of the file tree to search through
# @param ext = Optional parameter. If you specify an extension, only files with that extension will be returned.
def FindFiles( root, ext=None ):
    AllFiles = os.walk( root, True, None, False )
    ReturnFiles = list()

    for entry in AllFiles:
        # entry is a tuple containing (path, directories, files)
        for file in entry[2]:
            ( layername, extension ) = os.path.splitext( file )
            if ext != None:
                if extension == ext:
                    ReturnFiles.append( os.path.join( entry[0], file ) )
            else:
                ReturnFiles.append( os.path.join( entry[0], file ) )
                
    return ReturnFiles

""" For some reason, python thinks that this method is a part of the method above it. I'll deal with this later.
	# Returns a list of all files under the jurisdiction of this DirectoryManager which have the same name as the given name
	# Used to find all files associated with a Shapefile
	def GetFilesByName( self, name ):
		BathyConfig.ConditionalPrint( "Finding all files of name %s in %s.", ( name, self.Directory ) )
		AllFiles = self.GetAllFiles()
		ReturnFiles = list()
		for file in AllFiles:
			( INPUT_DIRECTORY, FILE ) = INPUT.rsplit( os.sep, 1 ) # Split the input path into the filename, and the file's directory
			( FILE_NAME, EXTENSION ) = os.path.splitext( FILE )
			if FILE_NAME == name:
				ReturnFiles.append( file )
		return ReturnFiles
"""		