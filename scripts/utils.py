#
# Copyright (c) 2017 Ensoft Ltd, 2008-2010 Martin Morrison, Matthew Earl
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

#
# Some Utility functions
#

import sys, os, tempfile, os.path

def writeOptions(name, vals, selected, onchange='', out=sys.stdout, optional=False):
    """
    Print a <select> block out of the given file-like object.  The
    first argument is the name of the select, the second is an array
    of tuples, the first element of which is the value for the option,
    and the second is the display name of the option. The third
    argument is the value to select by default, and the last, optional
    argument is the file to print to (stdout by default)
    The optional argument determines whether to insert a blank entry first.
    """

    out.write("<select id='%s' name='%s' onchange='%s'>\n" % (name, name, onchange))
    if optional:
        out.write(' <option></option>')
    for val in vals:
        if type(val) == str:
            value = val
            display = val
        else:
            value = val[0]
            display = val[1]
        if selected == value:
            out.write(" <option selected value='%s'>%s</option>\n" %
                      (value, display))
        else:
            out.write(" <option value='%s'>%s</option>\n" % (value, display))
    out.write("</select>\n")

def encodeHTML(string):
    """
    Encodes some things as HTML Entities, making them safe to print anywhere.

    Currently changes [&<>'"] "'# work around Emacs bug...
    """
    return string.replace('&', '&amp;') \
           .replace('<', '&lt;')        \
           .replace('>', '&gt;')        \
           .replace('"', '&quot;')      \
           .replace("'", '&apos;')

def decodeHTML(string):
    return string.replace('&apos;', "'") \
           .replace('&quot;', '"')       \
           .replace('&gt;', '>')         \
           .replace('&lt;', '>')         \
           .replace('&amp;', '&')

def encodeCDATA(string):
    return string.replace(']]>', ']]>]]&gt;<![CDATA[')

def encodeJS(string):
     return '"%s"' % string.replace('\\', '\\\\').replace('\n', r'\n').replace('"', r'\"')

def JSListFromSequence(arg):
    return "[%s]" % ", ".join(map(encodeJS, arg))

def stringToColour(string):
    """
    Converts a string into a CSS colour code. Uses the string's hash.
    """
    return "#%06x" % (abs(hash(str(hash(str(hash(string)))))) & 0xffffff)

def writeToTempFile(contents):
    fileObj, filename = tempfile.mkstemp()
    os.write(fileObj, contents.encode('utf8'))
    os.close(fileObj)

    return filename

def memoize(f):
    cache = {}
    def memoized(*args, **kwargs):
        key = (args, frozenset(list(kwargs.items())))
        if not key in cache:
            cache[key] = f(*args, **kwargs)
        return cache[key]
    return memoized

def search_paths(paths, file):
    for path in paths:
        candidate = os.path.join(path, file)
        if os.path.exists(candidate):
            return candidate
    return None

def dictDiff(a, b, nullVal=None):
    """Compare two dicts."""

    aKeys = set(a.keys())
    bKeys = set(b.keys())

    removed = aKeys - bKeys
    changed = aKeys & bKeys
    added = bKeys - aKeys

    for key in removed:
        yield (key, (a[key], nullVal))

    for key in changed:
        if a[key] != b[key]:
            yield (key, (a[key], b[key]))

    for key in added:
        yield (key, (nullVal, b[key]))

