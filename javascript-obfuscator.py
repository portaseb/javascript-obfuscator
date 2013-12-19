#!/usr/bin/python2.7

import httplib, urllib, sys, re

def putFunctionsInFile(anArray, fw) :
	if ( len(anArray) > 0 ):
		for i in anArray:
			fw.write( anArray[i] + '\n' )

		fw.write('\n\n\n')	
		
def putVariablesInFile(anArray, fw) :
	if ( len(anArray) > 0 ):
		begin = None
		for i in anArray:
			if begin is None:
				fw.write( 'var ' + i + ' = ' + anArray[i] )
				begin = 0
			else:
				fw.write( ',\n\t' + i + ' = ' + anArray[i] )
		fw.write(';\n\n\n')	

# Define the parameters for the POST request and encode them in
# a URL-safe format.

#params = urllib.urlencode([
#    ('js_code', sys.argv[1]),
#    ('compilation_level', 'WHITESPACE_ONLY'),
#    ('output_format', 'text'),
#    ('output_info', 'compiled_code'),
#  ])

# Always use the following value for the Content-type header.
#headers = { "Content-type": "application/x-www-form-urlencoded" }
#conn = httplib.HTTPConnection('closure-compiler.appspot.com')
#conn.request('POST', '/compile', params, headers)
#response = conn.getresponse()
#data = response.read()
#print data
#conn.close()

properties = {}
refObjects = {}
functionProperties = {}
setFunctions = {}
getFunctions = {}

fr = open(sys.argv[1], 'r')
fw = open('workfile', 'w')
i = 0
for line in fr:
	#if ( i > 3 ):
	#	break
	#i = i + 1
	# look for properties access
	m = re.search('([a-zA-Z0-9_-]*)(\.[a-zA-Z0-9_-]*)+(\s*=\s*)([a-zA-Z0-9_-][^;]*);?(|//.*)', line)
	if m is not None:
		line = line.rstrip()
		anObject = m.group(1).replace('.','')
		aProperty = m.group(2).replace('.','')
		equalSign = m.group(3)
		aValue = m.group(4)
		someComments = m.group(5)
		#objKey = 'my' + aRefObject
		#if not objKey in refObjects:
		#	refObjects[objKey] = '"' + aRefObject + '"'
		newName = 'my' + aProperty.title()
		if not newName in functionProperties:
			# create the associated function
			functionProperties [newName] = 'function ' + newName + '(anObj, aValue) { return anObj.' + aProperty + ' = aValue; }'
			
		# toto.titi = 3	
		line = line.replace(anObject + '.' + aProperty, newName + '(' + anObject);
		line = line.replace(equalSign, ','); #subtitue the equal by a comma
		line = line.replace(aValue, aValue + ')');
		fw.write( line + someComments + '\n' )	
		
		
	else:
		# Loog for get function
		m = re.search('([a-zA-Z0-9_-]*)(\.[a-zA-Z0-9_-]*)*\.([a-zA-Z0-9_-]*)\s*\(', line)
		if m is not None:
			mainObject = m.group(1)
			if mainObject == '':
					fw.write( line + '\n' )
			else : 
				subObjects = m.group(2)
				if subObjects is not None:
					subObjects = subObjects.split('.') 
					#manage sub object reference
					if not subObjects[1] in getFunctions:
						getFunctions[subObjects[1]] = '"' + subObjects[1] + '"'
					line = line.replace("." + subObjects[1], "[" + subObjects[1] + "]")	

				aFunction = m.group(3)

				functionKey = 'my' + aFunction.title()
				if not functionKey in getFunctions:
					getFunctions[functionKey] = '"' + aFunction + '"'
				line = line.replace('.' + aFunction, '[my' + aFunction + ']')
				
				matchObj = re.match( '\s*loc[a-zA-Z0-9_-]*', mainObject)
				# verification que c'est pas une variable locale
				if matchObj is None:				
					# cache the object ref
					objKey = 'my' + mainObject.title()
					if not objKey in refObjects:
						refObjects[objKey] = mainObject		
					line = line.replace(mainObject, objKey)		
				fw.write( line + '\n' )
				#print line + '\n'
				#print mainObject + '->///// ' + subObjects + '///// ' + aFunction + '\n'
		else:
			fw.write( line )
fr.closed
fw.closed

#exit(0)

fw = open('workfile.final', 'w')

#add get functions
putVariablesInFile(getFunctions, fw)

#add ref objects
putVariablesInFile(refObjects, fw)

#add properties functions
putFunctionsInFile(functionProperties, fw)

fr = open('workfile', 'r')
for line in fr:
	fw.write( line )
fr.closed
fw.closed

