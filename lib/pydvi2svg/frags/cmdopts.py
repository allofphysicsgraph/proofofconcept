# -*- coding: iso-8859-2 -*-
# $Id: cmdopts.py,v 1.8 2007-03-13 21:03:19 wojtek Exp $
#
# SVGfrags - command line parsing
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl/

# changelog
"""
13.03.2007
	+ '--traceback'
"""

import optparse
import conv.utils

def parse_args(args=None):
	parser = optparse.OptionParser()
	
	# SVGfrags options
	parser.add_option(
		"-i", "--input",
		help	= "Name of input SVG file",
		dest	= "input_svg",
		default	= ""
	)

	parser.add_option(
		"-o", "--output",
		help	= "Name of output SVG file",
		dest	= "output_svg",
		default	= ""
	)

	parser.add_option(
		"-r", "--rules",
		help	= "Name of text file that contains replacement pairs",
		dest	= "input_txt",
		default	= ""
	)
	
	parser.add_option(
		"--no-strip",
		help	= "Do not strip leading & trailing spaces from strings",
		dest	= "frags_strip",
		action	= "store_false",
		default	= True,
	)

	parser.add_option(
		"--keep-tex",
		help	= "Do not remove temporary TeX files (useful for debugging)",
		dest	= "frags_keeptex",
		action	= "store_true",
		default	= False,
	)

	parser.add_option(
		"--keep-dvi",
		help	= "Do not remove temporary DVI files.  By default they are keep, and can be re-use",
		dest	= "frags_keepdvi",
		action	= "store_true",
		default	= False,
	)

	parser.add_option(
		"--no-hide-text-obj",
		help	= "Do not hide replaced <text> nodes.",
		dest	= "frags_hidetext",
		action	= "store_false",
		default	= True,
	)

	parser.add_option(
		"--remove-text-obj",
		help	= "Remove from SVG replaced <text> nodes",
		dest	= "frags_removetext",
		action	= "store_true",
		default	= False,
	)

	parser.add_option(
		"-f", "--force-overwrite",
		help	= "Overwrite existing file",
		dest	= "frags_overwrite_file",
		action	= "store_true",
		default	= False,
	)

	parser.add_option(
		"--traceback",
		help	= "Print full error message",
		dest	= "print_traceback",
		action	= "store_true",
		default	= False,
	)

	# DVI engine options
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

	if args is not None:
		return parser.parse_args(args)
	else:
		return parser.parse_args()


def parse_enc_repl(option, opt_str, value, parser):
	parser.values.enc_repl = utils.parse_enc_repl(value)


def parse_enc_methods(option, opt_str, value, parser):
	parser.values.enc_methods = utils.parse_enc_methods(value)


# vim: ts=4 sw=4 nowrap
