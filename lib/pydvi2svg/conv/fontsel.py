# -*- coding: iso-8859-2 -*-
# $Id: fontsel.py,v 1.20 2007-03-13 21:04:15 wojtek Exp $
#
# pydvi2svg - SVG fonts & char encoding utilities
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
 4.03.2007
	- mftrace support
 3.03.2007
	- fontforge/fntmeta issues
 2.03.2007
	- fixed bug in make_cache_file
	- better pfa/pfb detecting
13.11.2006
	- use findfile.which to detect Fontforge/fnt2meta
16.10.2006
	- removed is_font_supported, unavailable_fonts
	- use FontForge to convert (added fontforge_convert)
	- use own utility fnt2meta (added load_metadata & parse_metadata)
15.10.2006
	- removed get_encoding
	- encoding is now determined inside function create_DVI_font
14.10.2006
	- guess_encoding
	- split get_encoding: get_encoding_from_TFM, get_encoding_from_AFM,
	  get_encoding_from_cache, get_encoding_from_MAPfiles
13.10.2006
	- DVI font contains s and d (original scale saved in DVI file)
	- added get_char_name
	- added get_font
 6.10.2006
 	- added fontDB functions:
		- load fonts at given scale (create_DVI_font)
		- get glyph data, its scale and hadv for given char (get_char)
	- override encoding of font
	- permanently modify encoding (change file setup.font_lookup)
 5.10.2006
	- removed unused function
	- use logging module
 2.10.2006
    - remove SVGFont class
	- added following functions:
		* make_cache_file
		* get_glyph
		* get_height
		* glyph_info
		* font_info
		* unknown_fonts
 1.10.2006
 	- moved font releated functions from main program here
