# Copyright 2013 Fabian Behnke
# Copyright 2011 Fred Hatfull
#
# This file is now part of BeDJAY
# This file was originally part of Partify (https://github.com/fhats/partify).
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

from flask import jsonify, request, session, url_for

from partify import app
from partify.decorators import with_mpd

@app.route('/track/listplaylists', methods=['GET'])
@with_mpd
def listplaylists(mpd):

	response = {}
	result = mpd.listplaylists() #geht
	response['status'] = 'ok'
        response['results'] = result

#        test = mpd.listplaylistinfo("90s") #geht auch - jippi!!!
	return jsonify(response)

@app.route('/track/listplaylistinfo', methods=['GET'])
@with_mpd
def listplaylistinfo(mpd):
	mpd_search_terms = []
    	for term in ('playlist'):
        	if term in request.args:
            		mpd_search_terms.append(term)
            		mpd_search_terms.append(request.args[term])
#	print len(request.args)
#	print 'playlist' in request.args
	
        response = {}
	if 'playlist' in request.args:
        	result = mpd.listplaylistinfo(request.args['playlist'])
        	response['status'] = 'ok'
        	response['results'] = result
	else:
		response['status'] = 'error'
	        response['message'] = 'No search criteria specified!'

#        test = mpd.listplaylistinfo("90s") #geht auch - jippi!!!
        return jsonify(response)

@app.route('/track/search', methods=['GET'])
@with_mpd
def track_search(mpd):
    """Performs a search on the MPD server for tracks matching the specified criteria (as arguments in the URL i.e. HTTP GETs).
    Must contain at least one of ``artist``, ``title``, or ``album``.

    :param artist: The artist to search for
    :type artist: string, optional
    :param title: The title to search for
    :type title: string, optional
    :param album: The album to search for
    :type album: string, optional
    :returns: A list of search results
    :rtype: JSON string
    """
    mpd_search_terms = []
    for term in ('artist', 'title', 'album'):
        if term in request.args:
            mpd_search_terms.append(term)
            mpd_search_terms.append(request.args[term])
      
    response = {}

    if len(mpd_search_terms) > 0:
        results = mpd.search(*mpd_search_terms)
#	test = mpd.listplaylists() #geht
#	test = mpd.listplaylistinfo("90s") #geht auch - jippi!!!
#	print test
        response['status'] = 'ok'
        response['results'] = _process_results(results, mpd_search_terms)
#	i = 0
#	for result in response['results']:	
#		if result['time'] == "0":
#			print "delete"
#			print result['file']
#			print response['results'][i]['file']
#			print i
#			print response['results'][i]
#			del response['results'][i]
#		i = i + 1 
# 	i=0
#       	for result in response['results']:      
#                if result['time'] == "0":
#                       print "delete"
#                        print result['file']
#                        print response['results'][i]['file']
#                       print i
#                       print response['results'][i]
#                        del response['results'][i]
#                i = i + 1 

##		print i
#	i=0
#        for result in response['results']:      
#                if "artist" in result['file']:
#                       print "delete"
#                       print result['file']
#                       print i
#                       print response['results'][i]
#                        del response['results'][i]
#                i = i + 1 
	
	##Filter ZERO-Seconds tracks
	i=0
	n=len(response['results'])
	while i < n:
		if response['results'][i]['time'] == "0":
			del response['results'][i]
			n=n-1
		else: 
			i=i+1;
	for result in response['results']:
		print result
    else:
        response['status'] = 'error'
        response['message'] = 'No search criteria specified!'
    return jsonify(response)

def _process_results(results, search_terms):
    """Takes a result set in results and returns an organized result set sorted by the following criteria:

    * Sorted first by artist
    * Then by album
    * Then by order in album

    :param results: A list of search results from MPD
    :type results: list of dictionaries
    :param search_terms: The search terms used in the MPD query
    :type search_terms: list of strings
    :returns: A list of search results grouped appropriately
    :rtype: list of dictionaries
    """
    
    # Build a dict out of the search_terms list
    search_terms = dict( (k,v) for k,v in zip(search_terms[::2], search_terms[1::2]) )

    return sorted(results, key=lambda k: ( all( [k[term] != searched_term for term, searched_term in search_terms.items()] ), (k['album'], int(k['track']))) )
