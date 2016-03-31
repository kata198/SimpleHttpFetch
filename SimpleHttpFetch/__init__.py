# Copyright (c) 2015-2016 Tim Savannah under terms of LGPLv2.
#
#  SimpleHttpFetch supports through the most simple interface possible fetching of URLs as strings or JSON as dict


try:
    import httplib  # python2
except ImportError:
    import http.client as httplib # python3

import json
import re
import sys


__all__ = ('SimpleHttpFetchBadStatus', 'SimpleHttpFetchTooManyRedirects', 'parseURL', 'getConnection', 'getRequestData', 'getRequestDataAsJson', 'fetchUrl', 'fetchUrlAsJson', 'fetchUrlRaw')

__version__ = '4.0.0'

__version_tuple__ = (4, 0, 0)

DEFAULT_USER_AGENT = 'SimpleHttpFetch %s' %(__version__,)

HTTP_PROTOCOL_URL_PATTERN = re.compile('^(?P<protocol>[h][t][t][p][s]{0,1}[:][/]{2}){0,1}(?P<domain>[a-zA-Z0-9\.\-\_]+){1}(?P<port>:[\d]+){0,1}(?P<rel_uri>[/].*){0,1}$')


NO_DECODE = 'nodecode'

CHARSET_PATTERN = re.compile('.*;[ ]*charset=(?P<charset>.*)')


MAX_REDIRECT_DEPTH = 15

############################
#   Methods - Main         #
############################


def fetchUrl(url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT, defaultEncoding='utf-8', headers=None):
    '''
        fetchUrl - Fetches the contents of a url.

        Will follow redirects via Location header or 301 status.

        @param httpMethod <str> - HTTP Method (default GET)
        @param userAgent <str>  - User agent to provide, defaults to SimpleHttpFetch <version>
        @param defaultEncoding <str> - default utf-8. Encoding to use if one is not specified in headers. If set to "nodecode", the results will not be decoded regardless of headers (use for binary data)
        @param headers <None/dict> - overrides to default headers to send. keys is header name, value is header value.

        @return <str> - Web page contents

        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    connection = getConnection(url)

    return getRequestData(connection, url, httpMethod, userAgent, defaultEncoding, headers)


def fetchUrlRaw(url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT, headers=None):
    '''
        fetchUrlRaw - Fetches the contents of a url without decoding the data.

        Will follow redirects via Location header or 301 status.

        @param httpMethod <str> - HTTP Method (default GET)
        @param userAgent <str>  - User agent to provide, defaults to SimpleHttpFetch <version>
        @param headers <None/dict> - overrides to default headers to send. keys is header name, value is header value.

        @return <bytes> - Web page contents, unencoded.

        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    connection = getConnection(url)

    return getRequestData(connection, url, httpMethod, userAgent, NO_DECODE, headers)
    

