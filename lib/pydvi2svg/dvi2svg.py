#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
# $Id: dvi2svg.py,v 1.35 2007-03-14 20:07:33 wojtek Exp $
#
# pydvi2svg - main program
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republila.pl

# changelog
"""
14.03.2007
	- text generating reenabled
13.03.2007:
	- all cmdline parsing moved to conv/cmdopt.py
	- text generating disabled
12.03.2007
	- disabled fntnum_recode (due to svgfrags conflict)
11.03.2007
	- added fntnum_recode table -- a bit shorter files
10.03.2007
	- SVGGfxDocument: from method 'eop' & 'save' methods 'flush_rules',
	  'flush_chars' and 'flush_defs' were set apart
	- smaller output files (characters in some line are shifted relative
	  to first char in the line)
	- command line parsing moved to conv/cmdopts.py
 8.03.2007
	- a bit smaller output (+ function strip_0)
 7.03.2007
	- better command line parsing, now user can set name of
	  output file or set output directory
	- new switch --always-number
	- extended "bbox" keyword, now four number are accepted
	  (left/right & top/bottom margin)
	- two bugs fixed
 6.03.2007
	- calculate page bbox
	- --paper-size accepts keyword "bbox"
	- new switch --verbose
 3.03.2007
	- options are global (moved to setup.py)
	- new switches:
	  * --no-fontforge
	  * --no-fnt2meta
	- -paper-size accepts argument "query"
	- a bit shorter output (id string became shorter):
	  before:
	  * sample10001.svg = 123483
	  * sample10002.svg = 72777
	  * sample20001.svg = 90202
	  after:
	  * sample10001.svg = 113055 (-10kB)
	  * sample10002.svg = 66062  (-6.5kB)
	  * sample20001.svg = 83599  (-6.5kB)
 1.03.2007
    - fixed bug
16.10.2006
	- moved get_basename to utils.py
	- implementation of SVGTextDocument finished
15.10.2006
	- added --enc-methods switch
	- moved parse_enc_repl & parse_pagedef to utils.py
	- replaced function open_dvi with findfile.find_file call
14.10.2006
	- small fixes
13.10.2006
	- renamed class SVGDocument to SVGGfxDocument
	- both SVGGfxDocument & SVGTextDocument utilize utils.group_element
	  (code is much simplier)
12.10.2006
	- SVGTextDocument (started)
 6.10.2006
	- removed class fontDB, fontsel now provide these functions (*)
	- use logging module
	- added override encoding (--enc switch)
	- removed --update-cache switch
	- replaced --separate-files switch with --single-file
	- implemented --page-size switch

 4.10.2006
	- much smaller SVG output; characters with same scale factor
	  and y coordinate are grouped;

	  For example:

		<use x="0" y="10" transform="scale(0.5)" .../>
		<use x="1" y="10" transform="scale(0.5)" .../>
		<use x="2" y="10" transform="scale(0.5)" .../>
		<use x="3" y="11" transform="scale(0.5)" .../>
		<use x="4" y="11" transform="scale(0.5)" .../>
		<use x="5" y="11" transform="scale(0.5)" .../>

	  become

		<g transform="scale(0.5)">
			<g transform="translate(0,10)">
				<use x="0" .../>
				<use x="1" .../>
				<use x="2" .../>
			</g>
			<g transform="translate(0,11)">
				<use x="3" .../>
				<use x="4" .../>
				<use x="5" .../>
			</g>
		</g>

  2.10.2006
	- convert single pages
	- some fixes in rendering routines
	- fonts managed by external object, not render itself
	- added command line support
	- fixed font scale calculation
	- added separate class that produce SVG documents

 30.09.2006
 	- version 0.1 (based on previous experiments)
"""

import sys
import os
import xml.dom
import logging

import setup

# import modules
from conv import fontsel as font
from conv import utils
from conv import colors as colorspec
from conv import path_element
from conv import cmdopts

# import functions/classes
from conv.findfile		import find_file
from conv.binfile		import binfile
from conv.dviparser		import dviinfo as DVI_info, get_token as DVI_token
from conv.utils			import group_elements as group
from conv.unic			import name_lookup