"""

import sys
import re
import os
import cPickle
import logging

import setup
import findfile
import encoding
import utils

from binfile  import binfile
from metrics  import read_TFM, TFMError, read_AFM, AFMError, read_MAP
from encoding import EncodingDB, EncodingDBError
from unic     import transcode, name_lookup

fnt2meta_available  = True
fontforge_available = True
mftrace_available   = True
fnt2meta_path = "fnt2meta"

# create encodingDB instance
encodingDB	= EncodingDB(setup.encoding_path, setup.tex_paths)

# get logger
log = logging.getLogger('fonts')

class FontError(Exception):
	pass

class Config(object):
	pass

config = Config()

# table use to translate long encoding names into shorter form
config.encoding_lookup	= {}

# dict contains trivial info about fonts: its
# encoding name (short form) and design size
config.fonts_lookup		= {}

# loaded fonts
config.fonts			= {}

# created DVI fonts
config.dvi_fonts		= {}

def create_DVI_font(fontname, k, s, d, findenc):
	"""
	Create a font identified by number k scaled with factor s/d.
	"""

	# load font
	fontdata = load_font(fontname)

	class DVIFont:
		pass

	font = DVIFont()
	font.name			= fontname
	font.fontfamily		= fontdata.fontfamily
	font.designsize		= fontdata.designsize
	font.sd				= (s,d)
	font.scale			= float(s)/d * fontdata.designsize/1000.0
	font.hadvscale		= float(s)/1000
	font.glyphs_dict	= fontdata.glyphs_dict


	enc = None
	new = False
	for method in findenc:
		if method == 'c':	# load from cache
			try:
				enc = config.fonts_lookup[fontname][0]
				if enc:
					log.debug("%s: font encoding is %s (cache)", fontname, enc)
					break
			except KeyError:
				pass

		elif method == 't':	# load from TFM
			try:
				enc = get_encoding_from_TFM(fontname)
				if enc:
					log.debug("%s: font encoding is %s (TFM)", fontname, enc)
					new = True
					break
			except TFMError, e:
				log.debug("TFMError: %s", str(e))

		elif method == 'a':	# load from AFM:
			try:
				enc = get_encoding_from_AFM(fontname)
				if enc:
					log.debug("%s: font encoding is %s (AFM)", fontname, enc)
					new = True
					break
			except AFMError, e:
				log.debug("AFMError: %s", str(e))

		elif method == 'm':	# grep MAP files
			enc = get_encoding_from_MAPfiles(fontname)
			if enc:
				log.debug("%s: font encoding is %s (MAP)", fontname, enc)
				new = True
				break

		elif method == 'g':	# compare with all ENC files
			glyph_names = set(font.glyphs_dict.keys())
			enc_list    = guess_encoding(glyph_names)

			if enc_list:
				if len(enc_list) == 1:	# ok(?), one enc file
					enc = enc_list[0][0]
					new = True
					log.debug("%s: font encoding is %s (ENC)", fontname, enc)
				else:
					tmp = ', '.join([v[0] for v in enc_list])
					raise FontError("Guess encoding: found more then one encoding file that matches '%s'.  Here is a list of files: %s" % (fontname, tmp))
				
	#rof
	
	if not enc:
		raise FontError("Can't determine encoding of font '%s'.  Provide this information with --enc switch." % fontname)
	
	if 'c' not in findenc and new:
		log.debug("Adding information about new font to '%s': %s@%fpt, enc. %s" % (
			setup.font_lookup,
			font.name,
			font.designsize,
			enc)
		)
		file = open(setup.font_lookup, 'a')
		file.write("%s\t\t%s\t\t%s\n" % (font.name, enc, str(font.designsize)))
		file.close()
	
	
	font.encoding = encodingDB.getencodingtbl(enc)
	config.dvi_fonts[k] = font

def get_font(fontnum):
	return config.dvi_fonts[fontnum]

def get_char_name(fontnum, dvicode):
	font = config.dvi_fonts[fontnum]
	return font.encoding[dvicode]

def get_char(fontnum, dvicode):
	"""
	Returns following data releated to character:
	- glyph (shape)
	- shape scale factor needed to fit current font size
	- width of char in TeX units
	"""
	font = config.dvi_fonts[fontnum]

	glyphname = font.encoding[dvicode]
	try:
		glyph = font.glyphs_dict[glyphname]
		return glyph.path, font.scale, glyph.hadv * font.hadvscale
	except KeyError, e:
		log.error("%s: missing char '%s' (%d=0x%02x)", font.name, glyphname, dvicode, dvicode)
		raise e


def preload(enc_repl={}):
	global fontforge_available
	global fnt2meta_available
	global mftrace_available
	global fnt2meta_path

	mftrace_available   = findfile.which('mftrace') != None
	fontforge_available = findfile.which('fontforge') != None
	fnt2meta_available  = findfile.which('fnt2meta') != None
	if not fnt2meta_available:
		tmp = os.path.join(os.path.dirname(__file__), 'fnt2meta')
		if os.path.isfile(tmp):
			fnt2meta_path = tmp
			fnt2meta_available = True
	
	def yesno(val):
		if val: return 'yes'
		else:   return 'no'

	log.debug('Fontforge available: %s', yesno(fontforge_available))
	log.debug('fnt2meta available: %s', yesno(fnt2meta_available))
	log.debug('mftrace available: %s', yesno(mftrace_available))

	log.debug("Loading encoding names lookup from '%s'" % setup.enc_lookup)
	load_enc_lookup()

	log.debug("Loading font info from '%s'" % setup.font_lookup)
	load_font_info()
	for fontname, newenc in enc_repl.iteritems():
		if fontname not in config.fonts_lookup:
			log.debug("Encoding of '%s' set to %s", fontname, newenc)
			config.fonts_lookup[fontname] = (newenc, 10.0)
		else:
			enc, ds = config.fonts_lookup[fontname]
			if enc != newenc:
				log.debug("Encoding of '%s' chenged to %s (from %s)", fontname, newenc, enc)
				config.fonts_lookup[fontname] = (newenc, ds)


def load_font(fontname):
	try:
		font = config.fonts[fontname]
		log.debug("Getting font '%s' from cache" % fontname)
	except KeyError:
		filename = os.path.join(setup.cache_path + fontname.lower() + '.cache')
		if not os.path.exists(filename):
			log.debug("Cache file for '%s' font does not exists -- creating one" % fontname)
			make_cache_file(fontname)
			config.fonts[fontname] = font = cPickle.load(open(filename, 'rb'))
		else:
			log.debug("Loading font '%s' from cache file" % fontname)
			config.fonts[fontname] = font = cPickle.load(open(filename, 'rb'))

	return font


def load_enc_lookup():
	try:
		file = open(setup.enc_lookup, 'r')
		log.debug("Parsing file '%s'..." % setup.enc_lookup)
	except IOError:
		log.debug("... file '%s' not found" % setup.enc_lookup)

	for i, line in enumerate(file):
		# skip blank or commented lines
		line = line.strip()
		if not line or line[0] == '#':
			continue

		try:
			# line not empty, parse
			eqpos = line.rfind('=')
			if eqpos > -1:
				encodingname, encfile = line.rsplit('=', 2)
				encodingname = encodingname.strip()
				encfile      = encfile.strip()
				config.encoding_lookup[encodingname] = encfile
				log.debug("... line %d: '%s'=%s" % (i+1, encodingname, encfile))
			else:
				raise ValueError
		except ValueError:
			# wrong number of fields
			log.warning("... line %d has wrong format, skipping" % (i+1))
			continue

	file.close()

def load_font_info():
	try:
		file = open(setup.font_lookup, 'r')
		log.debug("Parsing file '%s'..." % setup.font_lookup)
	except IOError:
		log.debug("... file '%s' not found" % setup.font_lookup)
		return

	for i, line in enumerate(file):
		# skip blank or commented lines
		line = line.strip()
		if not line or line[0] == '#':
			continue

		try:
			fontname, encoding, designsize = line.split()
			if fontname not in config.fonts_lookup:
				config.fonts_lookup[fontname] = (encoding, float(designsize))
				log.debug("... line %d: %s @ %spt, enc. %s" % (
					i+1,
					fontname,
					str(float(designsize)),
					encoding,
				))
			else:
				log.warning("... line %d: font %s - duplicated entry ignored" % (i+1, fontname))
		except ValueError:
			# wrong number of fields
			log.waring("... line %d has wrong format, skipping" % (file.name, i+1))
			continue

	file.close()

def get_encoding_from_TFM(fontname):
	log.debug('checking TFM file')
	filename = findfile.locate(fontname + '.tfm', setup.tex_paths)
	if filename:
		log.debug("... using '%s'" % filename)
		file = binfile(filename, 'rb')
		try:
			_, _, encodingname, _ = read_TFM(file)
		except TFMError, e:
			log.error("... TFM error: %s" % str(TFMError))
		else:
			file.close()
			try:
				encoding = config.encoding_lookup[encodingname]
				log.debug("... encoding %s" % encoding)
				return encoding
			except KeyError:
				log.error("... font %s: unknown TeX encoding: '%s'" % (fontname, encodingname))
	else:
		log.debug("... TFM file not found")
		return None

def get_encoding_from_AFM(fontname):
	log.debug('checking AFM file')
	filename = findfile.locate(fontname + '.afm', setup.tex_paths)
	if filename:
		log.debug("... using '%s'" % filename)
		file = open(filename, 'r')
		try:
			encodingname, _, _ = read_AFM(file)
		except AFMError, e:
			log.error("... AFM error" + str(AFMError))
		else:
			file.close()
			try:
				if encodingname:
					encoding = config.encoding_lookup[encodingname]
					log.debug("... ... encoding %s" % encoding)
					return encoding
				else:
					log.error("... unknown AFM encoding: '%s'" % encodingname)
			except KeyError:
				log.error("... unknown AFM encoding: '%s'" % encodingname)
	else:
		log.debug("... AFM file not found")
		return None


tex_map_file_list = None
def get_encoding_from_MAPfiles(fontname):
	global tex_map_file_list

	log.debug("... checking map files")
	if tex_map_file_list != None:
		log.debug("... ... list of map files is present.")
	else:
		log.debug("... ... list of map files dosn't exists - getting one (it may take a while...)")

		def mappred(path, filename):
			return filename.endswith('.map')

		tex_map_file_list = findfile.find_all_files(setup.tex_paths, mappred)

	for filename in tex_map_file_list:
		log.debug("... ... ... scanning %s" % filename)
		enc = read_MAP(filename, fontname)
		if enc:
			log.debug("... ... ... encoding %s" % enc)
			return enc

enc_file_list = None
def guess_encoding(font_names):
	global enc_file_list

	log.debug("... checking enc files")
	if enc_file_list != None:
		log.debug("... enc files already loaded")
	else:
		log.debug("... searching for enc files")
		dirs      = [setup.encoding_path] + setup.tex_paths

		def encpred(path, filename):
			return filename.endswith('.enc')

		enc_file_list = []
		enc_files     = findfile.find_all_files(dirs, encpred)

		for file_path in enc_files:
			try:
				name_list = set(encoding.read_ENC(open(file_path, 'r'))[1])
				enc_file_list.append( (file_path, name_list) )
			except encoding.ENCFileError, e:
				log.debug("ENCFileError: %s" % str(e))

	min_diff = 256*4
	all      = []
	for file_path, enc_names in enc_file_list:
		diff = len(font_names.difference(enc_names))
		all.append( (file_path, diff) )
		if diff < min_diff:
			min_diff = diff

	# return best matching
	return [v for v in all if v[1] == min_diff]


def get_designsize(fontname):
	"""
	Function (tries to) determine designsize of given font.

	First checks a cache (loaded from setup.font_lookup),
	then seeks for corresponding TFM file and reads designsize.
	"""
	if fontname in config.fonts_lookup:
		encoding, designsize = config.fonts_lookup[fontname]
		log.debug("Getting designsize for '%s' from file cache" % fontname)
		return designsize

	# read TFM, if any
	log.debug('Checking TFM file...')
	filename = findfile.locate(fontname + '.tfm', setup.tex_paths)
	if filename:
		log.debug("Using file '%s'" % filename)
		file = binfile(filename, 'rb')
		try:
			_, designsize, _, _ = read_TFM(file)
		except TFMError, e:
			log.error("TFM error" + str(TFMError))
		else:
			file.close()
			return designsize / (2.0**20)
	else:
		log.warning("No TFM file found, default value 10.0 have been assumed")
		return 10.0

re_number	= re.compile('(\d+)')
re_mapping	= re.compile("^([0-9a-fA-F]{4}) N (.+)")

class Font:
	pass

class Glyph:
	def __init__(self):
		self.path    = ""
		self.unicode = u""
		self.name    = ""

def make_cache_file(fontname):

	font = Font()
	font.name = fontname

	#
	# 1. Locate/create SVG font
	#

	svgname = fontname.lower() + '.svg'
	def svgpred(path, filename):
		return filename.lower() == svgname

	filename = findfile.find_file(setup.svg_font_path, svgpred)
	if not filename:
		type1file = findfile.locate(fontname + '.pfb') or \
		            findfile.locate(fontname + '.pfa')

		if not type1file:
			# there is no pfa/pfb named fontname,
			# try to find pfa/pfb with some prefix as fontname
			
			# XXX: rewrite
			import string
			prefix = fontname.translate(string.maketrans("0123456789", " "*10)).split()[0]
			if prefix:
				def pred(path, filename):
					f = filename.lower()
					return f.startswith(prefix) and\
					       (f.endswith(".pfa") or f.endswith(".pfb"))
				type1file = findfile.find_file(setup.tex_paths, pred)

		if type1file:
			log.info("Found Type1 font: %s" % type1file)
			if setup.options.use_fontforge and fontforge_available:
				log.info("... trying FontForge")
				if fontforge_convert(type1file):
					filename = findfile.find_file(setup.svg_font_path, svgpred)
					log.info("... ... conversion successful!")
				else:
					log.info("... ... conversion failed")

			if not filename and setup.options.use_fnt2meta and fnt2meta_available:
				log.info("... trying fnt2meta")
				meta = load_metadata(type1file)
				if meta:
					font = parse_metadata(meta)
					font.designsize = get_designsize(fontname)
					log.debug("Font '%s' designed at %spt" % (fontname, str(font.designsize)))
					log.info("... conversion successful")
				
					# pickle
					f = open(setup.cache_path + fontname + '.cache', 'wb')
					cPickle.dump(font, f, protocol=cPickle.HIGHEST_PROTOCOL)
					f.close()
					return
				else:
					log.info("... ... conversion failed")
		#fi
	
	if not filename and not type1file:
		mffile = findfile.locate(fontname + '.mf')
		if mffile:
			log.info("METAFONT source found, trying mftrace...")
			if mftrace_convert(mffile):
				filename = findfile.find_file(setup.svg_font_path, svgpred)
				if filename:
					log.info("... ... conversion successful")
				else:
					log.info("... ... conversion failed")
			else:
				log.info("... ... conversion failed")
				
		

	if filename:
		log.debug("Using SVG font '%s' as '%s'", filename, font.name)
	else:
		if type1file:
			raise FontError("%s: suitable vector font found, but conversion failed (are FontForge or/and fnt2meta installed?)" % font.name)
		else:
			raise FontError("%s: can't find SVG font" % font.name)

	# get designsize
	font.designsize = get_designsize(fontname)
	log.debug("Font '%s' designed at %spt" % (fontname, str(font.designsize)))

	#
	# 2. Process SVG file
	#

	# a. load file
	from xml.dom.minidom import parse
	data = parse(filename)

	# b. get font element
	try:
		fontnode = data.getElementsByTagName('font')[0]
		# get default horizontal advance (if any)
		if fontnode.hasAttribute('horiz-adv-x'):
			default_hadvx = float(fontnode.getAttribute('horiz-adv-x'))
		else:
			default_hadvx = None
	except IndexError:
		raise FontError("There should be at least one <font> element in SVG file")

	# d. get font face name
	if fontnode.getAttribute('font-family'):
		font.fontfamily = fontnode.getAttribute('font-family')
	else:
		font.fontfamily = fontname

	try:
		fontface = data.getElementsByTagName('font-face')[0]
		if fontface.getAttribute('bbox') and fontface.getAttribute('units-per-em'):
			xmin,ymin, xmax,ymax = map(float, fontface.getAttribute('bbox').replace(",", " ").split())
			upem = float(fontface.getAttribute('units-per-em'))
#			raise str((upem, (ymax-ymin)))
	except IndexError:
		pass

	# e. load fonts
	font.glyphs_dict = {}
	for node in fontnode.getElementsByTagName('glyph'):

		# 1. read path info
		glyph = Glyph()
		if node.hasAttribute('d'):	# is defined as <glyph> attribute
			glyph.path = node.getAttribute('d')
		else:
			# XXX: glyph is defined with path child element and I assume
			#      there is just one element
			path_elements = node.getElementsByTagName('path')
			if len(path_elements) == 0:		# no path elements at all
				pass
			elif len(path_elements) == 1:	# one path element
				glyph.path = path_elements[0].getAttribute('d')
			else: # more paths...
				pass # XXX: join them?

		# 2. get character name
		glyph.name = node.getAttribute('glyph-name')
		if glyph.name == '':
			log.error("There is a glyph without name, skipping it")
			continue

		# 2a. transcode
		if glyph.name not in name_lookup:
			try:
				glyph.name = transcode[glyph.name]
			except KeyError:
				log.error("Don't know what is '%s', skipping it", glyph.name)
				continue

		# 3. get horiz-adv-x
		if node.hasAttribute('horiz-adv-x'):
			glyph.hadv = float(node.getAttribute('horiz-adv-x'))
		elif default_hadvx != None:
			glyph.hadv = default_hadvx
		else:
			# XXX: calculate glyphs extends?
			raise FontError("Can't determine width of character '%s'", glyph.name)

		if glyph.name in font.glyphs_dict:
			log.error("Character '%s' already defined, skipping", glyph.name)
		else:
			font.glyphs_dict[glyph.name] = glyph
	#rof

	# f. write the cache file
	cPickle.dump(font, open(setup.cache_path + fontname + '.cache', 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)


def load_metadata(filename):
	global fnt2meta_available

	if fnt2meta_available:
		stdout     = os.popen('%s %s' % (fnt2meta_path, filename), 'r')
		meta       = stdout.readlines()
		exitstatus = stdout.close()
		if exitstatus:
			if exitstatus >> 8 == 127: fnt2meta_available = False
			return None
		else:
			return meta
	else:
		return None

def parse_metadata(text):
	font  = Font()
	cpx   = 0
	cpy   = 0
	lastx = 0
	lasty = 0

	for line in text:
		fields  = line.split()
		command = fields[0]
		if command == 'family':
			font.fontfamily  = " ".join(fields[1:])
			font.designsize  = 10.0	# XXX: caller have to determine this value
			font.glyphs_dict = {}
		elif command == 'char':
			glyph = Glyph()

			glyph.name = fields[1]
			d     = []
			lastx = 0
			lasty = 0
		elif command == 'adv':
			glyph.hadv = int(fields[1])
		elif command == 'end':
			# skip missing glyph
			if glyph.name != '.notdef' and d:	
				glyph.path = ''.join(d)
				font.glyphs_dict[glyph.name] = glyph

		#
		# path commands
		#

		# moveto
		elif command == 'M':
			cpx, cpy = int(fields[1]), int(fields[2])
			lastx = cpx
			lasty = cpy
			d.append("M%d,%d" % (cpx, cpy))
	
		# lineto
		elif command == 'L':
			x, y = int(fields[1]), int(fields[2])

			# close path
			if x == lastx and y == lasty:
				d.append("z")

			# vert line
			elif x == cpx: 
				d.append("V%d" % y)

			# horiz line
			elif y == cpy:
				d.append("H%d" % x)

			else:
				d.append("L%d,%d" % (x,y))
				
			cpx, cpy = x, y

		# quadric_to (conic, in freetype nomenclature)
		if command == 'Q':
			cp2x, cp2y = int(fields[1]), int(fields[2])
			cp3x, cp3y = int(fields[3]), int(fields[4])
			d.append("Q%d,%d %d,%d" % (cp2x,cp2y, cp3x,cp3y))

			cpx, cpy = cp3x, cp3y
		
		# cubic to
		if command == 'C':
			cp2x, cp2y = int(fields[1]), int(fields[2])
			cp3x, cp3y = int(fields[3]), int(fields[4])
			cp4x, cp4y = int(fields[5]), int(fields[6])
			d.append("C%d,%d %d,%d %d,%d" % (cp2x,cp2y, cp3x,cp3y, cp4x,cp4y))

			cpx, cpy = cp4x, cp4y

	return font


def fontforge_convert(fullpath):
	global fontforge_available
	if not fontforge_available:
		return False

	path, file = os.path.split(fullpath)
	target     = os.path.join(setup.svg_font_path, utils.basename(file)+'.svg')
	cmd = "fontforge -c 'Open($1); Generate($2)' %s %s" % (fullpath, target)
	exitstatus = os.system(cmd)
	if exitstatus:
		if exitstatus >> 8 == 127:
			fontforge_available = False
		return False
	else:
		return True


def mftrace_convert(mffile):
	global mftrace_available

	mfname = os.path.split(mffile)[1][:-3] # just name is needed, no path, no extension

	cmd = "cd %s; mftrace --formats=svg %s" % (setup.svg_font_path, mfname)
	exitstatus = os.system(cmd)
	if exitstatus:
		if exitstatus >> 8 == 127:
			mftrace_available = False
		return False
	else:
		return True


# vim: ts=4 sw=4 noexpandtab nowrap
