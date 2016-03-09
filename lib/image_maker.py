
import sys
import json
import cPickle as pickle
import mimetypes
import hashlib
from stat import *
import os


excludes = set()
excludes.add('/proc')
excludes.add('/home')
excludes.add('/sys')
excludes.add('/root')
excludes.add('/boot')
excludes.add('/usr/src')


__NA = 'N/A'

__ascii = False
__hash = False
__type = False

def get_root_dir() :
	""" http://stackoverflow.com/questions/12041525/a-system-independent-way-using-python-to-get-the-root-directory-drive-on-which-p """

	dr = os.path.splitdrive( sys.executable )
	if not dr[0] :		#	dr[0] is empty, we have *nix system, root dir is '/' handled later
		return '/'
	else :				#	dr[0] is like 'C:\\', we have a Windows system
		return dr[0]

		'''		This one returns the base location of the script	'''
    # return os.path.abspath(os.sep)



def hashfile(afile, hasher, blocksize=65536):
	'''
http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
	'''
	if afile == None :
		return ''
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	afile.close()
	return hasher.digest()


def sec_open(path, op_str) :
	try :
		f = open(path, op_str)
		return f
	except :
		pass


def create_file_obj(full_path, name ) :

	full_name = os.path.join(full_path, name)

	# print full_name

	if __type :
		mime = os.popen( "file '{0}' ".format( full_name ) ).read().split( ':' )[-1].strip()
	else :
		mime = mimetypes.guess_type( full_name )[0]
		if mime == None :
			mime = __NA

	stat_obj = os.lstat(full_path)	# lstat instead of stat to NOT follow symlinks

	fobj = dict()

	fobj['filename'] = name
	fobj['path'] = full_path
	fobj['owner'] = stat_obj[ST_UID]
	fobj['group'] = stat_obj[ST_GID]
	fobj['size'] = stat_obj[ST_SIZE]
	fobj['privileges'] = str( oct( stat_obj[ST_MODE] ) )
	fobj['type'] = mime
	fobj['SHA2'] = __NA
#	for exc in excludes :
	if full_name in excludes :
		return fobj

	if S_ISLNK(stat_obj.st_mode) :
		return fobj

	if os.path.isdir(full_name) :

		fobj['type'] = 'directory'
		fobj['content'] = crawl_folder (full_path, name, dict())
#		print full_name


	elif 'text' in mime and __ascii:

		try :
			f = open( full_name, 'r' )
			fobj['content'] = f.read().strip()
			f.close()
		except :
			pass

	else :
		fobj['content'] = __NA

		if __hash :
			try :
				f = open( full_name, 'rb' )
				fobj['SHA2'] = hashfile(f, hashlib.sha256())
				f.close()
			except :
				pass

	return fobj


def crawl_folder(base, folder_path, fset) :

	full_path = os.path.join( base, folder_path )

	try : 
		for file in os.listdir(full_path) :
			fobj = create_file_obj(full_path, file)
			fset[ full_path + os.sep + file ] = fobj
# 			print full_path + file
	except OSError :
			pass


	return fset


def crawl_filesystem() :

	root = get_root_dir()

#	root = '/home/john/'

	ret = {}
	ret = create_file_obj(root, '')
	# crawl_folder(root, '', ret)
	
	return ret




if __name__ == "__main__" :

	fsys = crawl_filesystem()
	# f = open ('file_system.json', 'w')
	# f.write( json.dumps( fsys, indent = 1 ) + '\n' )
	f = open ('file_system_n.pkl', 'wb')
	f.write( pickle.dumps( fsys ) )

	f.close()
#	print fsys