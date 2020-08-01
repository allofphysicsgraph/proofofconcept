# -*- coding: iso-8859-2 -*-
# $Id: cmdopts.py,v 1.7 2007-03-14 20:00:36 wojtek Exp $
#
# pydvi2svg - command line parsing
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
13.03.2007
	+ parse_pos_args
11.03.2007
	+ new
"""

import optparse
import logging

import utils
import sys
import os

from paper_size import paper_size

log = logging.getLogger('dvi2svg')


def parse_args(args=None):
	parser = optparse.OptionParser()

	parser.set_defaults(use_bbox=False)

	parser.add_option(
		"-p", "--pages",
		help	= "Comma separated list of pages or page ranges\
		           to convert, for example: 1-5,7-9,15,17,20-",
		dest  	= "pages",
		default	= None
	)
	
	parser.add_option(
		"--always-number",
		help	= "append page number to output name\
		           even if one page is converted",
		dest  	= "always_number",
		action	= "store_true",
		default	= False,
	)
	
	parser.add_option(
		"--paper-size",
		help	= """\
(a) set paper size (A4, B3, etc)
(b) string 'query' - print all know sizes, and quits
(c) string 'bbox' - bbox is calculated, additionaly
margins around bbox can be set, i.e. bbox:LRTB
(all same) or bbox:LR,TB (left=right & top=bot)
or bbox:L,R,T,B (all different)""",
		dest  	= "paper_size",
		type	= "string",
		action	= "callback",
		callback= parse_paper_size,
		default	= paper_size["A4"],
	)
	
	parser.add_option(
		"-s", "--scale",
		help	= "scale of document (default 1.0, i.e. no scale)",
		type	= "float",
		dest	= "scale",
		action	= "callback",
		callback= parse_scale,
		default	= 1.0,
	)
	
	parser.add_option(
		"--enc",
		help	= "encoding of fonts; comma separated list of pair font:encoding, for example: cmr10:ot1,pltt:t1",
		dest  	= "enc_repl",
		type	= "string",
		action	= "callback",
		callback= parse_enc_repl,
		default	= {},
	)

	parser.add_option(
		"--enc-methods",
		help	= "Methods use to resolve font encoding; \
		           comma-separated list of keywords: \
				   cache, tfm, afm, map, guess.  Default: \
				   cache,tfm,afm.",
		dest	= "enc_methods",
		type	= "string",
		action	= "callback",
		callback= parse_enc_methods,
		default	= "c,t,a"
	)
	
	parser.add_option(
		"--single-file",
		help	= "place all pages in single file; by default all\
		           pages are saved in separate files",
		dest  	= "single_file",
		action	= "store_true",
		default	= False,
	)

	parser.add_option(
		"-v", "--verbose",
		help	= "program is verbose, i.e. prints a lot of messages",
		dest  	= "verbose",
		action	= "store_true",
		default	= False,
	)

	parser.add_option(
		"--no-fontforge",
		help	= "do not use Fontforge, even if available",
		dest  	= "use_fontforge",
		action	= "store_false",
		default	= True,
	)

	parser.add_option(
		"--no-fnt2meta",
		help	= "do not use fnt2meta, even if available",
		dest  	= "use_fnt2meta",
		action	= "store_false",
		default	= True,
	)

	parser.add_option(
		"--generate-text",
		help	= "expremimental: output text instead of glyphs",
		dest  	= "generate_text",
		action	= "store_true",
		default	= False,
	)

	parser.add_option(
		"--pretty-xml",
		help	= "output nice formated XML, easy to read\
		           (debugging purposes)",
		dest  	= "prettyXML",
		action	= "store_true",
		default	= False,
	)

	if args is not None:
		return parser.parse_args(args)
	else:
		return parser.parse_args()


def parse_pos_args(args):
	"syntax: [DVI file [SVG file | dir]]+"
	import findfile
	
	def preprocess(filename):
		# directory? (output)
		if os.path.isdir(filename):
			return ('dir', filename)

		# DVI file? (input)
		dir, fname = os.path.split(filename)
		if dir == '': dir = '.'
		def dvipred(p, f):
			return f==fname or \
			       f==fname + '.dvi' or \
			       f==fname + '.DVI' or \
			       f==fname + '.Dvi'
		dvi = findfile.find_file(dir, dvipred, enterdir=lambda p, l: False)
		if dvi is not None:
			return ('dvi', dvi)

		# SVG file? (output)
		if filename.lower().endswith('.svg'):
			return ('svg', filename[:-4])

		# none, skipping
		log.info("File '%s' not found, skipping" % filename)
		return None

	tmp  = filter(bool, map(preprocess, args))
	args = []

	prev = tmp[0]
	for curr in tmp[1:] + [('dvi', None)]:
		t2, f2 = curr
		t1, f1 = prev
		prev   = curr

		if t1 == 'dvi':
			if t2 == 'svg':
				args.append( (f1, f2) )
			elif t2 == 'dir':
				basename = os.path.split(utils.get_basename(f1))[1]
				args.append( (f1, os.path.join(f2, basename)) )
			else:
				basename = os.path.split(utils.get_basename(f1))[1]
				args.append( (f1, basename) )
	
	return args
	


def parse_scale(option, opt_str, value, parser):
	if value <= 0.0:
		raise optparse.OptionValueError("--scale: number must be greater then 0")
	parser.values.scale = value


def parse_enc_methods(option, opt_str, value, parser):
	parser.values.enc_methods = utils.parse_enc_methods(value)


def parse_enc_repl(option, opt_str, value, parser):
	parser.values.enc_repl = utils.parse_enc_repl(value)


def parse_paper_size(option, opt_str, value, parser):
	# read paper size/print all known paper-size names
	value = value.upper()
	parser.values.use_bbox = False
	try:
		parser.values.paper_size = (pw, ph) = paper_size[value]
		log.debug("Paper size set to %s (%dmm x %dmm)", value, pw, ph)
		return
	except KeyError:
		pass # ok, maybe query or bbox passed
	
	if value == "QUERY":
		for name in sorted(paper_size.keys()):
			(pw, ph) = paper_size[name]
			print "%-4s: %dmm x %dmm" % (name, pw, ph)
		sys.exit()
	
	if value.startswith("BBOX"): # Bounding box
		parser.values.paper_size = (0.0, 0.0)
		parser.values.use_bbox = True

		# variants:
		#  1. BBOX
		#  2. BBOX:number
		#  3. BBOX:number,number
		#  4. BBOX:number,number,number,number
		
		mT = mB = mL = mR = 0.0
		if value.startswith("BBOX:"):
			tmp = value[5:].split(",", 4)
			if len(tmp) == 1: # BBOX:number
				mT = mB = mL = mR = abs(utils.safe_float(tmp[0]))
			elif len(tmp) == 2: # BBOX:number,number
				mL = mR = abs(utils.safe_float(tmp[0]))
				mT = mB = abs(utils.safe_float(tmp[1]))
			elif len(tmp) == 4: # BBOX:number,number,number,number
				mL = abs(utils.safe_float(tmp[0]))
				mR = abs(utils.safe_float(tmp[1]))
				mT = abs(utils.safe_float(tmp[2]))
				mB = abs(utils.safe_float(tmp[3]))
			else:
				log.warning("Bbox: invalid syntax, margins set to 0")

		parser.values.bbox_margin_L = mL
		parser.values.bbox_margin_R = mR
		parser.values.bbox_margin_T = mT
		parser.values.bbox_margin_B = mB
		log.debug("BBox margins: left=%0.2f, right=%0.2f, top=%0.2f, bottom=%0.2f", mL, mR, mT, mB)
	else:
		log.warning("Know nothing about paper size %s, defaults to A4" % value)
		parser.values.paper_size = paper_size['A4']

# vim: ts=4 sw=4 nowrap
