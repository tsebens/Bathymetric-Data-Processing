# Process Bathymetric Data
# Main script for the larger program.
# TODO: Add logic to handle an improper shutdown. Specifically, finding the last file the system was editing, and rewriting it

import BathyConfig
import BathyToolbox
import OSToolbox
import Threader
import DirectoryManager
import shutil
import os
import time
import arcpy
import sys

# The root of the directory which the script will walk through looking for all raw data (raw data meaning all data which has yet to be used by this script)
INPUT_FILE_DIRECTORY_ROOT = BathyConfig.INPUT_ROOT_FOLDER

# The root directory where all intermediate file subdirectories will be held.
OUTPUT_DIRECTORY = BathyConfig.OUTPUT_ROOT_FOLDER

# Directories where intermediate files will be held
XYZ_HEADER_OUTPUT_DIRECTORY = os.path.join( OUTPUT_DIRECTORY, "XYZ_Headers_Added" ) # Where XYZ files will go after having headers added to them
SHAPEFILE_OUTPUT_DIRECTORY = os.path.join( OUTPUT_DIRECTORY, "Unprojected_Shapefiles" ) # Where Shapefiles processed from XYZ files will go
PROJ_OUTPUT_DIRECTORY = os.path.join( OUTPUT_DIRECTORY, "Projected_Shapefiles" ) # Where Shapefiles will go after being projected to the desired coordinate system
OL_OUTPUT_DIRECTORY = os.path.join( OUTPUT_DIRECTORY, "Outlier_Analysis_Performed" ) # Where Shapefiles will go after having an outlier analysis performed on them

UNPROJECTABLE_DIRECTORY = os.path.join( OUTPUT_DIRECTORY, "Unprojectable_Files" ) # Where Shapefiles go if they cannot be projected. For whatever reason
if os.path.isdir( UNPROJECTABLE_DIRECTORY ):
	pass
else:
	os.mkdir( UNPROJECTABLE_DIRECTORY )

INPUT_FILE_FORMAT = BathyConfig.INPUT_FILE_FORMAT

# The threading manager we will use to provide multi-threading capability
ThreadingManager = Threader.ThreadingManager( max=BathyConfig.MAX_ALLOWED_THREADS )

# Directory Managers. Used to make sure that the new files are arranged neatly and cleanly in their new directories
INPUTDirectoryManager = DirectoryManager.GetDirectoryManagerForDirectory( INPUT_FILE_DIRECTORY_ROOT )
XYZDirectoryManager = DirectoryManager.GetDirectoryManagerForDirectory( XYZ_HEADER_OUTPUT_DIRECTORY, FolderClassName="XYZHeader_" )
SHPDirectoryManager = DirectoryManager.GetDirectoryManagerForDirectory( SHAPEFILE_OUTPUT_DIRECTORY, FolderClassName="Shapefile_" )
PRJDirectoryManager = DirectoryManager.GetDirectoryManagerForDirectory( PROJ_OUTPUT_DIRECTORY, FolderClassName="Projected_To_AA_" )
OLDirectoryManager  = DirectoryManager.GetDirectoryManagerForDirectory( OL_OUTPUT_DIRECTORY, FolderClassName="Outliers_Removed_" )
# For each of the following methods, the DirectoryManager passed to the method should refer to the directory where the files will be processed to, not from

# Accepts a list of filepaths, and returns a list containing only the names of the files those paths pointed to.
# Containing directories and extensions are removed
def PruneDownToFilenames( list ):
	PrunedList = []
	for element in list:
		( FILE_DIRECTORY, FILE_NAME, FILE_EXTENSION ) = BathyToolbox.SplitFilePath( element )
		PrunedList.append( FILE_NAME )
	
	return PrunedList
	
# Accepts a pair of filepath lists, and removes from the first list all elements whose names appear in the second list
# Names do not have to be an exact match, the second list element only has to contain the first list element. Additional name tags can be present
def RemoveCommonElements( List1, List2 ):
	List1Copy = list(List1) # Workaround for shitty python logic
	for entry1 in List1Copy:
		for entry2 in List2:
			( ENTRY1DIR, ENTRY1NAME, ENTRY1EXT ) = BathyToolbox.SplitFilePath( entry1 )
			( ENTRY2DIR, ENTRY2NAME, ENTRY2EXT ) = BathyToolbox.SplitFilePath( entry2 )
			# This loop covers every possible pairing of elements between list 1 and 2
			if ENTRY1NAME in ENTRY2NAME:
				List1.remove( entry1 )
				BathyConfig.ConditionalPrint( "%s has already been processed." % ENTRY1NAME )
				break
	return List1

def ParseErrorCode( exception ):
	index = exception.find( "ERROR" ) + 6
	error_code = exception[index:index+6]
	return error_code

# An error of a type specified by ERROR_CODE has occurred while attempting to process File. Deal with it
def HandleGeoprocessingError( ERROR_CODE, File ):
	BathyConfig.ConditionalPrint( "Error code %s occurred while processing %s.", ( ERROR_CODE, File ) )
	
