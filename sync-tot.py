#!/usr/bin/python

# Author: Porter Liu

import re
import sys
import json
import string
import urllib2
import os.path

from poster.encode import MultipartParam
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers


# http://foo.com/allbuilds/iOS-client.123/InHouse_123.ipa
configuration_smaple = {
	"base_url"      : "http://foo.com/allbuilds/",
	"build_pattern" : "iOS-client.(\\d+)",
	"build_path"    : "iOS-client.{bn}/InHouse_{bn}.ipa",
	"tot_url"       : "http://bar.com/tot/",
}

def show_configuration_file_syntax():
	print( configuration_smaple )


# we need one argument for configuration file
if len( sys.argv ) != 2:
	print( 'Usage: ' + sys.argv[0] + ' configuration_file' )
	exit( 1 )

# generate build number filename from configuration filename
# for instance: foo.json => foo.buildnumber.txt
temp1, temp2 = os.path.splitext( os.path.basename( sys.argv[1] ) )
buildnumber_filename = temp1 + '.buildnumber.txt';

# open & load configuration in JSON format
try:
	configurationFile = open( sys.argv[1] )
	try:
		config = json.load( configurationFile )
	except Exception, e:
		print( e )
		exit( 1 )
	finally:
		configurationFile.close()
except Exception, e:
	print( e )
	exit( 1 )

# verify configuration file
for key in configuration_smaple.keys():
	if key not in config:
		print( 'Failed to find "' + key + '" in ' + sys.argv[1] )
		show_configuration_file_syntax()
		exit( 1 )

#
# load the last processed build number
#
build_number = 0

if os.path.exists( buildnumber_filename ):
	temp = open( buildnumber_filename, 'r' )
	build_number = string.atoi( temp.read() )
	temp.close()

print( 'old build number = ' + str( build_number ) )

#
# find out the latest build number
#
try:
	remotefile = urllib2.urlopen( config['base_url'] )
	data = remotefile.read()
	remotefile.close()
except Exception, e:
	print( 'failed to access "' + config['base_url'] + '", ' + str( e ) )
	exit( 1 )

temp_build_number = build_number

pattern = config['build_pattern']
po = re.compile( pattern )
mo = po.findall( data )
if mo:
	for item in mo:
		n = string.atoi( item )
		if n > temp_build_number:
			temp_build_number = n

print( 'current max build number = ' + str( temp_build_number ) )

if temp_build_number <= build_number:
	print( 'no new build' )
	sys.exit( 0 )
else:
	build_number = temp_build_number

print( 'will use ' + str( build_number ) + ' as build number' )

#
# generate package url and download
#
url = ( config['base_url'] + config['build_path'] ).format( bn = build_number )
print( 'package URL = ' + url )

package_filename = os.path.basename( url )
print( 'package filename = ' + package_filename )

remotefile = urllib2.urlopen( url )
localFile = open( package_filename, 'wb' )
localFile.write( remotefile.read() )
localFile.close()
remotefile.close()

#
# upload package file onto TOT
#
register_openers()

#datagen, headers = multipart_encode( { 'file' : open( ipa_filename, 'rb' ), 'changelog' : build_name + '.' + str( build_number ), 'submit' : 'Submit' } )
ipa          = MultipartParam.from_file( 'file', package_filename )
ipa.filetype = 'application/octet-stream'
changelog    = MultipartParam( 'changelog', str( build_number ) )
submit       = MultipartParam( 'submit',    'Submit' )
datagen, headers = multipart_encode( [ ipa, changelog, submit ] )

request = urllib2.Request( config['tot_url'] + '/upload.php', datagen, headers )

print urllib2.urlopen( request ).read()

# delete the package
os.remove( package_filename )

#
# save the current build number
#
temp = open( buildnumber_filename, 'w' )
temp.write( str( build_number ) )
temp.close()
