# Repository for several functions used to process Bathymetric Data
# Author: Tristan Sebens
# Contact: tristan.ng.sebens@gmail.com

# import arcpy
import os
import sys
import time
import re
import arcpy
import sys

# This function requests all necessary licenses from ArcGIS
def GetNecessaryLicenses():
	arcpy.CheckOutExtension("3D")


# Originally authored by Jeff Hartley
# Edited for use in this toolbox by Tristan Sebens
# Method that splits the input feature class into multiple smaller feature classes, each made up of the specified number of features.
# If the cleanup flad is set to >0, then the input file will be deleted after being split.
# The new, smaller files will be saved into the same directory as the old, large, input file.
# @param fcName = The feature class to be split
# @param featCount = The max number of features each of the smaller feature classes will contain.
# @param cleanup = A flag for whether or not to delete the old, large file after the splitting is complete. Considered raised if > 0
def SplitFCByNumFeat( fcName, featCount, cleanup=False ):
    if arcpy.Exists( fcName ):
    	pass
    else:
        pass #TODO: Intelligent exception handling for a non-extant file

    ( outDir, FILE_NAME ) = fcName.rsplit( os.sep, 1 ) # Split the input path into the filename, and the file's directory
    ( FC_LAYER_NAME, EXT ) = os.path.splitext( FILE_NAME ) # Split the filename into the layername, and the extension

    # Create a layer for the selector
    arcpy.MakeFeatureLayer_management( fcName, "inputLayer" )
    print( "\nCreated layer for processing." )

    # For each range of OIDs, select the features from the feature class and write them to a new file
    i = featCount
    totalFeats = arcpy.GetCount_management("inputLayer")

    # figure out the OID for the layer
    fldList = arcpy.ListFields(fcName, "*", "OID")
    for fld in fldList:
        fldName = fld.name
    intersectStartTime = time.time()
	
    while i <= (int(totalFeats.getOutput(0)) + int(featCount)):
        print( "\nProcessing features " + fldName.upper() + " >= " + str(i - featCount) + " AND " + fldName.upper() + " < " + str(i) + "\n" )
		
	# Create the output feature class name
        outFC = os.path.join( outDir, FC_LAYER_NAME + "Intersect_" + str(i - featCount) + "_" + str(i) + EXT )
	# Select the features
        try:
            if i > featCount:
                arcpy.Select_analysis( fcName, outFC, fldName.upper() + " >= " + str(i - featCount) + " AND " + fldName.upper() + " < " + str(i) )
            else:
                arcpy.Select_analysis( fcName, outFC, fldName.upper() + " >= " + str(i - featCount) + " AND " + fldName.upper() + " < " + str(i) )
                print( "\n" + arcpy.GetMessages())
                selByAttrCount = arcpy.GetCount_management("inputLayer")
                print( "Number of features selected from " + fcName + " : " + str(selByAttrCount.getOutput(0) ) )
        except:
            print( "\n" + arcpy.GetMessages() )
            sys.exit()
        i += featCount
		
    intersectStopTime = time.time()
    intTotalTime = (intersectStopTime - intersectStartTime) / 60
    print( "Total time to run split using selection sets = " + str(intTotalTime) + " minutes.")

    # Delete old files
    if cleanup == True: # Check to see if the flag is set
        print( "Deleting old files." % FC_LAYER_NAME )
        files = os.listdir( outDir )
        for file in files:
            ( layerName, extension ) = os.path.splitext( file )
            if layerName == FC_LAYER_NAME:
                try:
                    os.remove( os.path.join( outDir, file ) )
                except:
                    pass # If the file isn't there any more, then we don't care
	
# Method that walks through a file tree recursively, looking for files with the specified extension.
# It then returns a list containing all files which mached the specified extension
# @param root = The root of the file tree to search through
# @param ext = The extension to look for
def FindFilesByExtension( ROOT, EXTENSION ):
    AllFiles = os.walk( ROOT, True, None, False )
    ReturnFiles = list()

    for entry in AllFiles:
        # entry is a tuple containing (path, directories, files)
        for file in entry[2]:
            ( filename, extension ) = os.path.splitext( file )
            if extension == ext:
                ReturnFiles.append( os.path.join( entry[0], file ) )

    return ReturnFiles

