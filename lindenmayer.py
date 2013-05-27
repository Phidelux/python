#!/usr/bin/python
from pyparsing import Word, alphas, Regex, Literal, OneOrMore, ZeroOrMore, \
  ParseException, ParserElement, LineStart, LineEnd, SkipTo, Optional, Empty, \
	StringEnd, Suppress
from Tkinter import *
from turtle import *
import turtle
import random
import getopt
import sys
import re

class Lindenmayer(object):
	def __init__(self, stream):
		# Set the default image dimensions ...
		self.width = 500
		self.height = 500
		
		# ... and the number of iterations.
		self.iterations = 5
		
		# Set the default rotation angle in degrees.
		self.alpha = 90
		
		# Initialize the branch stack, ...
		self.stack = []
		
		# ... the constants, the rules, the variables and the axiom ...
		self.const = {'+':'+', '-':'-', '[':'[', ']':']'}
		self.rules = {}
		self.vars = []
		self.axiom = None
		
		# ... and drawing settings.
		self.bgcolor = (1.0, 1.0, 1.0)
		self.lineLength = 20
		self.lineWidth = 5
		self.lineColor = (0, 0, 0)
		
		# Calculate the starting position.
		self.offset = (0, -self.height*0.5)
		print 'Offset :', self.offset
		
		# Finally store the stream ...
		self.stream = stream
		
		# ... and initialize the parser.
		self.initialize()

	def initialize(self):
		ParserElement.setDefaultWhitespaceChars(' \t\r')
	
		integer = Regex(r"[+-]?\d+") \
			.setParseAction(lambda s,l,t: [ int(t[0]) ])
		number = Regex(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?") \
			.setParseAction(lambda s,l,t: [ float(t[0]) ])
		color = Regex(r"#([0-9a-fA-F]{6})")
		angle = "'" + Regex(r"(360|3[0-5][0-9]|[12][0-9]{2}|[0-9]{1,2})") \
			.setParseAction(lambda s,l,t: [ int(t[0]) ])
		variable = Word(alphas, exact=1).setParseAction(self.addVar)
		colon = Literal(":").suppress()
		comma = Literal(",")
		lBrace = Literal("(")
		rBrace = Literal(")")
		lBracket = Literal("[")
		rBracket = Literal("]")
		lAngle = Literal("<")
		rAngle = Literal(">")
		plus = Literal("+")
		minus = Literal("-")
		FTerm = Literal("F")
		fTerm = Literal("f")
		ZTerm = Literal("Z")
		zTerm = Literal("z")
		xTerm = Literal("x")
		cTerm = Literal("c")
		
		eol = OneOrMore(LineEnd()).suppress()
		param = ( angle | color | "!" + number | "|" + number )
		self.pList = lBrace + param + ZeroOrMore(comma + param) + rBrace
		literal = ((lBracket + ( variable + Optional(self.pList) 
				| plus + Optional(self.pList) | minus + Optional(self.pList) ) + rBracket)
			| (variable + Optional(self.pList) | plus + Optional(self.pList) 
				| minus + Optional(self.pList)))
		terminal = (ZTerm | zTerm | FTerm | fTerm | xTerm | cTerm
			| plus | minus | lBracket | rBracket)
		lprod = ( 
			(OneOrMore(terminal) + lAngle + variable + rAngle + OneOrMore(terminal))
			| (OneOrMore(terminal) + lAngle + variable) 
			| (variable + rAngle + OneOrMore(terminal)) 
			| variable )
		rProd = OneOrMore(literal | terminal)
		comment = Suppress((LineStart() + "#" + SkipTo(eol, include=True)))
		rules = ( 
			(lprod + Literal("=") + rProd + eol).setParseAction(self.addRule) \
			| comment )
		defaults = ( ( ("Dimensions" + colon + integer + comma + integer) 
			| ("Position" + colon + integer + comma + integer)
			| ("Iterations" + colon + integer)
			| ("Angle" + colon + angle)
			| ("Linelength" + colon + number)
			| ("Linewidth" + colon + number)
			| ("Linecolor" + colon + color)
			| ("Background" + colon + color)
			| ("Axiom" + colon + rProd) ) + eol ).setParseAction(self.setAttribute)
		header = ( defaults | comment )
		self.grammar = Suppress(ZeroOrMore(LineEnd())) \
			+ ZeroOrMore(header) \
			+ OneOrMore(rules)
			
		try:
			L = self.grammar.parseString( self.stream )
		except ParseException, err:
			print err.line
			print " "*(err.column-1) + "^"
			print err
			
		print 'Rules:', self.rules
		
	def setAttribute(self, stream, loc, toks):
		if toks[0] == 'Dimensions':
			self.width = toks[1]
			self.height = toks[3]
		if toks[0] == 'Position':
			self.offset = (toks[1], toks[3])
		elif toks[0] == 'Iterations':
			self.iterations = toks[1]
		elif toks[0] == 'Angle':
			self.alpha = toks[2]
		elif toks[0] == 'Linelength':
			self.lineLength = toks[1]
		elif toks[0] == 'Linewidth':
			self.lineWidth = toks[1]
		elif toks[0] == 'Linecolor':
			self.lineColor = toks[1]
		elif toks[0] == 'Axiom':
			self.axiom = ''.join(toks[1:])
		elif toks[0] == 'Background':
			self.bgcolor = toks[1]
		
	def addVar(self, stream, loc, toks):
		self.vars.append(toks[0])
		
	def addRule(self, stream, loc, toks):
		toks = list(toks)
		
		if "<" in toks and ">" in toks:
			key = (
				''.join(toks[:toks.index('<')]), 
				toks[toks.index('<')+1],
				''.join(toks[toks.index('>')+1:toks.index('=')])
			)
		elif "<" in toks:
			key = (
				''.join(toks[:toks.index('<')]), 
				toks[toks.index('<')+1],
				None
			)
		elif ">" in toks:
			key = (
				None,
				toks[toks.index('>')],
				''.join(toks[toks.index('>')+1:toks.index('=')])
			)
		else:
			key = (
				None,
				toks[0],
				None
			)
		
		self.rules[key] = toks[toks.index('=')+1:]
				
	def iterate(self):
		if self.axiom == None or not self.rules:
			return
			
		result = self.axiom
		for repeat in range(0, self.iterations):
			result = self.translate(result)

		return result

	def translate(self, axiom):
		result = ''
		for i in range(len(axiom)):
			if axiom[i] in self.const:
				result += axiom[i]
				continue
			if i > 0 and i < len(axiom)-1:
				key = (axiom[i-1], axiom[i], axiom[i+1])

				if key in self.rules:
					result += ''.join(map(str, self.rules.get(key)))
					continue
			if i > 0:
				key = (axiom[i-1], axiom[i], None)
				
				if key in self.rules:
					result += ''.join(map(str, self.rules.get(key)))
					continue
			if i < len(axiom)-1:
				key = (None, axiom[i], axiom[i+1])
				
				if key in self.rules:
					result += ''.join(map(str, self.rules.get(key)))
					continue
			key = (None, axiom[i], None)
			result += ''.join(map(str, self.rules.get(key, axiom[i])))
		return result

	def draw(self, stream, outputFile):
		# Setup turtle, ...
		turtle.setup(self.width, self.height) 
		
		# ... create a new window ...
		window = turtle.Screen()
		window.screensize(self.width, self.height)
		window.bgcolor(self.bgcolor)
		
		# ... and setup a new ninja turtle.
		raphael = turtle.Turtle()
		raphael.hideturtle()
		raphael.tracer(23, 0)
		raphael.speed(0)
		raphael.pensize(self.lineWidth)
		
		# Workaround for the eps background color problem.
		raphael.begin_fill()
		raphael.begin_poly()
		raphael.pencolor(self.bgcolor)
		raphael.fillcolor(self.bgcolor)
		raphael.goto(-self.width/2, -self.height/2)
		raphael.goto(self.width/2, -self.height/2)
		raphael.goto(self.width/2, self.height/2)
		raphael.goto(-self.width/2, self.height/2)
		raphael.goto(-self.width/2, -self.height/2)
		raphael.end_poly()
		raphael.end_fill()
		
		# Finally change settings to defaults.
		raphael.left(90)
		raphael.goto(self.offset)
		raphael.pencolor(self.lineColor)

		# Process the result stream symbol by symbol.
		for i in range(len(stream)):
			c = stream[i]
			
			if i+1 < len(stream)-1 and stream[i+1] == '(':
				end = stream.find(')', i+1)
				if end > 0:
					params = stream[i+1:end+1]
					print params
			
					try:
						L = self.pList.parseString( params )
					except ParseException, err:
						L = 'ERROR'
						print err.line
						print " "*(err.column-1) + "^"
						print err
			
					print 'Params:', L
					
			if c == 'F':
				# Move forward
				raphael.forward(self.lineLength)
			if c == 'f':
				# Move forward without drawing
				raphael.penup()
				raphael.forward(self.lineLength)
				raphael.pendown()
			if c == 'Z':
				# Move forward a half step
				raphael.forward(self.lineLength*0.5)
			if c == 'z':
				# Move forward a half step without drawing
				raphael.penup()
				raphael.forward(self.lineLength*0.5)
				raphael.pendown()
			if c == 'c':
				# Randomly change color
				self.lineColor = (random.random(), random.random(), random.random())
				raphael.pencolor(self.lineColor)
			if c == '+':
				# rotate clockwise
				raphael.right(self.alpha)
			if c == '-':
				# rotate anti-clockwise
				raphael.left(self.alpha)
			if c == '[':
				# Push the current turtle state to the stack
				self.stack.append((
					self.lineColor, self.lineWidth, raphael.heading(), raphael.pos()))
			if c == ']':
				# restore the transform and orientation from the stack
				self.lineColor, self.lineWidth, d, p = self.stack.pop()
				raphael.penup()
				raphael.pencolor(self.lineColor)
				raphael.pensize(self.lineWidth)
				raphael.goto(p)
				raphael.setheading(d)
				raphael.pendown()
				
		if outputFile != None: 
			ts = raphael.getscreen()
			ts.getcanvas().postscript(file=outputFile, colormode='color')
		
		window.onkey(window.bye, "q")
		window.listen()
		turtle.mainloop()
		
def usage():
	print "Usage: python Lindenmayer.py [-i <inputfile>] [-o <outputfile>] [-h]\n\n" \
	    "-i\tPath to the input file.\n\n" \
	    "-o\tPath to the eps output file.\n" \
	    "\tDefault is Lindenmayer.eps.\n\n" \
	    "-h\tShows this help";

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:o:", ["help", "input=", "output="])
	except getopt.GetoptError as err:
		# Print usage information and exit.
		print(err)
		usage()
		sys.exit(2)
	
	inputFile = None
	outputFile = None
	
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit(0)
		elif o in ("-i", "--input"):
			inputFile = a;
		elif o in ("-o", "--output"):
			outputFile = a;
		else:
			assert False, "unhandled option"
	
	if inputFile == None:
		print "Input file missing ..."
		usage()
		sys.exit(2)
	
	# Read the whole input file.
	with open(inputFile, 'r') as fp:
		stream = fp.read()
	
	# Do something!
	lindenmayer = Lindenmayer(stream)
	stream = lindenmayer.iterate()
	lindenmayer.draw(stream, outputFile)
	
if __name__ == "__main__":
	main(sys.argv[1:])
