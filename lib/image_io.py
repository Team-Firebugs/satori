
import cPickle as pickle
import json

import gzip

__use_gzip = False

def which_open() :
	if __use_gzip :
		return gzip.open
	else :
		return open

def loadImage(filename, type = 'pickle') :	# type = json | pickle | sqlite

	open = which_open()
	infile = open(filename, 'rb')
	meth = pickle
	if type == 'json' :
		meth = json

	return meth.load ( infile )


def saveImage(filename, toSave, type = 'pickle') :

	open = which_open()
	outfile = open(filename, 'wb')
	meth = pickle
	if type == 'json' :
		meth = json

	outfile.write( meth.dumps( toSave ) ) 

