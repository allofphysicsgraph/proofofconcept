# -*- coding: iso-8859-2 -*-
#
# part of SVGfrags - simple parser
#
# Main program
# $Id: parser.py,v 1.4 2007-03-12 22:20:19 wojtek Exp $
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl/

# changelog:
"""
11-12.03.2007
	- first version
"""

import re
RegularExpressionType = type(re.compile(' '))

def preprocess(*expr):
	"""
	Gets expression or pair (callback, expression) and
	depending of expression type return proper rule instance.
	"""
	if len(expr) == 2:
		if callable(expr[0]):
			callback, expr = expr
		else:
			raise ValueError("First argument must be callable")
	elif len(expr) == 1:
		expr = expr[0]
		callback = None
	else:
		raise ValueError("Too many arguments; 1 or 2 allowed")


	# string: if string is enclosed in () is returned
	# otherwise is eaten
	if type(expr) is str:
		if len(expr) > 2 and expr[0] == '(' and expr[-1] == ')':
			if len(expr) > 3:
				return string(expr[1:-1], callback)
			else:
				return char(expr[1:-1], callback)
		else:
			if len(expr) == 1:
				return eat(char(expr, callback))
			else:
				return eat(string(expr, callback))

	# regexp
	elif type(expr) is RegularExpressionType:
		return regexp(expr, callback)
	
	# rule instance
	elif isinstance(expr, rule):
		if callback is not None:  # set callback if wasn't set
			expr.callback = callback
		return expr
	
	else:
		raise ValueError("Don't know how to deal with %s (%s)" % (str(expr), type(expr)))

token = preprocess

class rule(object):
	"Base class for parser"
	def __init__(self, expr, callback=None):
		assert callback is None or callable(callback), "Callback have to be callable or None"
		self.expr     = expr
		self.callback = callback
		
	def match(self, string):
		try:
			length, matched = self.get(string)
			if self.callback is not None:
				matched = self.callback(string, length, matched)

			return (length, matched)
		except TypeError:
			return None
	
	def get(self, string):
		raise RuntimeError("Abstract method called")


class char(rule):
	"Matches single char"
	def get(self, string):
		try:
			if self.expr == string[0]:
				return (1, [self.expr])
		except IndexError:
			pass # empty string
			

class string(rule):
	"Matches string"
	def get(self, str):
		if str.startswith(self.expr):
			return (len(self.expr), [self.expr])


class regexp(rule):
	"Matches regular expression"
	def get(self, string):
		match = self.expr.match(string)
		if match:
			if len(match.groups()) == 1:
				return (match.end(), [match.groups()[0]])
			elif len(match.groups()) > 1:
				return (match.end(), [match.groups()])
			else:
				return (match.end(), [])


class eat(rule):
	"Matches anything, but returns no data"
	def get(self, string):
		try:
			length, matched = self.expr.match(string)
			return (length, [])
		except TypeError:
			pass # no match


class seq(rule):
	"""
	Matches ALL expressions from the list.
	Optional ws rule is consumed before processing
	every expression list.
	"""

	def __init__(self, *expr):
		if len(expr) > 1 and callable(expr[0]):
			self.callback = expr[0]
			expr = expr[1:]
		else:
			self.callback = None
		
		self.expr = [preprocess(e) for e in expr]
	
	ws = []

	def eat_ws(self, string):
		if seq.ws:
			try:
				length, matched = seq.ws.match(string)
				if length > 0:
					return (length, string[length:])
			except TypeError:
				pass

		return (0, string)
	
	def get(self, string):
		length  = 0
		matched = []
		for expr in self.expr:
			try:
				l, string = self.eat_ws(string)
				length = length + l

				l, m   = expr.match(string)
				length = length + l
				string = string[l:]
				matched.extend(m)
			except TypeError:
				return None # not all expression matches

		return (length, matched)


class glued(seq):
	"Like seq, but ws is not processed, even if present"	
	def eat_ws(self, string):
		return (0, string)


class optional(rule):
	"Matches 0 or 1 times"
	def __init__(self, *expr):
		self.callback = None
		if len(expr) > 1:
			self.expr = seq(*expr)
		else:
			self.expr = preprocess(*expr)

	def get(self, string):
		try:
			length, matched = self.expr.match(string)
			return (length, matched)
		except TypeError:
			return (0, []) # no match

class alt(seq):
	"Matches FIRST expressions from the list"
	def get(self, string):
		for expr in self.expr:
			try:
				length, matched = expr.match(string)
				return (length, matched)
			except TypeError:
				pass

class infty(seq):
	"While any of expression from the list matches, consume input"
	def get(self, string):
		matches = []
		length  = 0
		while True:
			for expr in self.expr:
				try:
					l, m = expr.match(string)
					length += l
					string  = string[l:]
					matches.extend(m)
					break
				except TypeError:
					pass
			else:
				# no matches
				break

		if length:
			return (length, matches)
		else:
			return None

# vim: ts=4 sw=4 nowrap