class SVGGfxDocument(object):
	"Outputs glyphs"
	def __init__(self, mag, scale, unit_mm, page_size):
		self.mag		= mag		# magnification
		self.scale		= scale		# additional scale
		self.oneinch	= 25.4/unit_mm

		self.id			= set()
		self.bbox_cache = {}

		def strip_0(s):
			if s.find('.') > -1:
				s = s.rstrip('0')
				if s[-1] == '.':
					return s[:-1]
			return s

		self.scale2str = self.s2s = lambda x: strip_0("%0.5f" % x)
		self.coord2str = self.c2s = lambda x: strip_0("%0.3f" % x)

		implementation = xml.dom.getDOMImplementation()
		doctype = implementation.createDocumentType(
			"svg",
			"-//W3C//DTD SVG 1.1//EN",
			"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd")
		self.document = implementation.createDocument(None, "svg", doctype)

		# set SVG implementation
		self.svg      = self.document.documentElement
		self.svg.setAttribute  ('xmlns', 'http://www.w3.org/2000/svg')
		self.svg.setAttributeNS('xmlns', 'xmlns:xlink', "http://www.w3.org/1999/xlink")

		self.svg.setAttribute('width',  '%smm' % str(page_size[0]))
		self.svg.setAttribute('height', '%smm' % str(page_size[1]))

	def new_page(self):
		self.chars = []
		self.rules = []

	def put_char(self, putset, h, v, fntnum, dvicode, color=None):
		try:
			glyph, glyphscale, hadv = font.get_char(fntnum, dvicode)
			assert glyph is not None, (fntnum, dvicode)
		except KeyError:
			return 0.0

		self.id.add( (fntnum, dvicode) )

		H  = self.scale * (h + self.oneinch)
		V  = self.scale * (v + self.oneinch)

		self.chars.append( (fntnum, dvicode, H, V, glyphscale, color, putset) )
		return hadv

	def put_rule(self, h, v, a, b, color=None):
		self.rules.append( (h, v, a, b, color) )

	def eop(self):
		"Finish the page"

		s2s = self.scale2str
		c2s = self.coord2str

		# 0. get bounding box (if needed)
		if setup.options.use_bbox:
			xmin, ymin, xmax, ymax = self.get_page_bbox()

			xmin -= setup.options.bbox_margin_L
			ymin -= setup.options.bbox_margin_T
			xmax += setup.options.bbox_margin_R
			ymax += setup.options.bbox_margin_B

			dx = (xmax - xmin)*self.mag
			dy = (ymax - ymin)*self.mag
			self.svg.setAttribute("width",  c2s(dx))
			self.svg.setAttribute("height", c2s(dy))
			self.svg.setAttribute("viewBox", "%s %s %s %s" %
				(c2s(xmin*self.mag), c2s(ymin*self.mag), c2s(dx), c2s(dy))
			)

		elements = []

		# 1. make rules (i.e. filled rectangles)
		elements.extend( self.flush_rules() )

		# 2. process chars
		elements.extend( self.flush_chars() )

		# 3. append elements to page, and page to document
		self.lastpage = self.document.createElement('g')
		self.lastpage.setAttribute('transform', 'scale(%s)' % str(self.mag))
		self.svg.appendChild(self.lastpage)

		for element in elements:
			self.lastpage.appendChild(element)


	def get_page_bbox(self, element=None):
		"Returns bbox of chars (self.chars) and rules (self.reules)."

		new  = self.document.createElement
		X = []
		Y = []

		# bbox of chars
		for (fntnum, dvicode, H, V, glyphscale, color, _) in self.chars:
			try:
				bbox = self.bbox_cache[fntnum, dvicode]
			except KeyError:
				path   = font.get_char(fntnum, dvicode)[0]
				tokens = path_element.tokens(path)
				bbox   = path_element.bounding_box(tokens)
				self.bbox_cache[fntnum, dvicode] = bbox

			(xmin, ymin), (xmax, ymax) = bbox
			X.append(H+xmax*glyphscale)
			X.append(H+xmin*glyphscale)
			Y.append(V-ymax*glyphscale)
			Y.append(V-ymin*glyphscale)

			"""
			# blue background for char's bbox (TESTING)
			tmp = new('rect')
			tmp.setAttribute('fill',  '#aaf')
			tmp.setAttribute('x', str(H+xmax*glyphscale))
			tmp.setAttribute('y', str(V-ymax*glyphscale))
			tmp.setAttribute('width',  str(glyphscale * (xmin-xmax)))
			tmp.setAttribute('height', str(glyphscale * (ymax-ymin)))
			element.appendChild(tmp)
			"""

		# bbox of rules
		for (h,v, a, b, color) in self.rules:
			X.append(self.scale * (h + self.oneinch))
			X.append(self.scale * (h + self.oneinch + b))

			Y.append(self.scale * (v - a + self.oneinch))
			Y.append(self.scale * (v + self.oneinch))

		# get bbox
		xmin = min(X)
		xmax = max(X)

		ymin = min(Y)
		ymax = max(Y)

		"""
		# red frame around bbox (TESTING)
		tmp = new('rect')
		tmp.setAttribute("x", str(xmin))
		tmp.setAttribute("y", str(ymin))
		tmp.setAttribute("width",  str(xmax - xmin))
		tmp.setAttribute("height", str(ymax - ymin))
		tmp.setAttribute('fill',  'none')
		tmp.setAttribute('stroke','red')
		tmp.setAttribute('stroke-width', '2')
		element.appendChild(tmp)
		"""

		return xmin, ymin, xmax, ymax


	def flush_chars(self):
		new = self.document.createElement
		s2s = self.scale2str
		c2s = self.coord2str

		elements = []

		# (fntnum, dvicode, H, V, glyphscale, color)

		# group chars with same glyphscale
		byglyphscale = group(self.chars, value=lambda x: x[4])
		for (glyphscale, chars2) in byglyphscale:
			g = self.document.createElement('g')
			g.setAttribute('transform', 'scale(%s,%s)' % (s2s(glyphscale), s2s(-glyphscale) ))
			elements.append(g)

			# then group by V
			byV = group(chars2, value=lambda x: x[3])
			for (V, chars3) in byV:

				xo = chars3[0][2]/glyphscale # get X coords of first
				g1 = new('g')
				g1.setAttribute('transform', 'translate(%s,%s)' %
					(c2s(xo), c2s(-V/glyphscale))
				)
				g.appendChild(g1)

				for j, char in enumerate(chars3):
					c = new('use')
					g1.appendChild(c)
						
					H       = char[2]
					fntnum  = char[0]
					dvicode = char[1]
					color   = char[5]
					idref   = "#%02x%d" % (dvicode, fntnum)

					c.setAttributeNS('xlink', 'xlink:href', idref)
					if j > 0:
						c.setAttribute('x', c2s(H/glyphscale - xo))
					if color:
						c.setAttribute('fill', color)

		self.chars = []
		return elements
		#rof


	def flush_rules(self):
		new = self.document.createElement
		c2s = self.coord2str

		elements = []
		for (h,v, a, b, color) in self.rules:
			rect = new('rect')
			rect.setAttribute('x',      c2s(self.scale * (h + self.oneinch)))
			rect.setAttribute('y',      c2s(self.scale * (v - a + self.oneinch)))
			rect.setAttribute('width',  c2s(self.scale * b))
			rect.setAttribute('height', c2s(self.scale * a))
			if color:
				rect.setAttribute('fill', color)

			elements.append(rect)

		self.rules = []
		return elements


	def flush_glyphs(self):
		new = self.document.createElement

		elements = []
		for fntnum, dvicode in self.id:
			try:
				glyph, _, _ = font.get_char(fntnum, dvicode)
			except KeyError:
				continue

			path = new('path')
			path.setAttribute("id", "%02x%d" % (dvicode, fntnum))
			path.setAttribute("d",  glyph)
			elements.append(path)

		return elements


	def save(self, filename):
		# create defs
		defs = self.document.createElement('defs')
		self.svg.insertBefore(defs, self.svg.firstChild)

		for element in self.flush_glyphs():
			defs.appendChild(element)

		# save file
		f = open(filename, 'wb')
		if setup.options.prettyXML:
			f.write(self.document.toprettyxml())
		else:
			f.write(self.document.toxml())
		f.close()


