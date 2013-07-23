# Copyright 2013 Fabian Behnke
# Copyright 2012 Jacob Weber
#
# This file is now part of BeDJAY
# This file was originally part of Cover Art Server (https://github.com/jacobweber/coverArt).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#!/usr/bin/python

import sys, os, urllib, string, xml.dom.minidom, traceback, time, hashlib, base64, hmac

class AmazonCoverArt(object):
	""" Gets covers from Amazon's web service. The license file must contain
	an Access Key ID, followed by a carriage return, followed by a Secret Access Key.
	Optionally, you can include another carriage return and an associate tag.
	"""

	LICENSE_FILE = "amazonLicense.txt"
	HOST = "webservices.amazon.com"
	PATH = "/onca/xml"

	license = ""
	secret = ""
	associate = ""

	def __init__(self):
		if os.access(self.LICENSE_FILE, os.R_OK):
			f = open(self.LICENSE_FILE)
			self.license = f.readline().strip()
			self.secret = f.readline().strip()
			self.associate = f.readline().strip()
			f.close()
		if (self.license == "" or self.secret == ""):
			print 'The file "amazonLicense.txt" must contain your access key ID and secret key, separated by a return.'
		if (self.associate == ""):
			self.associate = "none"

	def search(self, artist='', album='', keywords=''):
		if (self.license == "" or self.secret == ""): return []
		params = {
			'Artist': artist.encode('utf-8'),
			'Keywords': keywords,
			'Operation': 'ItemSearch',
			'ResponseGroup': 'Images',
			'SearchIndex': 'Music',
			'Service': 'AWSECommerceService',
			'AssociateTag': self.associate,
			'Title': album.encode('utf-8')
		}
		url = self.getSignedURL(params)
		#print url
		covers = []
		c = None
		try:
			c = urllib.urlopen(url)
			xmlStr = c.read()
			covers = self.getCovers(xmlStr)
			c.close()
		except:
			traceback.print_exc(file=sys.stdout)
			if c: c.close()
		return covers

	def getCovers(self, xmlStr):
		covers = []
		usedURLs = []
		try:
			rootNode = xml.dom.minidom.parseString(xmlStr)
			#print rootNode.toprettyxml().encode('ascii', 'ignore')
			itemNodes = rootNode.getElementsByTagName("Item")
			for itemNode in itemNodes:
				#for tagName in ("SmallImage","MediumImage","LargeImage"):
				
					#imageNodes = itemNode.getElementsByTagName(tagName)
					imageNodes = itemNode.getElementsByTagName("MediumImage")
					for imageNode in imageNodes:
						cover = self.getCoverInfo(imageNode)
						if cover["url"] not in usedURLs:
							covers.append(cover)
							usedURLs.append(cover["url"])
		except:
			traceback.print_exc(file=sys.stdout)
			raise
		return covers

	def getCoverInfo(self, imageNode):
		cover = {}
		cover["url"] = imageNode.getElementsByTagName("URL")[0].childNodes[0].data
		cover["w"] = imageNode.getElementsByTagName("Height")[0].childNodes[0].data
		cover["h"] = imageNode.getElementsByTagName("Width")[0].childNodes[0].data
		return cover

	def getSignedURL(self, params):
		params["AWSAccessKeyId"] = self.license
		params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
		keys = params.keys()
		keys.sort()
		pairs = []
		for key in keys:
			val = params[key]
			pairs.append(urllib.quote(key, safe='') + '=' + urllib.quote(val, safe='-_~'))
		query = '&'.join(pairs)
		hm = hmac.new(
			self.secret,
			"GET\n%s\n%s\n%s" % (self.HOST, self.PATH, query),
			hashlib.sha256
		)
		signature = urllib.quote(base64.b64encode(hm.digest()))
		return "http://%s%s?%s&Signature=%s" % (self.HOST, self.PATH, query, signature)

def main():
	print "test"
	aca = AmazonCoverArt()
	# sample search
	covers = aca.search('Pur', 'Abenteuerland')
	#for cover in covers:
	if len(covers) > 0:
		print covers[0]["url"]

if __name__ == '__main__':
	main()
