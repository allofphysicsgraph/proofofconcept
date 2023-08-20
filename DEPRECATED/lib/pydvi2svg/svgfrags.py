#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
# $Id: svgfrags.py,v 1.9 2007-03-13 20:55:37 wojtek Exp $
#
# SVGfrags - main program
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl/

"""
13.03.2007
	- syntax chenges:
	  * keyword "this" as source
	- use frags.get_text, frags.get_anchor
	- + cleanup 
	- + traceback
12.03.2007
	- use new parser (frags/parser.py & frags/parse_subst.py)
	- syntax changes:
	  * removed 'settowidth' & 'settoheight' (now can be expressed with 'scale')
	  * removed 'fit' (now 'scale' option)
	  * added ('length' num) to scale
10.03.2007
	- share same TeX expression
	- id based on file timestamp & string hash (to reasume purposes)
	- keep old DVI & TeX fles
	- EquationsManager updated (SVGGfxDocument was changed)
	- colors inherit from text nodes
	- TeX-object space margin support
	- options parse
 9.03.2007
	- parser
	- clean up
 8.03.2007
	- early tests
"""

import sys, os, atexit

import logging
import xml.dom.minidom

import setup
import frags
import dvi2svg

from conv import utils
from conv import fontsel
from conv import dviparser
from conv.findfile import which
from conv.binfile  import binfile


DEBUG = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('SVGfrags')

class EquationsManager(dvi2svg.SVGGfxDocument):
	def __init__(self, doc, mag, scale, unit_mm):
		super(EquationsManager, self).__init__(mag, scale, unit_mm, (0,0))

		self.document = doc
		self.svg = self.document.documentElement

	def new_page(self):
		self.chars = []
		self.rules = []
		self.lastpage = None
		self.lastbbox = None
		pass

	def eop(self):
		scale2str = self.scale2str
		coord2str = self.coord2str

		g = self.document.createElement('g')
		self.lastpage = g
		self.lastbbox = self.get_page_bbox()

		for element in self.flush_rules() + self.flush_chars():
			g.appendChild(element)


		# (DEBUG)
		if DEBUG:
			xmin, ymin, xmax, ymax = self.lastbbox
			r = self.document.createElement('rect')
			r.setAttribute('x', str(xmin))
			r.setAttribute('y', str(ymin))
			r.setAttribute('width', str(xmax - xmin))
			r.setAttribute('height', str(ymax - ymin))
			r.setAttribute('fill', 'none')
			r.setAttribute('stroke', 'red')
			r.setAttribute('stroke-width', '0.25')
			g.appendChild(r)
		#for
	
	def save(self, filename):
		defs = self.document.getElementsByTagName('defs')[0]
		for element in self.flush_glyphs():
			defs.appendChild(element)

		# save file
		f = open(filename, 'wb')
		if setup.options.prettyXML:
			f.write(self.document.toprettyxml())
		else:
			f.write(self.document.toxml())
		f.close()


