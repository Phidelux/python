#!/usr/bin/python
from Tkinter import *
from turtle import *
import turtle
import getopt
import sys

class Langton(object):
	def __init__(self, iterations, blockSize, gridSize):
		self.iterations = iterations
		self.blockSize = blockSize
		self.gridSize = gridSize
		self.stepSize = blockSize

		self.posStack = dict()

		self.black = (0.0, 0.0, 0.0)
		self.white = (1.0, 1.0, 1.0)

		self.width = self.height = blockSize * gridSize

	def draw(self, outputFile):
		# Setup turtle, ...
		turtle.setup(self.width, self.height) 
		
		# ... create a new window ...
		window = turtle.Screen()
		window.screensize(self.width, self.height)
		
		# ... and setup a new ninja turtle.
		raphael = turtle.Turtle()
		raphael.pensize(self.blockSize)
		raphael.hideturtle()
		raphael.tracer(13, 0)
		raphael.speed(0)

		for i in range(self.iterations):
			# Fetch the current position ...
			pos = (int(raphael.pos()[0]), int(raphael.pos()[1]))

			# ... and fetch the current color.
			color = self.white

			if self.posStack.has_key(pos):
				color = self.posStack[pos]

			# Fetch the new color and update the direction.
			if color == self.white:
				raphael.left(90)
				color = self.black 
			else: 
				raphael.right(90)
				color = self.white
				
			# Fill the current cell, ...
			raphael.pencolor(color)
			raphael.dot(self.blockSize)

			# ... update the position stack ...
			self.posStack[pos] = color

			# ... and move one step.
			raphael.up()
			raphael.forward(self.stepSize)
			raphael.down()
				
		if outputFile != None: 
			ts = raphael.getscreen()
			ts.getcanvas().postscript(file=outputFile, colormode='color')
		
		window.onkey(window.bye, "q")
		window.listen()
		turtle.mainloop()
		
def usage():
	print "Usage: python langton.py [-i iterations] [-s blockSize] [-g gridSize] [-o outFile] [-h]\n\n" \
	    "-i\tNumber of iterations.\n" \
	    "\tDefault is 10000.\n\n" \
	    "-s\tSize of the fields.\n" \
	    "\tDefault is 3 (3x3 px).\n\n" \
	    "-g\tSize of the drawing grid.\n" \
	    "\tDefault is 500 (500x500 px).\n\n" \
	    "-o\tPath to the eps output file.\n" \
	    "\tDefault is no output.\n\n" \
	    "-h\tShows this help";

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:s:g:o:", ["help", "iterations=", "size=", "grid=", "output="])
	except getopt.GetoptError as err:
		# Print usage information and exit.
		print(err)
		usage()
		sys.exit(2)

	iterations = 10000
	blockSize = 3
	gridSize = 500
	outputFile = None

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit(0)
		elif o in ("-i", "--iterations"):
			iterations = int(a);
		elif o in ("-s", "--size"):
			blockSize = int(a);
		elif o in ("-g", "--grid"):
			gridSize = int(a);
		elif o in ("-o", "--output"):
			outputFile = a;
		else:
			assert False, "unhandled option"
	
	# Do something!
	langton = Langton(iterations, blockSize, gridSize)
	langton.draw(outputFile)
	
if __name__ == "__main__":
	main(sys.argv[1:])
