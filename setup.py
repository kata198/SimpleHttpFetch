#!/usr/bin/env python

import os
from setuptools import setup


if __name__ == '__main__':

    summary = "Python module that will, in a single line, fetch an http/https url and return a string or dictionary (JSON)"

    try:
        dirName = os.path.dirname(__file__)
        if dirName and os.getcwd() != dirName:
            os.chdir(dirName)
    except:
        pass

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Error reading long description: %s\n' %(str(e),))
        long_description = summary

    setup(name='SimpleHttpFetch',
            version='4.0.0',
            packages=['SimpleHttpFetch'],
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            url='https://github.com/kata198/SimpleHttpFetch',
            maintainer_email='kata198@gmail.com',
            description=summary,
            long_description=long_description,
            license='LGPLv2',
            keywords=['fetch', 'url', 'GET', 'http', 'html', 'https', 'string', 'json', 'dict', 'as', 'simple', 'easy', 'basic', 'request', 'method', 'str', 'fetchUrl', 'fetchUrlAsJson', 'redirect', '301', 'absolute', 'relative'],
            classifiers=['Development Status :: 5 - Production/Stable',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.6',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Topic :: Internet :: WWW/HTTP',
                          'Topic :: Text Processing :: Markup :: HTML',
                          'Topic :: Software Development :: Libraries :: Python Modules',
            ]
    )



