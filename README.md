# SimpleHttpFetch

SimpleHttpFetch supports through the most simple interface possible fetching of URLs as strings or JSON as dict

It supports both HTTP and HTTPS through the same interface.
It will automatically follow 301 redirects and Location headers, you do not have to worry about handling that.

Fetching the contents of a URL could not be simpler!!!


Example Usage
-------------

Fetch google.com over HTTPS and return contents as a string:

	import SimpleHttpFetch

	contents = SimpleHttpFetch.fetchUrl('https://www.google.com')


That's it!!!


You can also convert a page that returns JSON into a dictonary with a single call as well!


Fetch a servlet that returns JSON from example.com over HTTP, and convert to a python dictionary:

	import SimpleHttpFetch

	jsonContents = SimpleHttpFetch.fetchUrlAsJson('http://www.example.com/myJsonServlet?username=myuser')


So simple!


Fetch the linux kernel, do not try to decode into text.:

	import SimpleHttpFetch

	kernel = SimpleHttpFetch.fetchUrlRaw('https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.4.1.tar.xz')


Encodings
---------

SimpleHttpFetch will check for the "charset" defined in Content-type header, and use that as the encoding. If that is not found, it will use the "defaultEncoding" param, which defaults to utf-8. 


**Binary Data**

To fetch binary data, use the "fetchUrlRaw" method, or pass "nodecode" as the "defaultEncoding" paramater. Use this mode to fetch images, video, tarballs, etc.


Extra Headers
-------------

The automatic headers needed for an HTTP/HTTPS request are provided by default, but you may override or provide your own headers through the "headers" parameter to most functions.


Full Documentation
------------------

Full documentation on other methods and arguments can be found here:  http://htmlpreview.github.io/?https://github.com/kata198/SimpleHttpFetch/blob/master/doc/SimpleHttpFetch.html?vers=2 .
