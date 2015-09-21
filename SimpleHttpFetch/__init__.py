# Copyright (c) 2015 Tim Savannah under terms of LGPLv2.
#
#  SimpleHttpFetch supports through the most simple interface possible fetching of URLs as strings or JSON as dict


try:
    import httplib  # python2
except ImportError:
    import http.client as httplib # python3

import json
import re


__all__ = ('SimpleHttpFetchBadStatus', 'parseURL', 'getConnection', 'getRequestData', 'getRequestDataAsJson', 'fetchUrl', 'fetchUrlAsJson')

__version__ = '1.0.0'

__version_tuple__ = (1, 0, 0)

DEFAULT_USER_AGENT = 'SimpleHttpFetch %s' %(__version__,)

HTTP_PROTOCOL_URL_PATTERN = re.compile('^(?P<protocol>[h][t][t][p][s]{0,1}[:][/]{2}){0,1}(?P<domain>[a-zA-Z0-9\.]+){1}(?P<port>:[\d]+){0,1}(?P<rel_uri>[/].*){0,1}$')


############################
#   Methods                #
############################


def parseURL(url):
    '''
        parseURL - parses a url and returns a dictionary containing the pieces of information

        @param url <string> - A full URL (ex: http://www.example.com/test)

        @return - Dictionary describing url. Keys are:
            protocol <string> - http or https
            domain   <string> - host domain/server (ex: example.com)
            port     <int>    - TCP Port for request
            rel_uri  <string> - Relative URI of request (ex: /index.html)
    '''
    matchObj = HTTP_PROTOCOL_URL_PATTERN.match(url)
    if not matchObj:
        raise ValueError('Cannot parse url: "%s"' %(url,))
    groupDict = matchObj.groupdict()

    if not groupDict['protocol']:
        groupDict['protocol'] = 'http'
    else:
        groupDict['protocol'] = groupDict['protocol'][:-3] # Truncate http:// to http
    
    if not groupDict['port']:
        if groupDict['protocol'] == 'http':
            groupDict['port'] = 80
        else:
            groupDict['port'] = 443
    else:
        groupDict['port'] = int(groupDict['port'])

    if not groupDict['rel_uri']:
        groupDict['rel_uri'] = '/'

    return groupDict

def getConnection(url):
    '''
        getConnection - Get a connection object given a url. Supports http and https

        @return - Connection
    '''
    urlInfo = parseURL(url)
    
    if urlInfo['protocol'] == 'https':
        connection = httplib.HTTPSConnection(urlInfo['domain'], urlInfo['port'])
    else:
        connection = httplib.HTTPConnection(urlInfo['domain'], urlInfo['port'])

    return connection

def getRequestData(connection, url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT):
    '''
        getRequestData - Given a connection, fetch a URL and return a string of the contents. Use this to make multiple requests instead of fetchUrl to the same server, as it allows you to reuse a connection.
        
        Will follow relative redirects via Location header or 301 status.

        @param connection <obj> - return of getConnection function
        @parma url <str> - Url to fetch
        @param httpMethod <str> - An http method. Probably GET.
        @param userAgent <str>  - Your user agent. Defaults to SimpleHttpFetch <version>

        @return <str> - Web page contents

        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    if not url.startswith('/'):
        url = parseURL(url)['rel_uri']

    connection.request(httpMethod, url, [],{'User-agent': 'FetchURL'})
    response = connection.getresponse()
    if response.status == 301:
        try:
            response.read()
        except:
            pass
        locationHeader = response.getheader('Location')
        if locationHeader.startswith('/'): # Follow a relative redirect, but dont try to follow an absolute
            return getRequestData(connection, locationHeader, httpMethod)
    if response.status != 200:
        try:
            response.read() # Clear buffer if present
        except:
            pass
        toRaise = SimpleHttpFetchBadStatus('Got non-200 response from upstream server [%s]: (%d) %s' %(url, response.status, response.reason))
        toRaise.statusCode = response.status
        raise toRaise

    data = response.read()

    if type(data) == str:
        return data
    return data.decode('utf-8')

def getRequestDataAsJson(connection, url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT):
    '''
        getRequestDataAsJson - Given a connection, fetch a URL and return a string of the contents. Use this to make multiple requests to the same server instead of fetchUrlAsJson, as it allows you to reuse a connection.
        
        Will follow relative redirects via Location header or 301 status.

        @param connection <obj> - Return of getConnection function
        @param url <str> - Url to fetch
        @param httpMethod <str> - An http method. Probably GET.
        @param userAgent <str> - Your user agent. Defaults to SimpleHttpFetch <version>

        @return <dict> - Dictionary of parsed JSON on page

        @raises ValueError if webpage contents are not JSON-compatible
        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    data = getRequestData(connection, url, httpMethod)
    if not data:
        raise Exception('Server at "%s" returned no data' %(url,))

    try:
        ret = json.loads(data)
    except ValueError:
        raise ValueError('Could not parse data from server as JSON:\n%s\n' %(data,))

    return ret


def fetchUrl(url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT):
    '''
        fetchUrl - Fetches the contents of a url.

        Will follow relative redirects via Location header or 301 status.

        @param httpMethod <str> - HTTP Method (default GET)
        @param userAgent <str>  - User agent to provide, defaults to SimpleHttpFetch <version>

        @return <str> - Web page contents

        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    connection = getConnection(url)

    return getRequestData(connection, url, httpMethod, userAgent)

def fetchUrlAsJson(url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT):
    '''
        fetchUrl - Fetches the contents of a url and converts the JSON to a python dictionary.

        Will follow relative redirects via Location header or 301 status.

        @param httpMethod <str> - HTTP Method (default GET)
        @param userAgent <str>  - User agent to provide, defaults to SimpleHttpFetch <version>

        @return <dict> - Dictionary of parsed JSON on page

        @raises ValueError if webpage contents are not JSON-compatible
        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    connection = getConnection(url)

    return getRequestDataAsJson(connection, url, httpMethod, userAgent)


############################
#   Exceptions             #
############################

class SimpleHttpFetchBadStatus(Exception):
    '''
        Exception that is raised when a non-200 (Success) code is received from upstream server. This is not including 301 (redirects).

        Has a member "statusCode" which will list the status code returned.
    '''

    def __init__(self, msg, statusCode):
        Exception.__init__(self, msg)
        self.statusCode = statusCode

