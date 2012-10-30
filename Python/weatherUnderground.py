#!/usr/bin/python

# ========================
# Weather underground API
# ========================

from urllib import urlopen
import json

APIkey = ''
APIlink = 'http://api.wunderground.com/api'
responseFormat = 'json'

dateFlickrFormat = '2009-09-21 12:38:35'

debug = 0


def sendQuery(method, **params):
	url = '%s/%s/%s%s.%s' %(APIlink,APIkey,method,paramstoURL(params),responseFormat)
	if debug:
		print "===\tMethod is:\t%s\n===\tQueryURL:\t%s\n" % (method,url)
	return urlopen(url)


def parse(jsonData):
	data = json.loads(jsonData.read())
	if debug:
		print data
	return data


def paramstoURL(params):
 # put into URL formatting
 	result=''
 	for (key, value) in params.items():
		# result += "&" + key
		if isinstance(value, list):
			# multiple params
			result += ','.join([item for item in value])
		else:
			# single param
			result += value
	return result


def geoLookUp(nGeo):
	jsonData = parse(sendQuery('geolookup/q/',geo = nGeo))

	if debug:
		print jsonData['location']['city']
	return jsonData['location']['l']


def weatherAtDate(location,date):
	date = dateWUFormat(date)
	method = 'history_'+str(date)
	weatherData = parse(sendQuery(method,location=location))
	if debug:
		print weatherData
	return weatherData


def dateWUFormat(date):
	# dateFlickrFormat	= YYYY-MM-DD HH:MM:SS
	# wUnderound Format = YYYYMMDD 
	return ''.join(date.split(' ',1)[0].split('-'))