class SVGTextDocument(SVGGfxDocument):
	"""
	Outputs text
	"""
	def flush_chars(self):
		new = self.document.createElement
		s2s = self.scale2str
		c2s = self.coord2str
		
		# (fntnum, dvicode, H, V, glyphscale, color, putset)
		elements = []

		# group chars typeseted with the same font
		byfntnum = group(self.chars, value=lambda x: x[0])
		for (fntnum, char_list) in byfntnum:
			g = new('g')
			elements.append(g)

			fnt   = font.get_font(fntnum)
			style = "font-family:%s; font-size:%0.1fpt" % (fnt.fontfamily, fnt.designsize)
			s,d   = fnt.sd
			if s != d:	# scaled font
				style += "; font-scale: %0.1f%%" % ((100.0*s)/d)

			g.setAttribute('style', style)

			def isglyphknown(fntnum, dvicode):
				try:
					return bool(name_lookup[font.get_char_name(fntnum, dvicode)])
				except KeyError:
					return False

			# (fntnum, dvicode, H, V, glyphscale, color, putset)
			def output_char_string(list):
				H     = list[0][2]
				V     = list[0][3]
				color = list[0][5]
				text  = ''.join([name_lookup[font.get_char_name(item[0], item[1])] for item in list])

				node = new('text')
				if color:
					node.setAttribute('fill', color)

				node.setAttribute('x', c2s(H))
				node.setAttribute('y', c2s(V))
				node.appendChild(self.document.createTextNode(text))
				return node

			# (fntnum, dvicode, H, V, glyphscale, color, putset)
			def output_char(char):
				H     = char[2]
				V     = char[3]
				color = char[5]
				text  = name_lookup[font.get_char_name(char[0], char[1])]

				node = new('text')
				if color:
					node.setAttribute('fill', color)

				node.setAttribute('x', c2s(H))
				node.setAttribute('y', c2s(V))
				node.appendChild(self.document.createTextNode(text))
				return node

			# find unknown chars
			for (known, char_list2) in group(char_list, lambda x: isglyphknown(x[0], x[1])):
				if not known:
					for char in char_list2:
						H = char[2]
						V = char[3]

						node = new('text')
						node.setAttribute('x', c2s(H))
						node.setAttribute('y', c2s(V))
						node.setAttribute('fill', 'red')
						node.appendChild(self.document.createTextNode('?'))
						g.appendChild(node)
				else:
					# group set_char commands
					for (set_char, char_list3) in group(char_list2, lambda x: x[6]):
						if set_char == 'set':
							for (color, char_list4) in group(char_list3, lambda x: x[5]):
								g.appendChild(output_char_string(char_list4))
						else:
							for char in char_list3:
								g.appendChild(output_char(char))
					#rof

		self.chars = []
		return elements
		#rof

	def save(self, filename):
		if setup.options.prettyXML:
			log.warning("Pretty XML is disabled in text mode")

		# save
		f = open(filename, 'wb')
		f.write(self.document.toxml(encoding="utf-8"))
		f.close()