def fetchUrlAsJson(url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT, defaultEncoding='utf-8', headers=None):
    '''
        fetchUrl - Fetches the contents of a url and converts the JSON to a python dictionary.

        Will follow redirects via Location header or 301 status.

        @param httpMethod <str> - HTTP Method (default GET)
        @param userAgent <str>  - User agent to provide, defaults to SimpleHttpFetch <version>
        @param defaultEncoding <str> - default utf-8. Encoding to use if one is not specified in headers. If set to "nodecode", the results will not be decoded regardless of headers (use for binary data)
        @param headers <None/dict> - overrides to default headers to send. keys is header name, value is header value.

        @return <dict> - Dictionary of parsed JSON on page

        @raises ValueError if webpage contents are not JSON-compatible
        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    connection = getConnection(url)

    return getRequestDataAsJson(connection, url, httpMethod, userAgent, defaultEncoding, headers)



############################
#   Methods - Helpers      #
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

def getRequestData(connection, url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT, defaultEncoding='utf-8', headers=None, _depth=None):
    '''
        getRequestData - Given a connection, fetch a URL and return a string of the contents. Use this to make multiple requests instead of fetchUrl to the same server, as it allows you to reuse a connection.
        
        Will follow redirects via Location header or 301 status.

        @param connection <obj> - return of getConnection function
        @parma url <str> - Url to fetch
        @param httpMethod <str> - An http method. Probably GET.
        @param userAgent <str>  - Your user agent. Defaults to SimpleHttpFetch <version>
        @param defaultEncoding <str> - default utf-8. Encoding to use if one is not specified in headers. If set to "nodecode", the results will not be decoded regardless of headers (use for binary data)
        @param headers <None/dict> - overrides to default headers to send. keys is header name, value is header value
        @param _depth <None/list> - If you pass in a list, you can check that list after the call (the function will modify it) to see if any redirects (301's) were followed. Each url fetched will have an entry, so len(_depth) == 1 means no redirects were followed.

        @return <str> - Web page contents

        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    if _depth is None:
        _depth = []

    _depth.append(url)

    if not url.startswith('/'):
        url = parseURL(url)['rel_uri']

    if not headers:
        headers = {}
    if 'User-agent' not in headers:
        headers['User-agent'] = userAgent

    connection.request(httpMethod, url, '', headers)
    response = connection.getresponse()
    if response.status == 301:
        if len(_depth) > MAX_REDIRECT_DEPTH:
            raise SimpleHttpFetchTooManyRedirects(_depth)

        try:
            response.read()
        except:
            pass
        locationHeader = response.getheader('Location')
        if locationHeader.startswith('/'): # Follow a relative redirect on same connection
            return getRequestData(connection, locationHeader, httpMethod, userAgent, defaultEncoding, headers, _depth)
        else:
            newConnection = getConnection(locationHeader)
            return getRequestData(newConnection, locationHeader, httpMethod, userAgent, defaultEncoding, headers, _depth)

    if response.status != 200:
        try:
            response.read() # Clear buffer if present
        except:
            pass
        toRaise = SimpleHttpFetchBadStatus('Got non-200 response from upstream server [%s]: (%d) %s' %(url, response.status, response.reason), response.status, response.reason)
        toRaise.statusCode = response.status
        raise toRaise

    
    data = response.read()
    if defaultEncoding == NO_DECODE:
        return data

    encoding = extractEncodingFromHeaders(response) or defaultEncoding or sys.getdefaultencoding()

    if encoding == NO_DECODE:
        return data


    return data.decode(encoding)

def getRequestDataAsJson(connection, url, httpMethod='GET', userAgent=DEFAULT_USER_AGENT, defaultEncoding='utf-8', headers=None):
    '''
        getRequestDataAsJson - Given a connection, fetch a URL and return a string of the contents. Use this to make multiple requests to the same server instead of fetchUrlAsJson, as it allows you to reuse a connection.
        
        Will follow relative redirects via Location header or 301 status.

        @param connection <obj> - Return of getConnection function
        @param url <str> - Url to fetch
        @param httpMethod <str> - An http method. Probably GET.
        @param userAgent <str> - Your user agent. Defaults to SimpleHttpFetch <version>
        @param defaultEncoding <str> - default utf-8. Encoding to use if one is not specified in headers. If set to "nodecode", the results will not be decoded regardless of headers (use for binary data)
        @param headers <None/dict> - overrides to default headers to send. keys is header name, value is header value.

        @return <dict> - Dictionary of parsed JSON on page

        @raises ValueError if webpage contents are not JSON-compatible
        @raises SimpleHttpFetchBadStatus If page does not return status 200 (success)
    '''
    data = getRequestData(connection, url, httpMethod, userAgent, defaultEncoding, headers)
    if not data:
        raise Exception('Server at "%s" returned no data' %(url,))

    try:
        ret = json.loads(data)
    except ValueError:
        raise ValueError('Could not parse data from server as JSON:\n%s\n' %(data,))

    return ret


def extractEncodingFromHeaders(response):
    '''
        extractEncodingFromHeaders - Extract encoding if present from "Content-type" header.

        @param response - Response object

        @return - String of encoding, or None if no encoding found.
    '''
    contentTypeHeader = response.getheader('Content-type')
    if contentTypeHeader:
        charSetMatch = CHARSET_PATTERN.match(contentTypeHeader)
        if charSetMatch:
            return charSetMatch.groupdict()['charset'].lower()
    return None
            

############################
#   Exceptions             #
############################

class SimpleHttpFetchBadStatus(Exception):
    '''
        Exception that is raised when a non-200 (Success) code is received from upstream server. This is not including 301 (redirects).

        Has a member "statusCode" which will list the status code returned.
    '''

    def __init__(self, msg, statusCode=None, reason=None):
        Exception.__init__(self, msg)
        self.statusCode = statusCode
        self.reason = reason


class SimpleHttpFetchTooManyRedirects(Exception):
    '''
        Too many redirects have been followed and we've given up. The message will contain after the first newline character the list of urls fetched.
    '''

    def __init__(self, urls):
        msg = "Too many redirects (%d):\n%s" %(len(urls), str(urls))
        Exception.__init__(self, msg)