# Adds header to XYZ file. NOT TECHNICALLY TESTED (since revision)
# Throws an exception if a line is found with missing data. When this happens, the line is disregarded, an error is printed to the console, and processing continues
# @param FILE_PATH = The path of the file to be processed
# @param OUT_DIRECTORY = The directory to save the newly processed file
def AddHeaderToXYZFile( FILE_PATH, OUT_DIRECTORY ):
    ( FILE_DIRECTORY, FILE_NAME, FILE_EXTENSION ) = SplitFilePath( FILE_PATH )
    headerLine = "x,y,z\n"

    newFilename = FILE_NAME + "_proc" + FILE_EXTENSION # Create the new filename for the file.

    # Here we open the file for parsing 
    f = open( FILE_PATH, "r+" )
                
    content = headerLine
    f.readline()

    # In this loop, we go through the file line by line
    for line in f.readlines():
        line.strip()
        newLine = re.sub(r"[\t ]+", ",", line)
        newLineArray = newLine.split(",")
        try: 
            z = float(newLineArray[-1].strip()) * -1
        except ValueError:
            errorCount += 1

            print("Found an offending line: " + line + "Total Offending Lines: " + str(errorCount) )
            continue
        newLine = "%s,%s,%s\n" % (newLineArray[0], newLineArray[1], z)
        content+= newLine
            
    # Now that we have finished writing the new file, we can save it to the finished directory
    newFile = open(os.path.join( OUT_DIRECTORY, newFilename), "w")
    newFile.write(content)
       
    # We are finished. Now we clean up after outselves by closing all resources.
    f.close()
    newFile.close

# Processes an XYZ file into a shapefile, along will all corresponding file, to the specified directory
# @param FILE_PATH = The path of the file that is to be processed
# @param OUT_DIRECTORY = The directory into which the shape file and all corresponding files will be output to
def ProcessXYZtoShapefile( FILE_PATH, OUT_DIRECTORY ):
    ( FILE_DIRECTORY, FILE_NAME, FILE_EXTENSION ) = SplitFilePath( FILE_PATH )
    outFile = os.path.join( OUT_DIRECTORY, FILE_NAME )
    arcpy.ASCII3DToFeatureClass_3d( FILE_PATH, "XYZ", outFile, "POINT", "1", "", "", "", "DECIMAL_POINT")

# Projects a shapefile in Alaska Albers coordinate system. If the projection is for some reason unsuccessful, this method throws an exception.
def ProjectShapefile( FILE_PATH, OUT_DIRECTORY ):
    ( FILE_DIRECTORY, FILE_NAME, FILE_EXTENSION ) = SplitFilePath( FILE_PATH )
    OUT_NAME = FILE_NAME + "_AA" + FILE_EXTENSION
    OUT_FILE = os.path.join( OUT_DIRECTORY, FILE_NAME )
    try:
        arcpy.Project_management( FILE_PATH, OUT_FILE, "PROJCS['NAD_1983_Alaska_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-154.0],PARAMETER['Standard_Parallel_1',55.0],PARAMETER['Standard_Parallel_2',65.0],PARAMETER['Latitude_Of_Origin',50.0],UNIT['Meter',1.0]]", "", "")
    except Exception as e:
        raise e

