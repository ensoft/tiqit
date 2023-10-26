#
# Copyright (c) 2017 Ensoft Ltd, 2011 Martin Morrison
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

"""
Provides an abstraction over the core metadata database structures provided by
Tiqit. This excludes the actual bug databases, which are owned by the
individual backends.

Currently, there are two sources for the data:
1. Pickled Python objects, always loaded, used for storing small, static data
2. Sqlite database, accessed on demand, used for storing larger data sets
"""

import tiqit
import sqlite3 as sqlite, os.path
import pickle

__all__ = [
    'initialise',
    'get', 'set',
    'cursor', 'commit',
    ]

_pickledData = {}
_sqlDb = None
_pickleChanged = False

def initialise():
    global _pickledData, _sqlDb
    global PICKLE_FILE, SQLDB_FILE

    PICKLE_FILE = os.path.join(tiqit.DATA_PATH, 'tiqit.pickle')
    SQLDB_FILE = os.path.join(tiqit.DATA_PATH, 'tiqit.db')

    with open(PICKLE_FILE, 'rb') as file:
        _pickledData = pickle.load(file)

    _sqlDb = sqlite.connect(SQLDB_FILE, timeout=5)

def get(key):
    if key not in _pickledData:
        tiqit.plugins.load_data_defaults(key)
    return _pickledData[key]

def set(key, value):
    global _pickleChanged
    _pickledData[key] = value
    _pickleChanged = True

def cursor():
    return _sqlDb.cursor()

def rollback():
    global _pickledData, _sqlDb

    with open(PICKLE_FILE, 'rb') as file:
        _pickledData = pickle.load(file)

    _sqlDb.rollback()

def commit():
    global _pickleChanged
    if _pickleChanged:
        with open(PICKLE_FILE, 'wb') as file:
            pickle.dump(_pickledData, file, -1)
        _pickleChanged = False

    _sqlDb.commit()
