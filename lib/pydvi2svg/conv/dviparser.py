# -*- coding: iso-8859-2 -*-
# $Id: dviparser.py,v 1.7 2007-03-13 21:04:15 wojtek Exp $
#
# pydvi2svg - DVI releated function (tokenizer, basic info about document)
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
 02.10.2006
 	- added dviinfo function
 25.09.2006
 	- fixed command number in get_token
 xx.09.2006
  	- first version (including binfile class, now moved out)
"""

def get_token(reader):
	command = reader.uint8()
	if command <= 127: # set_char_i (0-127)
		return ("set_char", command)
	elif command == 128: # set1
		return ("set_char", reader.uint8())
	elif command == 129: # set2
		return ("set_char", reader.uint16())
	elif command == 130: # set3
		return ("set_char", reader.uint24())
	elif command == 131: # set4
		return ("set_char", reader.uint32())

	elif command == 132: # set_rule
		a, b = reader.uint32(), reader.uint32()
		return ("set_rule", (a,b))

	elif command == 133: # put1
		return ("put", reader.uint8())
	elif command == 134: # put2
		return ("put", reader.uint16())
	elif command == 135: # put3
		return ("put", reader.uint24())
	elif command == 136: # put4
		return ("put", reader.uint32())

	elif command == 137: # put_rule
		a, b = reader.uint32(), reader.uint32()
		return ("put_rule", (a, b))
	elif command == 138: # nop
		return ("nop", None)
	elif command == 139: # bop
		c0 = reader.uint32()
		c1 = reader.uint32()
		c2 = reader.uint32()
		c3 = reader.uint32()
		c4 = reader.uint32()
		c5 = reader.uint32()
		c6 = reader.uint32()
		c7 = reader.uint32()
		c8 = reader.uint32()
		c9 = reader.uint32()
		p  = reader.int32()
		return ("bop", (c0,c1,c2,c3,c4,c5,c6,c7,c8,c9, p))
	elif command == 140: # eop
		return ("eop", None)
	elif command == 141: # push
		return ("push", None)
	elif command == 142: # pop
		return ("pop", None)

	elif command == 143: # right1
		return ("right", reader.int8())
	elif command == 144: # right2
		return ("right", reader.int16())
	elif command == 145: # right3
		return ("right", reader.int24())
	elif command == 146: # right4
		return ("right", reader.int32())
	
	elif command == 147: # w0
		return ("w0", None)
	elif command == 148: # w1
		return ("w", reader.int8())
	elif command == 149: # w2
		return ("w", reader.int16())
	elif command == 150: # w3
		return ("w", reader.int24())
	elif command == 151: # w4
		return ("w", reader.int32())

	elif command == 152: # x0
		return ("x0", None)
	elif command == 153: # x1
		return ("x", reader.int8())
	elif command == 154: # x2
		return ("x", reader.int16())
	elif command == 155: # x3
		return ("x", reader.int24())
	elif command == 156: # x4
		return ("x", reader.int32())
	
	elif command == 157: # down1
		return ("down", reader.int8())
	elif command == 158: # down2
		return ("down", reader.int16())
	elif command == 159: # down3
		return ("down", reader.int24())
	elif command == 160: # down4
		return ("down", reader.int32())
	
	elif command == 161: # y0
		return ("y0", None)
	elif command == 162: # y1
		return ("y", reader.int8())
	elif command == 163: # y2
		return ("y", reader.int16())
	elif command == 164: # y3
		return ("y", reader.int24())
	elif command == 165: # y4
		return ("y", reader.int32())

	elif command == 166: # z0
		return ("z0", None)
	elif command == 167: # z1
		return ("z", reader.int8())
	elif command == 168: # z2
		return ("z", reader.int16())
	elif command == 169: # z3
		return ("z", reader.int24())
	elif command == 170: # z4
		return ("z", reader.int32())

	elif 234 >= command >= 171:
		return ("fnt_num", command - 171)
	elif command == 235:
		return ("fnt_num", reader.uint8())
	elif command == 236:
		return ("fnt_num", reader.uint16())
	elif command == 237:
		return ("fnt_num", reader.uint24())
	elif command == 238:
		return ("fnt_num", reader.uint32())

	elif command == 239:
		k = reader.uint8()
		data = reader.read(k)
		return ("xxx", data)
	elif command == 240:
		k = reader.uint16()
		return ("xxx", reader.read(k))
	elif command == 241:
		k = reader.uint24()
		return ("xxx", reader.read(k))
	elif command == 242:
		k = reader.uint32()
		return ("xxx", reader.read(k))

	elif command == 243:
		k = reader.uint8()
		c = reader.uint32()
		s = reader.uint32()
		d = reader.uint32()
		a = reader.uint8()
		l = reader.uint8()
		dir = reader.read(a)
		fnt = reader.read(l)
		return ("fnt_def", (k,c,s,d, dir, fnt))
	elif command == 244:
		k = reader.uint16()
		c = reader.uint32()
		s = reader.uint32()
		d = reader.uint32()
		a = reader.uint8()
		l = reader.uint8()
		dir = reader.read(a)
		fnt = reader.read(l)
		return ("fnt_def", (k,c,s,d, dir, fnt))
	elif command == 245:
		k = reader.uint24()
		c = reader.uint32()
		s = reader.uint32()
		d = reader.uint32()
		a = reader.uint8()
		l = reader.uint8()
		dir = reader.read(a)
		fnt = reader.read(l)
		return ("fnt_def", (k,c,s,d, dir, fnt))
	elif command == 246:
		k = reader.uint32()
		c = reader.uint32()
		s = reader.uint32()
		d = reader.uint32()
		a = reader.uint8()
		l = reader.uint8()
		dir = reader.read(a)
		fnt = reader.read(l)
		return ("fnt_def", (k,c,s,d, dir, fnt))

	elif command == 247:
		i   = reader.uint8()
		num = reader.uint32()
		den = reader.uint32()
		mag = reader.uint32()
		k   = reader.uint8()
		x   = reader.read(k)
		return ("pre", (i, num, den, mag, x))
	elif command == 248:
		p   = reader.uint32()
		num = reader.uint32()
		den = reader.uint32()
		mag = reader.uint32()
		l   = reader.uint32()
		u   = reader.uint32()
		s   = reader.uint16()
		t   = reader.uint16()
		return ("post", (p, num, den, mag, l, u, s, t))
	elif command == 249:
		q = reader.uint32()
		i = reader.uint8()
		return ("post_post", (q, i))
	elif command in [250,251,252,253,254,255]:
		return ("undefined", command)
	else:
		raise ValueError("command %d not recognized (it is implementation error!)" % command)


def dviinfo(dvi):
	old_pos = dvi.tell()
	pad = chr(223)

	# read pre comand
	command, param = get_token(dvi)
	if command != "pre" or param[0] != 2:
		raise IOError("Not a DVI file")
	comment = param[4]

	# find post_post command
	dvi.seek(-14, 2)
	data  = dvi.read()

	# DVI file ends with 4-7 pad bytes
	off   = 0
	while len(data) and data[-1] == pad:
		data = data[:-1]
		off  = off - 1

	# before pads is a post_post command
	dvi.seek(off-6, 2)
	command, (q, i) = get_token(dvi)
	assert command == "post_post" and i == 2

	# q contains an offset to post command
	dvi.seek(q)
	command, (p, num, den, mag, l, u, s, t) = get_token(dvi)
	assert command == "post"

	#print "Pages count: %d" % t
	#print "Required stack size: %d" % s
	#print "Magnification: %d (%f)" % (mag, mag/1000.0)

	mm = num/(den*10000.0)
	#print "Page size: %d x %d (%fmm x %fmm)" % (u, l, u*mm, l*mm)

	# collect information about all fonts (they follow post command)
	fonts = {}
	while True:
		command, param = get_token(dvi)
		if command == "fnt_def":
			k, c, s, d, dir, fnt = param
			fonts[k] = c, s, d, fnt
			#print "%d: %s" % (k, fnt)
		else:
			break
	
	# collect pages offsets
	pages = []
	while p <> -1:
		pages.insert(0, p)
		dvi.seek(p)
		command, (c0,c1,c2,c3,c4,c5,c6,c7,c8,c9, p) = get_token(dvi)

	dvi.seek(old_pos)
	return (comment, (num, den, mag, u, l), pages, fonts)

# vim: ts=4 sw=4