# This method is meant to perform a basic analysis of bathymetric data, and to delete those points in the data which appear to be inaccurate.
# The inaccuracy arises largely from the fact that as the distance between the sonar array and the ocean floor increases, the readings become less and less reliable.
# Our model assumes that areas where close neighbors have very different values are probably not accurate readings, since the ocean floor 
# This assumption isn't perfect, and probably invalidates the scientific validity of this model, but given that we have to provide a way to feasibly perform basic
# error removal on mulit-terabyte sized data sets, it's pretty darn good.
# Currently requires two folders in the same directory as the passed file:
# 	One called 'outliers_removed' where the processed file will be saved
#	One called 'temp_files' where the temporary files required to execute the script will be saved.
# @param INPUT = The file to be processed
# @param OUTPUT_DIRECTORY = The directory to save the output in
# @param MIN_BIN_SCORE = The minimum Gi_bin score that will be included in the final shapefile
def RemoveOutliers( INPUT, OUTPUT_DIRECTORY, MIN_BIN_SCORE ):
    ( FILE_DIRECTORY, FILE_NAME, FILE_EXTENSION ) = SplitFilePath( FILE_PATH )
    ( INPUT_DIRECTORY, FILE_NAME, EXTENSION ) = SplitFilePath( INPUT )
	
    OUTPUT_FILE = os.path.join( OUTPUT_DIRECTORY, FILE_NAME + "_HADone" + EXTENSION )
    TEMP_DIRECTORY = os.path.join( INPUT_DIRECTORY, "temp_files" )
    HOTSPOT_ANALYSIS = os.path.join( TEMP_DIRECTORY, FILE_NAME + "_WANTED_FEATURES" + EXTENSION )
	
	
    # Perform Analysis	
    print( "Performing Hotspot Analysis on %s..." % FILE_NAME )
    arcpy.HotSpots_stats(INPUT, "z", HOTSPOT_ANALYSIS, "INVERSE_DISTANCE", "EUCLIDEAN_DISTANCE", "NONE", "", "", "", "NO_FDR")

    # Using the data from the Hotspot Analysis, select those features appear to be accurate (i.e. Exhibit good continuity of depth between closely neighbored features)
    print( "Selecting appropriate points from %s..." % FILE_NAME )
    arcpy.Select_analysis( HOTSPOT_ANALYSIS, OUTPUT_FILE, "\"Gi_Bin\">=" + MIN_BIN_SCORE)

    # Finally, remove all elements from the original input file that do not fall within the bounds of our select statement, and are therefore arguably inaccurate
    # data points.
	
    print( "Clipping inaccurate points from %s..." % FILE_NAME )
    arcpy.Clip_analysis( OUTPUT_FILE, WANTED_FEATURES, CLIPPED_OUTPUT, "")
    print( "Processing done for %s." % FILE_NAME )

# Accepts a shapefile as input, then calculates the Z-Score for each point in the shapefile and adds the value in a new column 
# The new column's name is specified in BathyConfig
def CalculateAndAddZScores( INPUT ):
	# Generate directory for table stats
	( IN_DIR, IN_NAME, IN_EXT ) = SplitFilePath( INPUT )
	TABLE_STATS = os.path.join( IN_DIR, "TABLE_STATS.dbf" )

	if os.path.isfile( TABLE_STATS ):
		shutil.remove( TABLE_STATS )
		
	# Process: Summary Statistics
	arcpy.Statistics_analysis(INPUT, TABLE_STATS, "z MEAN;z STD", "")
	
	try:
		# Process: Add Field
		arcpy.AddField_management(INPUT, BathyConfig.Z_SCORE_COLUMN_NAME, "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
	except:
		pass # TODO: What to do if the field already exists
		
	# Using a cursor, grab the statistical values from the table
	cursor = arcpy.SearchCursor( TABLE_STATS )
	row = cursor.next()
	STD_DEV = row.getValue( "STD_z" )
	MEAN =  row.getValue( "MEAN_z" )

	# Expression for calculating the z-score: ( Z - MEAN ) / STD_DEV
	EXPRESSION = "([" + BathyConfig.Z_FIELD_COLUMN_NAME + "]-" + str(MEAN) + ")/" + str(STD_DEV) 
	
	#  Calculate field and add it to the new column
	arcpy.CalculateField_management(INPUT, BathyConfig.Z_SCORE_COLUMN_NAME, EXPRESSION, "VB", "")
	
# Accepts a shapefile as input, then removes from the shapefile all features whose z-scores are outside the maximum allowed.
# Max allowed z-score is specified by BathyConfig
def RemoveExtremeZScores( INPUT ):
	( IN_DIR, IN_NAME, IN_EXT) = SplitFilePath( INPUT )
	SELECTED = os.path.join( IN_DIR, "SELECTED" )
	
	# Process: Select
	arcpy.Select_analysis(INPUT, SELECTED, "ABS( \"Z_SCORE\") > " + BathyConfig.Z_SCORE_MAX_MIN )

	# Process: Delete Features
	arcpy.DeleteFeatures_management(SELECTED)
	
# Helper function that takes in a filepath, and returns a list containing three items:
# 0: The directory of the file
# 1: The name of the file
# 2: The extension of the file
def SplitFilePath( INPUT ):
	( INPUT_DIRECTORY, FILE ) = INPUT.rsplit( os.sep, 1 ) # Split the input path into the filename, and the file's directory
	( FILE_NAME, EXTENSION ) = os.path.splitext( FILE )
	return ( INPUT_DIRECTORY, FILE_NAME, EXTENSION )
