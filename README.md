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

	jsonContents = SimpleHttpFetch.fetchUrlAsJson('https://www.example.com/myJsonServlet?username=myuser')


So simple!


Full Documentation
------------------

Full documentation on other methods and arguments can be found here:  http://htmlpreview.github.io/?https://github.com/kata198/SimpleHttpFetch/blob/master/doc/SimpleHttpFetch.html .
