# -*- coding: iso-8859-2 -*-
# $Id: path_element.py,v 1.8 2007-05-20 12:34:26 wojtek Exp $
#
# pydvi2svg - SVG path data parser & bbox calculate
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
20.05.2007
    - bug fixed in 'tokens.flag'
 8.03.2007
	- bug fixed in 'tokens'
 7.03.2007
	- function 'tokens' imporovements
	- function 'iter' renamed to 'path_iter'
"""

import re
import math
import string

r_split = re.compile("([MmZzLlHhVvCcSsQqTtAa])| ")
s_trans = string.maketrans("\n\r,", "   ")
set_Z   = set("zZ")
set_VH  = set("vVhH")
set_MLT = set("mMlLtT")
set_SQ  = set("sSqQ")
set_C   = set("cC")
set_A   = set("aA")
set_commands = set("zZvVhHmMlLtTsSqQcCaA")

class iter2(object):
	# simple iterator-like class, that support rewind
	def __init__(self, sequence):
		self.seq = sequence
		self.n = len(sequence)
		self.i = 0
	
	def next(self):
		if self.i == self.n:
			raise StopIteration
		v = self.seq[self.i]
		self.i += 1
		return v
	
	def back(self):
		if self.i == 0:
			raise StopIteration
		self.i -= 1


def tokens(d_attribute, tofloat=float):
	d = str(d_attribute).translate(s_trans)

	# split into list of commands/parameters
	d = filter(bool, re.split(r_split, d))
	
	# iter
	d = iter2(d)

	def number():
		try:
			item = d.next()
			return float(item)
		except StopIteration:
			raise ValueError("Number expeced, end of list reached")
		except ValueError:
			raise ValueError("Number expeced - got '%s'" % item)
	
	def pair():
		x = number()
		y = number()
		return x, y
	
	def flag():
		try:
			item = d.next()
			v = int(item)
		except StopIteration:
			raise ValueError("Flag expeced, end of list reached")
		except ValueError:
			raise ValueError("Integer expeced, got '%s'" % flag)

		if v == 0 or v == 1:
			return v
		else:
			raise ValueError("Flag must have value 0 or 1, got %d" % flag)

			
	command = 'undefined'
	while True:
		try: tmp = d.next()
		except StopIteration:
			break

		if tmp in set_commands:
			command = tmp
		else:
			# token is not a command, get back
			try: d.back()
			except StopIteration:
				raise ValueError("First element in path must be command.")
		
		if command in set_Z:
			yield (command, None)
		elif command in set_VH:
			yield (command, number())
		elif command in set_MLT:
			yield (command, pair())
		elif command in set_SQ:
			yield (command, (pair(), pair()))
		elif command in set_C:
			yield (command, (pair(), pair(), pair()))
		elif command in set_A:
			yield (command, (pair(), number(), flag(), flag(), pair(), pair()))
		else:
			raise ValueError("Unknown command '%s'" % command)
	#while


def path_iter(L, init_x=0.0, init_y=0.0, line_fn=None, ccurve_fn=None, qcurve_fn=None):

	cur_x = init_x		# current point
	cur_y = init_y

	clast_x2 = None		# last control point for 's'/'S' 
	clast_y2 = None

	qlast_x1 = None		# last control point for 't'/'T'
	qlast_y1 = None

	mlast_x1 = None		# last moveto coord (for 'z' -- closepath)
	mlast_y1 = None

	def nop(*arg):
		pass
	
	line_fn   = line_fn or nop
	ccurve_fn = ccurve_fn or nop
	qcurve_fn = qcurve_fn or nop

	prevcomm = 'none'
	for command, param in L:

		# move commands
		# ---------------------------------------------------

		# relative move
		if command == 'm':
			(x,y) = param

			# first 'm' is replaced with 'M'
			if prevcomm == 'none':
				cur_x = x
				cur_y = y
				mlast_x, mlast_y = cur_x, cur_y

			# sequence of m's are converted to rmoveto-lineto
			elif prevcomm == 'm':
				line_fn( (cur_x,cur_y), (cur_x + x, cur_y + y) )
				cur_x += x
				cur_y += y

			# relmove to
			else:
				cur_x += x
				cur_y += y
				mlast_x, mlast_y = cur_x, cur_y

		# absolute move (begin new subpath)
		elif command == 'M':
			(x,y) = param

			# sequence of M's are converted to moveto-lineto
			if prevcomm == 'M':
				line_fn( (cur_x, cur_y),  (x, y) )
				cur_x = x
				cur_y = y

			# move to
			else:
				cur_x = x
				cur_y = y
				mlast_x, mlast_y = cur_x, cur_y

		# line drawing commands
		# ---------------------------------------------------

		# relative lineto
		elif command == 'l':
			(x,y) = param
			line_fn( (cur_x, cur_y), (cur_x + x, cur_y + y) )
			cur_x += x
			cur_y += y

		# absolute lineto
		elif command == 'L':
			(x,y) = param
			line_fn( (cur_x, cur_y), (x, y) )
			cur_x = x
			cur_y = y

		# relative horizontal-lineto
		elif command == 'h':
			x = param
			line_fn( (cur_x, cur_y), (cur_x + x, cur_y) )
			cur_x += x
		
		# absolute horizontal-lineto
		elif command == 'H':
			x = param
			line_fn( (cur_x, cur_y), (x, cur_y) )
			cur_x = x

		# realive veritical-lineto
		elif command == 'v':
			y = param
			line_fn( (cur_x, cur_y), (cur_x, cur_y + y) )
			cur_y += y
		
		# absolute veritical-lineto
		elif command == 'V':
			y = param
			line_fn( (cur_x, cur_y), (cur_x, y) )
			cur_y = y

		# cubic curves
		# ---------------------------------------------------

		# relative curveto
		elif command == 'c':
			x1, y1 = param[0]
			x2, y2 = param[1]
			x, y   = param[2]

			ccurve_fn( (cur_x, cur_y),
			           (cur_x + x1, cur_y + y1),
			           (cur_x + x2, cur_y + y2),
			           (cur_x + x, cur_y + y))

			clast_x2 = cur_x + x2
			clast_y2 = cur_y + y2
			cur_x += x
			cur_y += y
		
		# absolute curveto
		elif command == 'C':
			x1, y1 = param[0]
			x2, y2 = param[1]
			x, y   = param[2]

			ccurve_fn( (cur_x, cur_y), (x1, y1), (x2, y2), (x, y) )

			clast_x2 = x2
			clast_y2 = y2
			cur_x = x
			cur_y = y

		# relative smooth curveto
		elif command == 's':
			x2, y2 = param[0]
			x, y   = param[1]

			if prevcomm in set(['c','C','s','S']):
				x1 = cur_x - clast_x2
				y1 = cur_y - clast_y2
			else:
				x1 = cur_x
				y1 = cur_y

			ccurve_fn( 
				(cur_x, cur_y),
				(cur_x + x1, cur_y + y1),
				(cur_x + x2, cur_y + y2),
				(cur_x + x, cur_y + y)
			)

			clast_x2 = cur_x + x2
			clast_y2 = cur_y + y2
			cur_x += x
			cur_y += y
				
		# absolute smooth curveto
		elif command == 'S':
			x2, y2 = param[0]
			x, y   = param[1]

			if prevcomm in set(['c','C','s','S']):
				x1 = cur_x - last_x2
				y1 = cur_y - last_y2
			else:
				x1, y1 = cur_x, cur_y

			ccurve_fn( (cur_x, cur_y), (x1, y1), (x2, y2), (x, y))

			clast_x2 = x2
			clast_y2 = y2
			cur_x = x
			cur_y = y


		# quadratic curves
		# ---------------------------------------------------
		
		# relative curveto
		elif command == 'q':
			x1, y1 = param[0]
			x, y   = param[1]

			qcurve_fn( (cur_x, cur_y), (cur_x + x1, cur_y + y1), (cur_x + x, cur_y + y) )

			qlast_x1 = cur_x + x1
			qlast_y1 = cur_y + y1
			cur_x += x
			cur_y += y
		
		# absolute curveto
		elif command == 'Q':
			x1, y1 = param[0]
			x, y   = param[1]

			qcurve_fn( (cur_x, cur_y), (x1, y1), (x, y) )

			qlast_x1 = x1
			qlast_y1 = y1
			cur_x = x
			cur_y = y
		
		# relative smooth curveto
		elif command == 't':
			(x,y) = param
			if prevcomm in set(['q','Q','t','T']):
				x1 = cur_x - qlast_x1
				y1 = cur_y - qlast_y1
			else:
				x1 = cur_x
				y1 = cur_y
			
			qcurve_fn( (cur_x, cur_y), (x1, y1), (cur_x + x, cur_y + y) )

			qlast_x1 = x1
			qlast_y1 = y1
			cur_x += x
			cur_y += y
			
		# absolute smooth curveto
		elif command == 'T':
			(x,y) = param
			if prevcomm in set(['q','Q','t','T']):
				x1 = cur_x - qlast_x1
				y1 = cur_y - qlast_y1
			else:
				x1 = cur_x
				y1 = cur_y
			
			qcurve_fn( (cur_x, cur_y), (x1, y1), (x, y) )

			qlast_x1 = x1
			qlast_y1 = y1
			cur_x = x
			cur_y = y
		
		elif command in set(['z', 'Z']):
			# close current subpath
			line_fn( (cur_x, cur_y), (mlast_x, mlast_y) )

		# elliptical arc (not implemented)
		elif command == 'a':
			raise NotImplementedError
		elif command == 'A':
			raise NotImplementedError
		
		else:
			ValueError("unknown command '%s'" % command)

		prevcomm = command
	#rof
#fed

def bounding_box(L):
	class Dummy:
		pass
	
	cur = Dummy()
	cur.x = []
	cur.y = []

	
	def line((x1,y1), (x2,y2)):
		cur.x.append(x1); cur.x.append(x2)
		cur.y.append(y1); cur.y.append(y2)
	#fed
	
	def qbezier((x0,y0), (x1,y1), (x2,y2)):
		"""Calculate BB of quadric Bezier curve"""

		# bezier curve represented in polynomial base:
		# A t^2 + B t^1 + C 
		Ax =    x0 - 2*y1 + y2
		Bx = -2*x0 + 2*y1
		Cx =    x0
		
		Ay =    y0 - 2*y1 + y2
		By = -2*y0 + 2*y1
		Cy =    y0

		# find extremas
		x = [x0,x2]
		if abs(Ax) > 1e-10:
			x.append(-Bx/(2*Ax))

		y = [y0,y2]
		if abs(Ay) > 1e-10:
			y.append(-By/(2*Ay))

		# update global table
		cur.x.extend(x)
		cur.y.extend(y)

		#return (min(x), min(y)), (max(x), max(y))
	#fed

	def cbezier((x0,y0), (x1,y1), (x2,y2), (x3,y3)):
		"""Calculate BB of cubic Bezier curve"""

		def solve(a,b,c):
			"""Solve quadratic equation"""
			if abs(a) < 1e-10:
				if abs(b) < 1e-10:
					return []
				else:
					return [-c/b]
			else:
				delta = b*b - 4*a*c
				if delta < 0.0:
					return []
				elif delta > 0.0:
					dsq = math.sqrt(delta)
					return [(-b-dsq)/(2*a), (-b+dsq)/(2*a)]
				else:
					return [-b/(2*a)]
		#fed

		# bezier curve represented in polynomial base:
		# A t^3 + B t^2 + C t + D
		Ax =   -x0 + 3*x1 - 3*x2 + x3	# t^3
		Bx =  3*x0 - 6*x1 + 3*x2		# t^2
		Cx = -3*x0 + 3*x1				# t^1
		Dx =    x0						# t^0
		
		Ay =   -y0 + 3*y1 - 3*y2 + y3	# t^3
		By =  3*y0 - 6*y1 + 3*y2		# t^2
		Cy = -3*y0 + 3*y1				# t^1
		Dy =    y0						# t^0

		# find extremas
		x = [x0, x3]
		for t in solve(3*Ax, 2*Bx, Cx):
			if 1.0 > t > 0.0:
				t2 = t*t
				t3 = t*t2
				x.append(t3*Ax + t2*Bx + t*Cx + Dx)
		
		y = [y0, y3]
		for t in solve(3*Ay, 2*By, Cy):
			if 1.0 > t > 0.0:
				t2 = t*t
				t3 = t*t2
				y.append(t3*Ay + t2*By + t*Cy + Dy)

		# update global table
		cur.x.extend(x)
		cur.y.extend(y)
		
		#return (min(x), min(y)), (max(x), max(y))
	#fed

	
	path_iter(L, line_fn=line, qcurve_fn=qbezier, ccurve_fn=cbezier)
	return (min(cur.x), min(cur.y)), (max(cur.x), max(cur.y))

# vim: ts=4 sw=4
