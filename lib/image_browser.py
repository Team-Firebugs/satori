#-*- coding: utf-8 -*-

import cmd
import re
import os
from pprint import pprint 

from lib.definitions import meta_templates, meta_tags

color = {}
color['gray'] = '\033[04;39m'
color['green'] = '\033[01;32m'
color['red'] = '\033[0;31m'
color['blue'] = '\033[01;34m'
color['END'] = '\033[00m'


class SatoriShell (cmd.Cmd) :

	commands = [ 'cd', 'ls', 'stat', 'cat', 'file', 'hash', 'pwd', 'info' ]
	debugs = [ 'keys', 'value' ]
	prompt_format = color['gray'] + "{{Satori}}" + color['END'] + ' %s%s@%s%s ' + color['blue'] + '{0} $ '+color['END']		# "{Satori} john@Lucinda / $ "
	prompt = prompt_format.format('/')

	dir_regex = '(\.\./?)+'

	cd_stack = []




	def change_prompt(self, dir) :

		path = dir['path'] + os.sep + dir['filename']
		if path.startswith(os.sep*2) :
			path = path[1:]

		self.prompt = self.prompt_format.format(path)



	def __init__ (self, image) :
		cmd.Cmd.__init__(self)
		self.__image = image
		self.__wd = image['system']
		self.__base = self.__wd
		self.__user = image['meta']['user']
		self.__host = image['meta']['hostname']

		col = color['green']
		if self.__user == 'root' :
			col = color['red']

		self.prompt_format = self.prompt_format % (col, self.__user, self.__host, color['END'])
		self.change_prompt(self.__wd)



	def exists (self, name) :
		if ( name in self.__wd['content'].keys() ) :
			return True
		else :
			print "	File '%s' doesn't exist in current directory!" % name
			return False


	def do_id (self, line) :
		"""	Typical UNIX command. Added for extra flavour"""
		print "	uid=%s(%s)	gid=%s"	% (self.__image['meta']['UID'], self.__image['meta']['user'], self.__image['meta']['GID'] )

	def do_info (self, line) :
		"""	Prints out Information about the Satori Image being browsed."""
		print
		print "Image Info:"
		for k in meta_tags :
			if k != 'program' :
				print ( "	"+meta_templates[k]. format( self.__image['meta'][k] ) ).encode('utf8')
		print


	def do_ls (self, line) :
		"""	Typical UNIX command. Lists directories."""
		# if line.strip() : 

		target = self.__wd
		arg = line.split()
		if len(arg) > 0 :

			if self.exists (arg[0]) :
				target = self.__wd['content'][arg[0]]
			else :
				return


		if target['type'] == 'directory' :
			print "	".join( target['content'].keys() )
		else :
			print "	'%s' is not a directory" % target['filename'] 
		return



	def complete_ls (self, text, line, begidx, endidx) :
		return self.complete_cd ( text, line, begidx, endidx ) 



	def do_cd (self, line) :
		"""	Typical UNIX command. Changes 'Current working directory'. Arguments such as '../' can also be used."""
		f = line.strip()
		if not f :
			return 

		if re.match(self.dir_regex, f) :
			bt_len = f.count('..') + 1
			wd = self.__wd

			for i in range(bt_len) :

				if len(self.cd_stack) > 0 :
					wd = self.cd_stack.pop()
				else :
					wd = None

			if wd == None :
				self.__wd = self.__base
			else :
				self.__wd = wd

			self.change_prompt(self.__wd)
			return

		if f in self.__wd['content'].keys() :

			if self.__wd['content'][f]['type'] == 'directory' :
				self.__wd = self.__wd['content'][f]
				self.cd_stack.append(self.__wd)

				self.change_prompt(self.__wd)

			else :
				print "	Can't 'cd' to '%s', not a directory." % self.__wd['content'][f]['filename']

		else :
			print "	cCan't 'cd' to '%s', directory doesn't exist." % f


	def complete_cd (self, text, line, begidx, endidx) :
		if not text :
			return self.__wd['content'].keys()
		else :
			return [ f for f in self.__wd['content'].keys() if f.startswith(text) ]



	def do_stat (self, line) :
		"""	Typical UNIX command. Displays collected information about files."""
		f = line.strip()

		if not f :
			target = self.__wd

		else :
			if self.exists(f) :
				target = self.__wd['content'][f]
			else :
				return

		for k in target.keys() :

			if k != 'content' :
				print  "	%s : %s" % ( k, target[k] ) 



	def do__keys (self, line) :
		# """Debugging command. Shows the "working directory's" dictionary keys"""
		
		print self.__wd.keys()

	def do__trace_cd (self, line) :
		# """Debugging command. Shows the "cd stack-trace" """

		print [x['filename'] for x in self.cd_stack]


	def emptyline (self) :
		return



if __name__ == "__main__" :		# TODO standalone module

	pass