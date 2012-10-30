#!/usr/bin/python

# =================================
# ====	TYP MeteoPhoto Script
# =================================

# This sctipt should take photos from flickr as well as geoData

from urllib import urlopen
import re
import time
import weatherUnderground
import json
import os

### Global vars
APIlink = 'http://flickr.com/services/rest'
APIkey = ''
userID = '89142869@N08' #myFlickr Id by default
galleryID = '89050056-72157631838723244' #myFlickr galleryId by default
responseFormat = 'json' 

#d3bu6 sfitsh.. To make this process just a bit more fun
debug = 0

class Bad_Flickr_Response(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class photoObj:
	def __init__(self,pid,date,url,geo):
		self.id=pid
		self.date=date
		self.url=url
		self.geo=geo


def getPhotos(galleryID):
	jsonData = parse(sendQuery('flickr.galleries.getPhotos',gallery_id=galleryID,extras=['geo', 'url_m','date_taken']))
	photosList = jsonData['photos']['photo']
	photos=[]

	for i in sureToList(photosList):
		geolocation = {'latitude': i['latitude'], 'longitude': i['longitude']}
		new = photoObj(i['id'],i['datetaken'],i['url_m'],geolocation) #__init__(self,id,date,url,geo)
		photos.append(new)
	return photos


def sendQuery(method, **params):
	url = '%s?api_key=%s&method=%s%s&format=%s' %(APIlink,APIkey,method,paramstoURL(params),responseFormat)
	if debug:
		print "===\tMethod is:\t%s\n===\tQueryURL:\t%s\n" % (method,url)
	return urlopen(url)


def getUserGalleries(userID):
	jsonData =  parse(sendQuery('flickr.galleries.getList',user_id=userID))
	galleryList = jsonData['galleries']['gallery']
	galleryIDList=[]
	for gal in sureToList(galleryList):
		galleryIDList.append(gal['id'])

	if debug:
		print "Galleries found:"
		print galleryIDList
	return galleryIDList


def paramstoURL(params):
 # put into URL formatting
	result=''
	for (key, value) in params.items():
		result += "&" + key
		if isinstance(value, list):
			# multiple params
			result += "="+','.join([item for item in value])
		else:
			# single param
			result += "="+value
	return result


def parse(jsonData):
	p = re.compile('{.*}') #due to standard
	data = json.loads(p.search(jsonData.read()).group())

	if debug:
		print data
		
	# data = json.loads((jsonData.read()[14:-1]))
	# this is faster, but less reliable method (as works on chars position)
	try:
		if data['stat'] == 'ok':
			return data
		elif data['stat'] == 'fail':
			stat = "Code: " + str(data['code'])+"\nMessage: " + str(data['message'])
			raise Bad_Flickr_Response(stat)
	except Bad_Flickr_Response as e:
			print '!!!\tFailure response from Flickr\n', e.value


def saveFile(filePath,data,binaryBool):
	with open (filePath,'wb') as f:
		if (binaryBool):
			f.write(data.read())
		else:
			f.write(data)
		f.close()


def fileDownload(url):
	path = './downloads'
	if not os.access(path,os.F_OK):
		os.mkdir(path)
	filename = path+"/"+url.split('/')[-1]
	print "Downloading: "+url
	buf = urlopen(url)
	saveFile(filename,buf,1)
	buf=None


def getPhotosFromAllGalleries(userID):
	gal_list=getUserGalleries(userID)
	for gal in sureToList(gal_list):
			savePicturesWithGeodata(getPhotos(gal))


def waitForWU():
	print 'Waiting for weatherUnderground timeout...' 
	time.sleep(7)


def savePicturesWithGeodata(picObjsList):
	for photo in sureToList(picObjsList):					
		fileDownload(photo.url)
		filename = "./downloads/"+photo.url.split('/')[-1]+".info"

		if (photo.geo['latitude'] and photo.geo['longitude']):
			waitForWU()
			geo=weatherUnderground.geoLookUp([str(photo.geo['latitude']),str(photo.geo['longitude'])])
			waitForWU()
			wInfo = weatherUnderground.weatherAtDate(geo,weatherUnderground.dateWUFormat(photo.date))
			wInfo = wInfo['history']['dailysummary']

			if isinstance(wInfo,list):
				wInfo = wInfo[0]

			meteoInfo = openDict(wInfo,0)

			photoInfo =	"PhotoID: "+photo.id+"\n"+ \
						"URL: "+photo.url+"\n"+ \
						"DateTaken: "+photo.date+"\n"+ \
						"Latitude: "+str(photo.geo['latitude'])+"\n"+ \
						"Longitude: "+str(photo.geo['longitude'])+"\n"+ \
						"Mean Temperature: "+wInfo['meantempm']+"\n"+ \
						"Dew Point: "+wInfo['meandewptm']+"\nMeteo"+meteoInfo
			saveFile(filename,photoInfo,0)
		else:
			print "No geodata for picture: ",filename


def openDict(dictO,upIndent):
	string=''
	indent=upIndent
	for (key,value) in dictO.items():
		if isinstance(value,dict):

			string+='\t'*indent+key+':\n'
			indent=indent+1
			string+=openDict(value,indent)
			indent=indent-1
		else:
			string +='\t'*indent+key + ": " +value+"\n"
	return string


def findByUserName(name):
	jsonData =  parse(sendQuery('flickr.people.findByUsername',username=name))
	userList = jsonData['user']
	userIDList=[]
	
	for user in sureToList(userList):
		userIDList.append(user['nsid'])
	if debug:
		print "Users found:"
		print userIDList
	return userIDList


def sureToList(obj):
	if isinstance(obj,list):
		return obj
	else:
		return [obj]


savePicturesWithGeodata(getPhotos(galleryID))

# savePicturesWithGeodata(getPhotos(getUserGalleries(userID)))
# getPhotosFromAllGalleries(findByUserName('elmofoto'))