def convert_page(dvi, document):

	h, v, w, x, y, z = 0,0,0,0,0,0	# DVI variables
	fntnum = None					# DVI current font number
	stack  = []						# DVI stack

	color  = None					# current color

	command     = None
	prevcommand = None

	while dvi:
		prevcommand  = command
		command, arg = DVI_token(dvi)

		if command == 'put_char':
			document.put_char('put', h, v, fntnum, arg, color)

		if command == 'set_char':
			if prevcommand == 'set_char':
				h += document.put_char('set', h, v, fntnum, arg, color)
			else:
				h += document.put_char('put', h, v, fntnum, arg, color)

		elif command == 'nop':
			pass
		elif command == 'bop':
			h, v, w, x, y, z = 0,0,0,0,0,0
			fntnum  = None
		elif command == 'eop':
			document.eop() # ok, we finished this page
			break
		elif command == 'push':
			stack.insert(0, (h, v, w, x, y, z))
		elif command == 'pop':
			(h, v, w, x, y, z) = stack.pop(0)
		elif command == 'right':
			h += arg
		elif command == 'w0':
			h += w
		elif command == 'w':
			b = arg
			w  = b
			h += b
		elif command == 'x0':
			h += x
		elif command == 'x':
			x  = arg
			h += arg
		elif command == 'down':
			v += arg
		elif command == 'y0':
			v += y
		elif command == 'y':
			y  = arg
			v += arg
		elif command == 'z0':
			v += z
		elif command == 'z':
			z  = arg
			v += arg
		elif command == 'fnt_num':
			#fntnum = fntnum_recode[arg] # recode fntnum, see comment marked with (A)
			fntnum = arg
		elif command == 'fnt_def':
			pass		# fonts are already loaded, nothing to do
		elif command == "pre":
			raise ValueError("'pre' command is not allowed inside page - DVI corrupted")
		elif command == "post":
			raise ValueError("'post' command is not allowed inside page - DVI corrupted")
		elif command == "put_rule":
			a, b = arg
			document.put_rule(h, v, a, b, color)

		elif command == "set_rule":
			a, b = arg
			document.put_rule(h, v, a, b, color)
			h += b

		elif command == "xxx":	# special
			if colorspec.is_colorspecial(arg):
				color, background = colorspec.execute(arg)
		else:
			raise NotImplementedError("Command '%s' not implemented." % command)

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

	# parse named args
	(setup.options, args) = cmdopts.parse_args()

	# parse positional args
	args = cmdopts.parse_pos_args(args)

	# set logging level
	if setup.options.verbose:
		logging.basicConfig(level=logging.DEBUG)

	log = logging.getLogger('dvi2svg')

	if not args:
		log.info("Nothing to do.")
		sys.exit()

	# load & process information about encoding
	font.preload(setup.options.enc_repl)

	for filename, basename in args:

		#
		# 1. Open file
		#
		dvi = binfile(filename, 'rb')
		log.info("Processing '%s' file -> '%s'", filename, basename)

		#
		# 2. Read DVI info
		#
		comment, (num, den, mag, u, l), page_offset, fonts = DVI_info(dvi)
		unit_mm = num/(den*10000.0)

		if mag == 1000: # not scaled
			log.debug("%s ('%s') has %d page(s)", dvi.name, comment, len(page_offset))
		else:           # scaled
			log.debug("%s ('%s') has %d page(s); magnification is %0.2f", dvi.name, comment, len(page_offset), mag/1000.0)

		#
		# 3. Preload fonts
		#


		# (A) Table use to recode font numbers.  For example if DVI
		# defines fonts 17, 18, 19, we use 0, 1, 2 -- it makes output
		# file a bit shorter.
		#fntnum_recode = dict((k, i) for i, k in enumerate(fonts.keys()))

		missing = []
		for k in fonts:
			_, s, d, fontname = fonts[k]
			log.debug("Font %s=%s" % (k, fontname))
			#print "Font %s=%s" % (k, fontname)
			try:
				#font.create_DVI_font(fontname, fntnum_recode[k], s, d, setup.options.enc_methods)
				font.create_DVI_font(fontname, k, s, d, setup.options.enc_methods)
			except font.FontError, e:
				log.error("Can't find font '%s': %s" % (fontname, str(e)))
				missing.append((k, fontname))

		if missing:
			log.info("There were some unavailable fonts, skipping file '%s'; list of missing fonts: %s" % (dvi.name, ", ".join("%d=%s" % kf for kf in missing)))
			continue

		#
		# 4. process pages
		#
		n = len(page_offset)
		if setup.options.pages is None:	# processing all pages
			pages = range(0, n)
		else: # processing selected pages
			try:
				tmp   = utils.parse_pagedef(setup.options.pages, 1, n)
				pages = [p-1 for p in tmp]
			except ValueError, e:
				log.warning("Argument of --pages switch has invalid syntax ('%s'), processing first page", setup.options.pages)
				pages = [0]

		# ok, write the file
		scale = unit_mm * 72.27/25.4
		mag   = mag/1000.0 * setup.options.scale

		if setup.options.generate_text:
			SVGDocument = SVGTextDocument
		else:
			SVGDocument = SVGGfxDocument

		if setup.options.single_file:
			svg = SVGDocument(1.25 * mag, scale, unit_mm, setup.options.paper_size)
			for i, pageno in enumerate(pages):
				log.info("Procesing page %d (%d of %d)", pageno+1, i+1, len(pages))
				dvi.seek(page_offset[pageno])
				svg.new_page()
				convert_page(dvi, svg)

			svg.save(basename + ".svg")
		else:
			n = len(pages)
			for i, pageno in enumerate(pages):
				log.info("Procesing page %d (%d of %d)", pageno+1, i+1, n)
				dvi.seek(page_offset[pageno])
				svg = SVGDocument(1.25 * mag, scale, unit_mm, setup.options.paper_size)
				svg.new_page()
				convert_page(dvi, svg)
				if n == 1 and not setup.options.always_number:
					svg.save(basename + ".svg")
				else:
					svg.save("%s%04d.svg" % (basename, pageno+1))
	#for

	sys.exit()

# vim: ts=4 sw=4 nowrap
