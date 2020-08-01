# -*- coding: iso-8859-2 -*-
# $Id: metrics.py,v 1.6 2007-03-13 21:04:15 wojtek Exp $
#
# pydvi2svg - reading TFM, MAP & AFM files
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
 14.10.2006
 	- fixed bug in read_MAP
  5.10.2006
	- added AFMError exception
	- read_MAP (not releated, but goes here)
  3.10.2006
	- read_AFM, read_TFM
"""

class TFMError(Exception):
	pass

class AFMError(Exception):
	pass

import re

afm_char_metrics = re.compile("^C (\d+) ; WX (\d+) ; N (.+) ; B")
def read_AFM(file):
	encodingname = None
	processing_char_metrics = False

	char_width = [None for _ in xrange(256)]
	char_name  = [None for _ in xrange(256)]
	for i, line in enumerate(file):
		if i==0 and not line.startswith('StartFontMetrics'):
			raise AFMError("Not a AFM file")
		if line.startswith('EncodingScheme'):
			encodingname = line.split(None, 2)[1]
		if line.startswith('StartCharMetrics'):
			processing_char_metrics = True
		elif line.startswith('EndCharMetrics'):
			break
		elif processing_char_metrics:
			match = afm_char_metrics.match(line)
			if match:
				code  = int(match.group(1))
				width = int(match.group(2))
				name  = match.group(3)
				char_width[code] = width
				char_name[code]  = name
	
	if not len(char_width):
		raise AFMError("AFM file does not contain any metric data")

	if encodingname == 'FontSpecific':
		return None, char_width, char_name
	else:
		return encodingname, char_width, char_name

def read_TFM(file):
	"""
	Read following information from a TFM file:
	* checksum
	* designsize
	* encoding name
	* array of characters width
	"""
	lf = file.uint16()
	lh = file.uint16()
	bc = file.uint16()
	ec = file.uint16()
	nw = file.uint16()
	nh = file.uint16()
	nd = file.uint16()
	ni = file.uint16()
	nl = file.uint16()
	nk = file.uint16()
	ne = file.uint16()
	np = file.uint16()

	#
	# 1. Check file format (is it TFM file?)
	#
	try:
		assert bc-1 <= ec <= 255
		assert ne <= 256                                  
		assert lf == 6+lh+(ec-bc+1)+nw+nh+nd+ni+nl+nk+ne+np 
	except AssertionError:
		raise TFMError("Not a TFM file")

	#
	# 2. Read header (get checksum, designsize and encoding name)
	#
	try:
		assert lh >= 12

		checksum   = file.uint32()
		designsize = file.int32()	# fixed point

		length     = file.uint8()	# length of encoding string
		encoding   = file.read(10*4-1)[:length]
		file.seek((lh-12)*4, 1)
	except AssertionError:
		raise TFMError("TFM header does not contains encoding name")

	char_info   = [file.uint32() for _ in xrange(bc, ec+1)]
	width_table = [file.uint32() for _ in xrange(0,  nw)]

	width = [None for _ in xrange(256)]
	for i, info in enumerate(char_info):
		code        = i + bc
		index       = info >> 24
		width[code] = width_table[index]

	return (checksum, designsize, encoding, width)


def read_MAP(filename, fontname):
	comment_chars = "%@"
	file = open(filename, 'r')

	pfa = "<%s.pfa" % fontname
	pfb = "<%s.pfb" % fontname
	enc = None
	for line in file:
		# skip empty or commented lines
		line = line.strip()
		if not line or (line[0] in comment_chars):
			continue

		if line.endswith(pfb) or line.endswith(pfa):
			tmp = line.split()
			if len(tmp) > 1:
				tmp = tmp[-2]
				if tmp[0] == '<' and tmp.endswith('.enc'):
					enc = tmp[1:-4]
					break

	file.close()
	return enc

# vim: ts=4 sw=4
