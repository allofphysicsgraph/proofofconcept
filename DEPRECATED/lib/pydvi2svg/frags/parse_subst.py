# -*- coding: iso-8859-2 -*-
# $Id: parse_subst.py,v 1.9 2007-03-13 20:51:30 wojtek Exp $
#
# part of SVGfrags -- subst list parser 
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl/

# changelog
"""
13.03.2007
	- use decorator expression
	- some cleanups
	- in case on SyntaxError, return string representation,
	  not string itself
12.03.2007
	- rewritten (use parser.py)
10.03.2007
	+ margins property
 9.03.2007
	- class approach:
	  + Tokenizer (base class)
	  + FragsTokenizer (specialized class)
	  + parser
 8.03.2007
	- first version
"""

import re
from parser import token, seq, alt, optional as opt, infty, glued, eat

space 	= re.compile(r'\s+')
comment	= re.compile('\s*%.*\n')

# by default eat spaces and comments
seq.ws = infty(space, comment)

def expression(expr):
	expr = token(expr)
	def foo(callback):
		expr.callback = callback
		return expr
	return foo

@expression(re.compile(r'([+-]?\d*\.\d+|[+-]?\d+\.\d*|[-+]?\d+)'))
def number(l, s, r):
	return [float(r[0])]

@expression(glued(number, opt("(%)")))
def numorperc(l, s, r):
	if len(r) == 2: # perc
		return [(r[0] * 0.01)]
	else:
		return r

@expression(re.compile(r'"((?:\\"|[^"])*)"'))
def quoted_string(l, s, r):
	return [r[0].replace('\\"', '"')]

@expression(re.compile(r'(#[a-zA-Z0-9._:-]+)'))
def xml_id(l, s, r):
	return [('id', r[0])]

@expression(seq("rect", "(", number, ",", number, ",", number, ",", number, ")"))
def rect(l, s, r):
	return [('rect', tuple(r))]
	
@expression(seq("point", "(", number, ",", number, ")"))
def point(l, s, r):
	return [('point', tuple(r))]


margin = seq(
	"margin", ":", numorperc,
	 opt(",", numorperc, opt(",", numorperc, ",", numorperc))
)
@expression(margin)
def margin(l, s, r):
	if len(r) == 1:
		m = r[0]
		return [('margin', m, m, m, m)]
	elif len(r) == 2:
		mx, my = r
		return [('margin', mx, mx, my, my)]
	else: # 4 elements
		return [('margin',) + tuple(r)]

@expression(seq("(width)", "(", alt(xml_id, "(this)"), ")"))
def width(l, s, r):
	return [tuple(r)]

@expression(seq("(height)", "(", alt(xml_id, "(this)"), ")"))
def height(l, s, r):
	return [tuple(r)]

@expression(seq("(length)", number))
def length(l, s, r):
	return [tuple(r)]

scaledim = alt(numorperc, number, width, height, length, "(uniform)")

@expression(seq("scale", ":", alt("(fit)", seq(scaledim, opt(",", scaledim)))))
def scale(l, s, r):
	if len(r) == 1: # fit/one scaledim
		sx = r[0]
		if sx == 'uniform': return [] # no scale (syntax error)
		if type(sx) is float:
			return [('scale', sx, sx)]
		elif sx == 'fit':
			return [('scale', 'fit')]
		else:
			return [('scale', sx, "uniform")]
	else: # two scaledim
		sx, sy = r

		if sx == sy == 'uniform':	# no scale
			return []
		
		if sy == 'uniform' and type(sx) is float:
			return [('scale', sx, sx)] # uniform
		else:
			return [('scale', sx, sy)]

px = alt(
	numorperc,
	number,
	"(center)",  "(c)",
	"(left)",    "(l)",
	"(right)",   "(r)",
	"(inherit)", "(i)",
)

@expression(px)
def px(l, s, r):
	x_const = {
		'center': 0.5, 'c':0.5,
		'left'  : 0.0, 'l':0.0,
		'right' : 1.0, 'r':1.0
	}
	val = r[0]
	if type(val) is str:
		try:
			return [x_const[val]]
		except KeyError:
			return ['inherit']
	else:
		return r


@expression(alt(numorperc, number, "(center)", "(c)", "(top)", "(t)", "(bottom)", "(b)"))
def py(l, s, r):
	y_const = {
		'center' : 0.5, 'c':0.5,
		'top'    : 0.0, 't':0.0,
		'bottom' : 1.0, 'b':1.0
	}
	val = r[0]
	if type(val) is str:
		return [y_const[val]]
	else:
		return r


@expression(seq("(position)", ":", px, opt(",", py)))
def position(l, s, r):
	if len(r) == 2: # single argument
		if r[1] == 'inherit':
			return [(r[0], 'inherit', 1.0)]
		else:
			return [(r[0], r[1], r[1])]
	else: # two args
		return [tuple(r)]


class record:
	def __init__(self):
		self.scale    = (1.0, 1.0)
		self.margin   = (0.0, 0.0, 0.0, 0.0)
		self.position = ('inherit', 1.0) # inherit, bottom
	def __str__(self):
		return "{%s}" % ", ".join(self.__dict__.keys())
	
	__repr__ = __str__


@expression(alt(quoted_string, xml_id, rect, point))
def target(l, s, r):
	if type(r[0]) is str:
		return [('string', r[0])]
	else:
		return r

arrow  = eat(token(re.compile(r'(?:->|=>|=)')))

@expression("(this)")
def this(l, s, r):
	return [None]

source = alt(quoted_string, this)

rule = seq(target, arrow, source, opt(position), opt(margin), opt(scale))
@expression(rule)
def rule(l, s, r):
	# target, source, (...other data...)
	data = record()
	for item in r[2:]:
		value = item[1:]
		if len(value) == 1:
			setattr(data, item[0], value[0])
		else:
			setattr(data, item[0], value)
	
	return [r[0], r[1], data]


class SyntaxError(Exception): pass
	

def parse(string):
	while string:
		try:
			l, _ = seq.ws.match(string)
			string = string[l:]
		except TypeError:
			pass

		if not string:
			break
		
		try:
			l, r = rule.match(string)
			yield r
			string = string[l:]
		except TypeError:
			raise SyntaxError("%r..." % string[:30])

# vim: ts=4 sw=4 nowrap
