import math
import re
import sys
import time

ProgressBarSize = 71 # Number of characters between the "<>"s in the progress bar. Max allowable (without a new line) seems to be 71

# A simple class for managing print commands to the console. Allows same-line printing, and provides a progress bar
class DisplayManager( object ):
	
	def __init__( self ):
		self.lastPrinted = "" # Stores the last line printed to the display.
	
	# Clears the current console line
	def clearLine( self ):
		if len( self.lastPrinted ) > 0:
			clear = ""
			for char in self.lastPrinted:
				clear += " "
			sys.stdout.write( clear + "\r" ) # No new line
			sys.stdout.flush()

	# Prints 'message' to the console. 
	# @param message = The message to be printed to the console.
	# @param before = If true, a newline is created before the message
	# @param after = If true, a newline is created after the message
	def Display( self, message, before=False, after=False ):
		if before == True:
			print( "\n" )
		self.clearLine()
		sys.stdout.write( str( message ) + "\r" ) # No new line

		self.lastPrinted = str( message )
		if after == True:
			print( "\n" )

	# Prints a little ASCII progress bar to the console, as well as the percentage completed.
	# @param perc = The percentage to be displayed. It is assumed that perc < 100
	def DisplayProgress( self, perc ):
		Nearest = math.floor( perc / ( 100 / ProgressBarSize ) ) # The closest estimation to perc (without going over) given the number of characters allowed in the progress bar
		ProgressBar = "<" 
		i = 0 # Our current index in the progress bar
		while i < Nearest - 1:
			ProgressBar += "-"
			i += 1
		ProgressBar += "|"
		i += 1
		while i < ProgressBarSize:
			ProgressBar += "_"
			i += 1
		ProgressBar += ">"
		self.Display( ProgressBar + " - " + str( perc ) )
		