# Finds all entries in Files which have corresponding entries somewhere in the directory managed by DM and removes them from the list of files to be processed.
# Then calls Function on each entry of Files.
# Uses threading if activated by BathyConfig
def ProcessUnprocessedFiles( Function, Files, DM, EXT="" ):
	Files = RemoveCommonElements( Files, DM.GetAllFiles() ) # Remove from the list of files to be processed all those files which have already been processed
	for File in Files:
		# For each of the files in the passed list...
		( name, extension ) = os.path.splitext( File )
		if EXT != "" and EXT != extension:
			BathyConfig.ConditionalPrint( "%s is of the wrong format.", name )
			continue
        # Here we pass to the function the file we want processed, and the directory we want the file processed to via the DirectoryManager		
		BathyConfig.ConditionalPrint( "Now processing %s", File )
		try:
			if BathyConfig.USE_THREADING == True:
				StartThreadedProcess( Function, ( File, DM.GetDirectory() ) )
			else:
				Function( File, DM.GetDirectory() )
		except arcpy.ExecuteError:
			e = sys.exc_info()[1]
			ERROR_CODE = ParseErrorCode( e.args[0] )
			HandleGeoprocessingError( ERROR_CODE, File )
		except Exception:
			print( "Runtime error has occurred." )
			
	
# Add a header to all of the XYZ Files
# @param XYZFiles = A list of all XYZ Files to be processed. Expressed as filepaths
# @param XYZDM = The appropriate DirectoryManager
def AddHeadersToXYZFiles( XYZFiles, XYZDM ):
	BathyConfig.ConditionalPrint( "Adding headers to XYZFiles..." )
	ProcessUnprocessedFiles( BathyToolbox.AddHeaderToXYZFile, XYZFiles, XYZDM )
		
# Process the XYZFiles to Shapefiles
# @param XYZDM = The DirectoryManager for the directory containing all of the XYZ files with headers
# @param SHPDM = The DirectoryManager for the directory where all un projected shapefiles will be kept
def ProcessXYZFilesToShapefiles( XYZDM, SHPDM ):
	BathyConfig.ConditionalPrint( "Processing XYZ Files to Shapefiles..." )
	ProcessUnprocessedFiles( BathyToolbox.ProcessXYZtoShapefile, XYZDM.GetAllFiles(), SHPDM )

# Project the Shapefiles into the proper projection (Which projection to use is specified in BathyConfig)
# @param SHPDM = The DirectoryManager for the directory containing all of the unprojected Shapefiles
# @param PRJDM = The DirectoryManager for the directory where all projected shapefiles will be kept
def ProjectShapefiles( SHPDM, PRJDM ):
	BathyConfig.ConditionalPrint( "Projecting Shapefiles..." )
	ProcessUnprocessedFiles( BathyToolbox.ProjectShapefile, SHPDM.GetAllFiles(), PRJDM, EXT=".shp" )

# Function that repeatedly attempts to create a thread until it is successfully created
# Respects the maximum number of allowable threads
def StartThreadedProcess( Function, Args ):
    created = False
    while created == False: # Until the thread is successfully created, we must keep trying to create it. Periodically though, so as not to hog processor cycles
        try:
			BathyConfig.ConditionalPrint( "Attempting to create thread." )
			ThreadingManager.CreateNewFunctionThread( Function, Args )
			created = True # The thread has been created, so we can exit the while loop
			BathyConfig.ConditionalPrint( "Thread created." )
        except Exception as e: # TODO: Should be specific to a TooManyThreadsActive Exception
			BathyConfig.ConditionalPrint( "Too many threads active. Waiting for threads to finish." )
            # There are too many threads active at the moment, so we need to wait a while, and then try again.
			time.sleep( BathyConfig.WAIT_TIME_AFTER_THREAD_CREATION_FAILURE ) # Wait the amount of time specified by the BathyConfig file

# Main script ------------------------------------------------------------------>
# First we have to satisfy ESRI that we're not stealing from them
BathyToolbox.GetNecessaryLicenses()


# First, we generate a list of all files in the directory tree, rooted at INPUT_FILE_DIRECTORY_ROOT, which are of the specified format
XYZ_FILES = DirectoryManager.FindFiles( INPUT_FILE_DIRECTORY_ROOT, ext=".csv" ) # A list of file paths, each pointing to a separate file which we're going to process
SHP_FILES = DirectoryManager.FindFiles( INPUT_FILE_DIRECTORY_ROOT, ext=".shp" )

AddHeadersToXYZFiles( XYZ_FILES, XYZDirectoryManager )

# Wait for the threads to finish
while ThreadingManager.isBusy():
    time.sleep( BathyConfig.MAIN_THREAD_SLEEP_TIME_WHILE_PROCESSING ) # The main thread checks in at intervals >= the value specified in BathyConfig
	
# Here we process the XYZ files into Shapefiles
ProcessXYZFilesToShapefiles( XYZDirectoryManager, SHPDirectoryManager )

# Wait for the threads to finish
while ThreadingManager.isBusy():
    time.sleep( BathyConfig.MAIN_THREAD_SLEEP_TIME_WHILE_PROCESSING ) # The main thread checks in at intervals >= the value specified in BathyConfig

# Here we project the files into the desired coordinate system
ProjectShapefiles( SHPDirectoryManager, PRJDirectoryManager )