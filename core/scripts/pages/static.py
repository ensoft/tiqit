#!/usr/bin/python
#
# Copyright (c) 2017 Ensoft Ltd, 2014 Matthew Earl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import re
import sys
import wsgiref.handlers

from tiqit import Arguments
from tiqit import Config
from tiqit import errorPage

# How much data is written to stdout at a time.
_CHUNK_SIZE = 512 * 1024 

subpath = Arguments()['path']
config = Config()
searchpaths = (config.section('general').getlist('staticpath') +
               [os.path.join(x, 'static') for x in
                config.section('general').getlist('overlays')])

_MIME_TYPES = (
    (r"\.css$", "text/css"),
    (r"\.js$", "application/javascript"),
    (r"\.gif$", "image/gif"),
    (r"\.png$", "image/png"),
)

class _SearchFailedError(Exception):
    """Raised when a file is not found in the search paths."""
    pass

def _search(subpath):
    """Search for a sub path within the search paths."""
    for search_path in searchpaths:
        abspath = os.path.join(search_path, subpath)
        if os.path.exists(abspath):
            return abspath
    raise _SearchFailedError

class _MimeTypeNotKnown(Exception):
    """Raised when the MIME-type for a path cannot be determined."""
    def __init__(self, path):
        self.path = path

def _get_mime_type(path):
    """Get the MIME type of a file, based on its filename."""
    for regex, mimetype in _MIME_TYPES:
        if re.search(regex, path):
            return mimetype
    raise _MimeTypeNotKnown


# Any of the internal functions can (in theory) raise any of the exceptions,
# hence the large try: block.
try:
    abspath = _search(subpath)

    # Write directly to the file-descriptor to circument the wrapper that
    # encodes output in UTF-8. (The wrapper is setup in index.py.)
    os.write(1, "Content-type: {}\n".format(_get_mime_type(abspath)))

    # Set the last-modified header to allow caching: The client will send
    # subsequent requests with the If-modified-since header, which we compare
    # to the current timestamp below. (Apache also reads these headers and will
    # automatically sent a 304 Not Modified instead of 200 OK in the case that
    # the timestamps match, and any document body we send here will be
    # dropped.)
    lastmodified = wsgiref.handlers.format_date_time(os.stat(abspath).st_mtime)
    os.write(1, "Last-modified: {}\n\n".format(lastmodified))

    if os.environ.get('HTTP_IF_MODIFIED_SINCE') != lastmodified:
        # Open the file and write it to stdout. Do it in chunks, whose size is
        # chosen to:
        #   - Have reasonable transient memory usage.
        #   - Minimize the time spent not writing to stdout.
        f = open(abspath, "rb")
        data = f.read(_CHUNK_SIZE)
        while data:
            os.write(1, data)
            data = f.read(_CHUNK_SIZE)
        f.close()
    else:
        # The client already has the latest version in cache. Don't bother
        # printing the file --- Apache will return a 304 Not Modified in this
        # case.
        pass

except _SearchFailedError:
    errorPage(404, "Path not found: {}".format(subpath))
except _MimeTypeNotKnown as e:
    errorPage(500, "Could not determine MIME-type for {}".format(e.path))
    
