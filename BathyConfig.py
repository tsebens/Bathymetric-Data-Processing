# BathyConfig
# A static text file that holds various configuration values that the rest of the program references

# If set to True, the script will use threading. Fair warning, this opens up an immense amount of complexity
USE_THREADING = False

# If set to True, the script will describe it's actions step by step. Useful for debugging
CONDITIONAL_OUTPUT_ALLOWED = True

# The root folder where the script will look for all raw input data
INPUT_ROOT_FOLDER = "C:\\Bathy\\ProcessBathymetricData\\Input"

# The root folder where all script outputs will be held (in appropriate subdirectories)
OUTPUT_ROOT_FOLDER = "C:\\Bathy\\ProcessBathymetricData\\Output"

# The file format which the script will look for in the raw data folder. At the moment, the script cannot handle any format except '.xyz'
INPUT_FILE_FORMAT = ".csv"

# The maximum number of parallel threads allowed to run simultaneously
MAX_ALLOWED_THREADS = 6

# The maximum size a subdirectory is allowed to reach before a new subdirectory is created. Expressed in bytes
MAX_FOLDER_SIZE = 900000

# If the main thread attempts to create a thread, and fails because there are too many threads, it will wait this long before reattempting to create the thread.
# A longer wait time will reduce the main thread load on the processor during heavy use, thus marginally decreasing latency, but may also decrease throughput.
# Expressed in seconds
WAIT_TIME_AFTER_THREAD_CREATION_FAILURE = 1

# When the main thread is waiting for the threads of a processing step to finish, it will check in at intervals >= this value
# Expressed in seconds
MAIN_THREAD_SLEEP_TIME_WHILE_PROCESSING = 1

# Column name for the Z_SCORE field when it's created in a shapefile
Z_SCORE_COLUMN_NAME = "Z-Score"

Z_FIELD_COLUMN_NAME = "z"

# The maxiumum absolute value a z score is allowed to have when processing a raw file
Z_SCORE_MAX_MIN = 1.98

# Only prints if the script has been told it is allowed. Can be set in BathyConfig
def ConditionalPrint( message, variables=None ):
	if CONDITIONAL_OUTPUT_ALLOWED == True:
		if variables != None:
			print( message % variables )
		else:
			print( message )