def main(args):
	from frags.cmdopts import parse_args

	(setup.options, args) = parse_args(args)
	
	# fixed options
	setup.options.use_bbox  = True
	setup.options.prettyXML = False

	input_txt = setup.options.input_txt
	input_svg = setup.options.input_svg
	output_svg = setup.options.output_svg

	if not input_txt:
		log.error("Rules file not provided, use switch -r or --rules")
		sys.exit(1)
	elif not os.path.exists(input_txt):
		log.error("Rules file '%s' don't exist", input_txt)
		sys.exit(1)
	
	if not input_svg:
		log.error("Input SVG file not provided, use switch -i or --input")
		sys.exit(1)
	elif not os.path.exists(input_svg):
		log.error("Input SVG file '%s' don't exist", input_svg)
		sys.exit(1)
	
	if not output_svg:
		log.error("Output SVG file not provided, use switch -i or --output")
		sys.exit(1)
	elif os.path.exists(output_svg) and not setup.options.frags_overwrite_file:
		log.error("File %s already exists, and cannot be overwritten.  Use switch -f or --force-overwrite to change this behaviour.", output_svg)
		sys.exit(1)


	# 1. Load SVG file
	XML = xml.dom.minidom.parse(input_svg)

	# 1.1. Create 'defs' tag (if doesn't exists), and add xlink namespace
	if not XML.getElementsByTagName('defs'):
		XML.documentElement.insertBefore(
			XML.createElement('defs'),
			XML.documentElement.firstChild
		)

	if not XML.documentElement.getAttribute('xmlns:xlink'):
		XML.documentElement.setAttribute('xmlns:xlink', "http://www.w3.org/1999/xlink")

	if True:
		# XXX: hack; for unknown reason expat do not read id attribute
		# and getElementById always fails
		ID = {}
		frags.collect_Id(XML, ID)

		def my_getElementById(id):
			try:
				return ID[id]
			except KeyError:
				return None
		XML.getElementById = my_getElementById


	# 1.2. find all text objects
	text_objects = {} # text -> node
	for node in XML.getElementsByTagName('text'):
		try:
			text = frags.get_text(node, setup.options.frags_strip)
			# add to list
			if text in text_objects:
				text_objects[text].append(node)
			else:
				text_objects[text] = [node]
		except ValueError:
			pass
	#for

	# 2. Load & parse replace pairs
	input = open(input_txt, 'r').read()

	from frags.parse_subst import parse
	repl_defs  = frags.Dict() # valid defs
	text_nodes = set()        # text nodes to remove/hide
	try:
		for item in parse(input):
			((kind, value), tex, options) = item

			if tex is None: # i.e. "this"
				if kind == 'string':
					if setup.options.frags_strip:
						tex = value.strip()
					else:
						tex = value
				elif kind == 'id':
					node = XML.getElementById(value[1:])
					if frags.istextnode(node):
						tex = frags.get_text(node)

			if tex is None:
				log.error("Keyword 'this' is not allowed for rect/points object")
				continue

			if kind == 'string':
				if setup.options.frags_strip:
					value = value.strip()

				try:
					for node in text_objects[value]:
						text_nodes.add(node)
						repl_defs[tex] = ((kind, node), tex, options)
				except KeyError:
					log.warning("String '%s' doesn't found in SVG, skipping repl", value)

			elif kind == 'id':
				object = XML.getElementById(value[1:])
				if object:
					# "forget" id, save object
					if object.nodeName in ['rect', 'ellipse', 'circle']:
						repl_defs[tex] = ((kind, object), tex, options)
					elif object.nodeName == 'text':
						repl_defs[tex] = (('string', object), tex, options)
					else:
						log.warning("Object with id=%s is not text, rect, ellipse nor circle - skipping repl", value)
				else:
					log.warning("Object with id=%s doesn't found in SVG, skipping repl", value)

			else: # point, rect -- no additional tests needed
				repl_defs[tex] = ((kind, value), tex, options)

	except frags.parse_subst.SyntaxError, e:
		log.error("Syntax error: %s", str(e))
		sys.exit(1)

	if not repl_defs:
		log.info("No rules - bye.")
		sys.exit()

	# make tmp name based on hash input & timestamp of input_txt file
	tmp_filename = "svgfrags-%08x-%08x" % (
		hash(input) & 0xffffffff, 
		os.path.getmtime(input_txt)
	)
	atexit.register(cleanup, tmp_filename)

	if not os.path.exists(tmp_filename + ".dvi"):
		# 3. prepare LaTeX source
		tmp_lines = [
			'\\batchmode',
			'\\documentclass{article}',
			'\\pagestyle{empty}'
			'\\begin{document}',
		]
		for tex in repl_defs:
			tmp_lines.append(tex)	# each TeX expression at new page
			tmp_lines.append("\\newpage")

		# 4. write & compile TeX source
		tmp_lines.append("\end{document}")

		tmp = open(tmp_filename + '.tex', 'w')
		for line in tmp_lines:
			tmp.write(line + "\n")
		tmp.close()

		if which('latex'):
			exitstatus = os.system("latex %s.tex > /dev/null" % tmp_filename)
			if exitstatus:
				log.error("LaTeX failed - error code %d; check log file '%s.log'", exitstatus, tmp_filename)
				sys.exit(2)
		else:
			log.error("Program 'latex' isn't avaialable.")
			sys.exit(3)
	else:
		log.info("File %s not changed, used existing DVI file (%s)", input_txt, tmp_filename)


	# 5. Load DVI
	dvi = binfile(tmp_filename + ".dvi", 'rb')
	comment, (num, den, mag, u, l), page_offset, fonts = dviparser.dviinfo(dvi)
	unit_mm = num/(den*10000.0)
	scale = unit_mm * 72.27/25.4
	mag   = mag/1000.0


	# 6. Preload fonts used in DVI & other stuff
	fontsel.preload()
	missing = []
	for k in fonts:
		_, s, d, fontname = fonts[k]
		log.debug("Font %s=%s" % (k, fontname))
		#print "Font %s=%s" % (k, fontname)
		try:
			fontsel.create_DVI_font(fontname, k, s, d, setup.options.enc_methods)
		except fontsel.FontError, e:
			log.error("Can't find font '%s': %s" % (fontname, str(e)))
			missing.append((k, fontname))

	if missing:
		log.error("There were some unavailable fonts; list of missing fonts: %s" % (dvi.name, ", ".join("%d=%s" % kf for kf in missing)))
		sys.exit(1)


	# 7. Substitute
	eq_id_n = 0

	# helper functions
	def get_width(obj_id, default=0.0):
		ref = XML.getElementById(obj_id)
		if ref:
			return frags.get_width(ref)
		else:
			log.error("Object id=%s doesn't exists", obj_id)
			return default
	
	def get_height(obj_id, default=0.0):
		ref = XML.getElementById(obj_id)
		if ref:
			return frags.get_height(ref)
		else:
			log.error("Object id=%s doesn't exists", obj_id)
			return default

	SVG = EquationsManager(XML, 1.25 * mag, scale, unit_mm)
	for pageno, items in enumerate(repl_defs.values()):
		dvi.seek(page_offset[pageno])
		SVG.new_page()
		dvi2svg.convert_page(dvi, SVG)
		assert SVG.lastpage is not None, "Fatal error!"
		assert SVG.lastbbox is not None, "Fatal error!"

		if len(items) > 1:
			# there are more then one referenco to this TeX object, so
			# we have to **define** it, and then reference to, with <use>
			eq_id    = 'svgfrags-%x' % eq_id_n
			eq_id_n += 1
			SVG.lastpage.setAttribute('id', eq_id)
			XML.getElementsByTagName('defs')[0].appendChild(SVG.lastpage)
		else:
			# just one reference, use node crated by SVGDocument
			equation = SVG.lastpage
			eq_id = None

		
		# process
		for ((kind, value), tex, options) in items:
			px, py = options.position
			if px == 'inherit':
				if frags.istextnode(value):
					px = frags.get_anchor(value)
				else:
					px = 0.0
			
			# bounding box of equation
			(xmin, ymin, xmax, ymax) = SVG.lastbbox

			# enlarge with margin values
			xmin -= options.margin[0]
			xmax += options.margin[1]
			ymin -= options.margin[2]
			ymax += options.margin[3]

			# and calculate bbox's dimensions
			dx = xmax - xmin
			dy = ymax - ymin

			if eq_id is not None:
				# more then one reference, create new node <use>
				equation = XML.createElement('use')
				equation.setAttributeNS('xlink', 'xlink:href', '#'+eq_id)

			
			def put_equation(x, y, sx, sy):
				# calculate desired point in equation BBox
				xo = xmin + (xmax - xmin)*px
				yo = ymin + (ymax - ymin)*py

				# move (xo,yo) to (x,y)
				if sx == sy:
					equation.setAttribute(
						'transform',
						('translate(%s,%s)' % (SVG.c2s(x), SVG.c2s(y))) + \
						('scale(%s)'        %  SVG.s2s(sx)) + \
						('translate(%s,%s)' % (SVG.c2s(-xo), SVG.c2s(-yo)))
					)
				else:
					equation.setAttribute(
						'transform',
						('translate(%s,%s)' % (SVG.c2s(x), SVG.c2s(y))) + \
						('scale(%s,%s)'     % (SVG.s2s(sx), SVG.s2s(sy))) + \
						('translate(%s,%s)' % (SVG.c2s(-xo), SVG.c2s(-yo)))
					)
				return equation


			# string or text object
			if kind == 'string':
				object = value
				if options.scale == 'fit':
					log.warning("%s is a text object, can't fit to rectangle", value)
					sx = sy = 1.0
				else:
					sx, sy = options.scale
					if type(sx) is tuple:
						kind, val = sx
						sx = 1.0
						if kind == 'width':
							if val == 'this': pass # no scale
							else: # XML id
								sx = get_width(val[1][1:], dx)/dx
						elif kind == "height":
							if val == 'this': pass # no scale
							else: # XML id
								sx = get_height(val[1][1:], dx)/dx
						elif kind == "length":
							sx = val/dx
					
					if type(sy) is tuple:
						kind, val = sy
						sy = 1.0
						if kind == 'width':
							if val == 'this': pass # no scale
							else: # XML id
								sy = get_width(val[1][1:], dy)/dy
						elif kind == "height":
							if val == 'this': pass # no scale
							else: # XML id
								sy = get_height(val[1][1:], dy)/dy
						elif kind == "length":
							sy = val/dy
				
					if sx == "uniform":
						sx = sy
					if sy == "uniform":
						sy = sx
					

				# get <text> object coords
				x = frags.safe_float(object.getAttribute('x'))
				y = frags.safe_float(object.getAttribute('y'))

				# (DEBUG)
				if DEBUG:
					c = XML.createElement("circle")
					c.setAttribute("cx", str(x))
					c.setAttribute("cy", str(y))
					c.setAttribute("r",  "3")
					c.setAttribute("fill", 'red')
					object.parentNode.insertBefore(c, object)

				put_equation(x, y, sx, sy)

				# copy fill color from text node
				fill = object.getAttribute('fill') or \
				       frags.CSS_value(object, 'fill')
				if fill:
					equation.setAttribute('fill', fill)
					

				# insert equation into XML tree
				object.parentNode.insertBefore(equation, object)


			# explicity given point
			elif kind == 'point':
				if options.scale == 'fit':
					log.warning("%s is a text object, can't fit to rectangle", value)
					sx = sy = 1.0
				else:
					sx, sy = options.scale
					if type(sx) is tuple:
						kind, val = sx
						sx = 1.0
						if kind == 'width':
							if val == 'this': pass # no scale
							else: # XML id
								sx = get_width(val[1][1:], dx)/dx
						elif kind == "height":
							if val == 'this': pass # no scale
							else: # XML id
								sx = get_height(val[1][1:], dx)/dx
						elif kind == "length":
							sx = val/dx
					
					if type(sy) is tuple:
						kind, val = sy
						sy = 1.0
						if kind == 'width':
							if val == 'this': pass # no scale
							else: # XML id
								sy = get_width(val[1][1:], dy)/dy
						elif kind == "height":
							if val == 'this': pass # no scale
							else: # XML id
								sy = get_height(val[1][1:], dy)/dy
						elif kind == "length":
							sy = val/dy
				
					if sx == "uniform":
						sx = sy
					if sy == "uniform":
						sy = sx
				
				
				# insert equation into XML tree
				x, y = value
				XML.documentElement.appendChild(
					put_equation(x, y, sx, sy)
				)

			# rectangle or object with known bbox
			elif kind == 'id' or kind == 'rect':
				# get bounding box
				if kind == 'rect':
					Xmin, Ymin, Xmax, Ymax = value # rect
				else:
					Xmin, Ymin, Xmax, Ymax = frags.get_bbox(value) # object

				DX = Xmax - Xmin
				DY = Ymax - Ymin

				# reference point
				x  = Xmin + (Xmax - Xmin)*px
				y  = Ymin + (Ymax - Ymin)*py

				# and set default scale
				sx = 1.0
				sy = 1.0

				# Fit in rectangle
				if options.scale == 'fit':
					tmp_x = DX/(xmax - xmin)
					tmp_y = DY/(ymax - ymin)

					if tmp_x < tmp_y:
						sx = sy = tmp_x
					else:
						sx = sy = tmp_y
				else:
					sx, sy = options.scale
					if type(sx) is tuple:
						kind, val = sx
						sx = 1.0
						if kind == 'width':
							if val == 'this':
								sx = DX/dx
							else: # XML id
								sx = get_width(val[1][1:], dx)/dx
						elif kind == "height":
							if val == 'this':
								sx = DX/dx
							else: # XML id
								sx = get_height(val[1][1:], dx)/dx
						elif kind == "length":
							sx = val/dx
					
					if type(sy) is tuple:
						kind, val = sy
						sy = 1.0
						if kind == 'width':
							if val == 'this':
								sy = DY/dy
							else: # XML id
								sy = get_width(val[1][1:], dy)/dy
						elif kind == "height":
							if val == 'this':
								sy = DY/dy
							else: # XML id
								sy = get_height(val[1][1:], dy)/dy
						elif kind == "length":
							sy = val/dy
				
					if sx == "uniform":
						sx = sy
					if sy == "uniform":
						sy = sx
				#endif

				# move&scale equation
				put_equation(x, y, sx, sy)

				# and append to XML tree
				if kind == 'rect':
					XML.documentElement.appendChild(equation)
				else: # kind == 'id'
					# in case of existing object, place them
					# just "above" them
					pn = value.parentNode
					if value == pn.lastChild:
						pn.appendChild(equation)
					else:
						pn.insertBefore(equation, value.nextSibling)
	#for

	
	# 9. modify replaced <text> nodes according to options
	if setup.options.frags_removetext: # remove nodes
		for node in text_nodes:
			node.parentNode.removeChild(node)
	elif setup.options.frags_hidetext: # hide nodes
		for node in text_nodes:
			node.setAttribute('display', 'none')

	SVG.save(output_svg)


def cleanup(tmp_filename):
	"remove temporary files"
	extensions = ['.aux', '.log']
	if not setup.options.frags_keeptex:
		extensions.append('.tex')
	if not setup.options.frags_keepdvi:
		extensions.append('.dvi')
	for ext in extensions:
		frags.remove_file(tmp_filename + ext)


if __name__ == '__main__':
	import traceback
	try:
		main(sys.argv)
	except SystemExit, (code):
		sys.exit(code)
	except:
		if setup.options.print_traceback:
			traceback.print_exc(file=sys.stderr)
		else:
			exception, instance, _ = sys.exc_info()
			print >> sys.stderr, "Unexpeced error - %s: %s" % (exception.__name__, str(instance))
	
# vim: ts=4 sw=4 nowrap
