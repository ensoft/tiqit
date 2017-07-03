#
# "Classes" provide the primary means for a single Tiqit installation to support
# different types of issue. Each class is effectively a separate installation,
# with the advantages that issues can reference each other, and even move
# between classes if necessary.
#
# The concept of classes is used beyond just this module to differentiate
# behaviour as required. Projects are specific instantiations of a Class, which
# additionally define which backend is in use. Projects and Classes are,
# for now at least, used interchangeably.
#
# This module defines the TiqitClass class, and defines the behaviour for
# extracting "formats". These formats are the HTML-format strings used to
# present bug data to the users. Formats usually belong to a specific "view", as
# well as a class. In future, they may also be user editable.
#

import os
from tiqit import *
from utils import search_paths

__all__ = [
    'TiqitClass',
    ]

class TiqitClass(object):
    """
    Classes have a bunch of formats.
    """

    _classes = {}

    def __init__(self, className):
        self.className = className
        self.formatCache = {}

        TiqitClass._classes[className] = self

    def forName(cls, className):
        _projmap = database.get('tiqit.projmap')
        className = _projmap.has_key(className) and _projmap[className] or className
        if TiqitClass._classes.has_key(className):
            return TiqitClass._classes[className]
        else:
            return TiqitClass._classes['default']
    forName = classmethod(forName)

    def getFormat(self, name):
        if not self.formatCache.has_key(name):
            self._loadFormat(name)
            
        return self.formatCache[name]

    def _loadFormat(self, name):
        """
        Load the format with the given name.
        """
        fmtdirs = ([os.path.join(DATA_PATH, 'formats')] +
                   [os.path.join(x, 'data', 'formats')
                    for x in Config().section('general').getlist('overlays')])

        fmtname = '%s:%s.format' % (self.className, name)

        fmtpath = search_paths(plugins.get_format_paths() + fmtdirs, fmtname)

        if fmtpath and os.path.exists(fmtpath):
            with open(fmtpath, 'r') as f:
                fmt = f.read()
        elif self.className != 'default':
            fmt = TiqitClass.forName('default').getFormat(name)
        else:
            fmt = "<p>This class does not support a format named '%s'.</p>" % name

        self.formatCache[name] = fmt

def initialise():
    TiqitClass('default')
    for cls in database.get('tiqit.classes'):
        TiqitClass(cls)
