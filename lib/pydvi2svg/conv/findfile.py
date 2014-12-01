# -*- coding: iso-8859-2 -*-
# $Id: findfile.py,v 1.5 2007-03-13 21:04:15 wojtek Exp $
#
# pydvi2svg - file searching functions
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
13.11.2006
	- +which
16.10.2006
	- generalized find_file & find_all_files (removed find_all, findfile)
	- upated kpsewhich
15.10.2006
	- find_all returns only files
5.10.2006
	- find_all
4.10.2006
	- locate, findfile (+ignorecase)
3.10.2006
	- kpsewhich, findfile
"""

import os
import types

def find_file(paths, pred, enterdir=lambda path, depth: True):
	"""
	Function searches all paths listed on paths list and
	return first file that pred(file) is True.  Subdirectories
	are visited only if function 'enterdir' return True.

	Function 'pred' must accept two arguments: path, filename
	and returns either True or False

	Function 'enterdir' must accept two arguments: path
	and depth in directory tree (counted from 0).
	"""
	def aux(path, pred, enterdir, level):
		dir = os.listdir(path)
		for file in dir:
			if pred(path, file):
				return os.path.join(path, file)

		# not found, go deeper
		for file in dir:
			newpath = os.path.join(path, file)
			if os.path.isdir(newpath) and enterdir(newpath, level):
				result = aux(newpath, pred, enterdir, level+1)
				if result:
					return result
		return None


	if type(paths) in types.StringTypes:
		return aux(paths, pred, enterdir, 0)
	else:
		for path in paths:
			file = aux(path, pred, enterdir, 0)
			if file:
				return file


def find_all_files(paths, pred, enterdir=lambda path, depth: True):
	"""
	Function searches all paths listed on paths list and
	return all files that pred(file) is True.  Subdirectories
	are visited only if function 'enterdir' return True.

	Function 'pred' must accept two arguments: path, filename
	and returns either True or False

	Function 'enterdir' must accept two arguments: path
	and depth in directory tree (counted from 0).
	"""
	def aux(path, pred, enterdir, level, list):
		dir = os.listdir(path)
		# XXX: use list comprehension
		for file in dir:
			if pred(path, file):
				list.append(os.path.join(path, file))

		# go deepper
		for file in dir:
			newpath = os.path.join(path, file)
			if os.path.isdir(newpath) and enterdir(newpath, level):
				aux(newpath, pred, enterdir, level+1, list)

	L = []
	if type(paths) in types.StringTypes:
		aux(paths, pred, enterdir, 0, L)
	else:
		for path in paths:
			file = aux(path, pred, enterdir, 0, L)
	return L


kpsewhich_available = True
def kpsewhich(filename):
	global kpsewhich_available

	assert filename != ''

	if kpsewhich_available:
		stdout     = os.popen('kpsewhich %s' % filename, 'r')
		path       = stdout.read().rstrip()
		exitstatus = stdout.close()
		if exitstatus:
			if exitstatus >> 8 == 127: kpsewhich_available = False
			return None
		else:
			return path
	else:
		return None


def locate(filename, search_paths=[]):
	return kpsewhich(filename) or \
	       find_file(search_paths, pred=lambda p, f: f==filename)


try:
	dirs = os.environ['PATH'].split(':')
except KeyError:
	dirs = []

def which(name):
	for path in dirs:
		fullpath = os.path.join(path, name)
		if os.path.isfile(fullpath):
			return fullpath

# vim: ts=4 sw=4
