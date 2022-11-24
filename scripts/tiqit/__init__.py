#
# This Library contains utility functions and variables. These relate to
# the display of HTML pages, management of preferences, news, joke feeds, etc.
#

import sys, os, urllib.request, urllib.parse, urllib.error, subprocess, time, cgi, tempfile, re, random, sqlite3 as sqlite, string
import itertools
import configparser, types
import pickle as pickle
from utils import *
from .toolbars import *
from . import database
from . import cookie

__all__ = [
    'MSG_WARNING', 'MSG_INFO', 'MSG_WARNING', 'queueMessage', 'sendMessage',
    'printMessages', 'printXMLMessages', 'msgIcons', 'MSG_ERROR',
    'Arguments', 'extractBugIds', 'timeMark', 'getBaseHost',
    'loadPrefs', 'savePrefs', 'encodeCDATA',
    'getBasePath', 'getSavedSearches', 'getNamedBugs', 'encodeJS',
    'getAdministrators',
    'authenticate', 'generateToken', 'loadPlugins', 'plugins', 'Config',
    'writeOptions', 'Prefs', 'stringToColour', 'writeToTempFile',
    'PAGE_HOME', 'PAGE_NEW', 'PAGE_VIEW', 'PAGE_SEARCH', 'PAGE_RESULTS',
    'PAGE_PREFS', 'PAGE_NEWS', 'printPageHeader', 'printPageFooter',
    'DATA_PATH',
    'PAGE_HOMEMETA', 'PAGE_FIELDS', 'PAGE_PROJECTS', 'PAGE_DEFVALS',
    'TiqitException', 'TiqitInfo', 'TiqitWarning', 'TiqitError',
    'redirect', 'NEWS_PATH', 'VERSION_STRING',
    'news', 'encodeHTML', 'loadSavedSearch', 'printSectionHeader',
    'printSectionFooter', 'pages', 'loadNamedBug', 'tbhandler',
    'SITE_MAIN', 'SITE_META',
    'database', 'initialise',
    'errorPage',
    'CFG_DIRS',
]

times = [("start", time.time())]

#
# Global Properties
#

# Global Constants

MAJ_VER   = 1
MIN_VER   = 1
PATCH_VER = 2
DEV_VER   = 1

VERSION = (MAJ_VER, MIN_VER, PATCH_VER)
VERSION_STRING = '.'.join(map(str, VERSION)) + (DEV_VER < 0 and "b%d" % -DEV_VER or "")

def initialise():
    # Database is needed to load fields
    database.initialise()
    # As are plugins (so they can add custom ones)
    loadPlugins()
    # Backend loads the backends and the fields
    import backend, frontend
    backend.initialise()
    frontend.classes.initialise()
    frontend.loadBugViews()

def errorPage(code, msg=""):
    print("""Content-type: text/html
Status: %d

<html>
  <head>
    <title>Error - %d</title>
  </head>
  <body>
    <h1>Error - %d</h1>
    %s
  </body>
</html>""" % (code, code, code, encodeHTML(msg)))

#
# Bug ID extractor
#

def extractBugIds(string):
    """
    Extract anything and everything that looks like a bug id from the
    given string. Will also normalise bugids (so can be used to
    normalise tqtSd12345 into TQTsd12345).
    """

    backends = (k for k, v in Config().section('backends').items())
    match = re.findall(r"(?:_|\b)((?:%s)?[A-Z][A-Z]\d\d\d\d\d)(?:_|\b)" %
                           "|".join(backends),
                       string,
                       re.I | re.M)

    if match:
        bugids = [x[:3].upper() + x[3:].lower() for x in match]
    else:
        bugids = []

    return list(dict.fromkeys(bugids))
    return plugins.findBugIds(string)

#
# Arguments
#

class Arguments(object):
    """
    This class provides a nicer wrapper around the CGI FieldStorage object for
    managing CGI arguments. It is a Singleton class, and will always return
    the same object when instantiated.
    """

    singleton = None
    def __new__(self):
        """
        Allocates a singleton object if not yet done, and returns that object
        always.
        """
        if not Arguments.singleton:
            Arguments.singleton = object.__new__(self)
        return Arguments.singleton

    def __init__(self):
        """
        The Constructor is careful to only init itself once.
        """
        if not hasattr(self, 'cgi'):
            self.cgi = cgi.FieldStorage(keep_blank_values=True)
            self.overrides = {}

    def keys(self):
        return list(self.cgi.keys()) + list(self.overrides.keys())

    def __contains__(self, key):
        return key in self.cgi or key in self.overrides

    def __repr__(self):
        string = '{'
        for key in list(self.keys()):
            string += "'%s': '%s', " % (str(key), str(self[key]))
        string = string[:-2]
        string += '}'
        return string

    def __getitem__(self, key):
        if key in self.overrides:
            val = self.overrides[key]
        elif key in self.cgi:
            val = self.cgi[key].value
        else:
            val = ''

        # Replace unicode newlines with regular newlines
        # in any argument values
        return val.replace('\u2028', '\n')

    def __setitem__(self, key, val):
        self.overrides[key] = val

    def __iter__(self):
        for x in self.cgi:
            if x not in self.overrides:
                yield x
        for x in self.overrides:
            yield x

    def asList(self, key):
        return self.cgi.getlist(key)

    def ofType(self, root, dims=1):
        indices = [1] * dims
        pos = -1

        while True:
            name = '%s%s' % (root, ('[%d]' * dims) % tuple(indices))
            # Check if we have this item
            if name in self:
                yield (indices, self[name])
                pos = -1
                indices[pos] += 1
            # Otherwise, can only continue if we have multiple dimensions
            # and haven't already tried incrementing them all
            elif indices[pos] > 1 and dims + pos > 0:
                indices[pos] = 1
                pos -= 1
                indices[pos] += 1
            else:
                return

    def writeToTempFile(self, key):
        fileObj, filename = tempfile.mkstemp()

        if self.cgi[key].file:
            while True:
                chunk = self.cgi[key].file.read(10000)
                if not chunk:
                    break
                os.write(fileObj, chunk)
        else:
            os.write(fileObj, self.cgi[key].value)

        os.close(fileObj)

        return filename

#
# Configuration (of TiQiT itself)
#

class Config:
    cfg_defaults = {
        'general': {
            'sitename': 'NIT',
            'sitetitle': 'Nameless Issue Tracker',
            'siteintro': 'This is an Issue Tracker with no name.',
            'infourl': 'https://github.com/ensoft/tiqit',
            'administrators': '',
            'datapath': '/var/lib/tiqit/data/',
            'pluginpath': '/usr/share/tiqit/scripts/plugins/',
            'staticpath': '/usr/share/tiqit/static/',
            'overlays': '',
            },
        'userdetails': {
            },
        'plugins': {
            },
        'backends': {
            },
        'otherlinks': {
            },
        'helpfields': {
            },
        }

    class ConfigSection:
        def __init__(self, cfg, name):
            self.cfg = cfg
            self.name = name
            self.opts = self.name in Config.cfg_defaults and Config.cfg_defaults[self.name] or {}
        def get(self, key, raw=False):
            try:
                return self.cfg.get(self.name, key, raw=raw)
            except configparser.NoOptionError:
                # Maybe the option is in the defaults
                if key in Config.cfg_defaults[self.name]:
                    return Config.cfg_defaults[self.name][key]
                raise
        def __getitem__(self, key):
            try:
                return self.get(key)
            except configparser.NoOptionError:
                raise KeyError
        def __contains__(self, item):
            try:
                _ = self.get(item)
                return True
            except configparser.NoOptionError:
                return False
        def getlist(self, key):
            ret_list = self[key].split()
            return ret_list if ret_list else []                
        def items(self, raw=False):
            items = self.cfg.items(self.name, raw)
            opts = self.name in Config.cfg_defaults and Config.cfg_defaults[self.name] or {}
            items.extend([(x, opts[x]) for x in opts if not self.cfg.has_option(self.name, x)])
            return items
        def has_key(self, key):
            return self.cfg.has_option(self.name, key) or key in Config.cfg_defaults[self.name]

    singleton = None
    def __new__(self):
        """
        Allocates a singleton object if not yet done, and returns that object
        always.
        """
        if not Config.singleton:
            Config.singleton = object.__new__(self)
        return Config.singleton

    def __init__(self):
        """
        The Constructor is careful to only init itself once.
        """
        if not hasattr(self, 'cfg'):
            self.readConfig(CFG_PATHS)

    def readConfig(self, paths):
        for path in paths:
           if os.path.isfile(path):
               break
        else:
            raise Exception('Config file not found in any of the expected ' +
                    'locations: %s' % ', '.join(CFG_PATHS))

        self.cfg = configparser.ConfigParser()
        [self.cfg.add_section(sect) for sect in Config.cfg_defaults]
        self.cfg.optionxform = str

        if os.path.exists(path):
            self.cfg.read(path)

    def section(self, name):
        return Config.ConfigSection(self.cfg, name)

    def get(self, section, key, raw=False):
        return self.section(section).get(key, raw)


#
# Data file paths
#

CFG_PATHS    = ['../config',
                '/etc/tiqit/tiqit.conf']
if 'TIQIT_CONFIG' in os.environ:
    CFG_PATHS = [os.environ['TIQIT_CONFIG']] + CFG_PATHS
gen_cfg = Config().section('general')
DATA_PATH = gen_cfg.get('datapath')
if not DATA_PATH.endswith('/'):
    DATA_PATH = DATA_PATH + '/'
PROFILE_PATH = DATA_PATH + 'profiles/'
NEWS_PATH    = DATA_PATH + 'news/'
CFG_DIRS = ["../",
            "/etc/tiqit/"]


#
# Administrators
#

def getAdministrators():
    return tuple(Config().section('general').getlist('administrators'))

#
# Authentication (for hypothetical future CLI)
#

def generateToken():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    token = ''.join([random.choice(chars) for i in range(128)])

    # Connect to the DB
    cu = database.cursor()

    # Before we insert this new token, we should probably delete any old tokens
    # generated for the same user on the same host
    cu.execute('DELETE FROM [tiqit#authtokens] WHERE uname = ? AND who = ?',
               (os.environ['REMOTE_USER'], os.environ['REMOTE_ADDR']))

    cu.execute('INSERT INTO [tiqit#authtokens] (uname, token, created, who) '
               'VALUES (?, ?, datetime("now"), ?)',
               (os.environ['REMOTE_USER'], token, os.environ['REMOTE_ADDR']))
    cu.close()
    database.commit()
    return token

def authenticate():
    if not os.environ.get('REMOTE_USER'):
        raise TiqitError("User is not logged in.")
    elif os.environ['REMOTE_USER'] == 'tiqit-api':
        # Should be a custom header with the auto token
        cu = database.cursor()
        cu.execute('SELECT uname FROM [tiqit#authtokens] WHERE token = ?',
                   (os.environ['HTTP_X_TIQIT_TOKEN'],))
        uname = cu.fetchone()
        if uname and uname[0]:
            os.environ['REMOTE_USER'] = uname[0]
        else:
            print("Status: 409\n\n")
            sys.exit()
        cu.close()
        database.commit()

#
# Plugins
#

class PluginManager:
    """
    Manages all plugins.
    """

    class Plugin:
        def __init__(self, modname):
            old_path = sys.path
            sys.path = (Config().section('general').getlist('pluginpath') + 
                        ['{}/scripts/plugins/'.format(x)
                         for x in Config().section('general')
                                                          .getlist('overlays')]
                        + sys.path)
            tmp = __import__(modname)
            sys.path = old_path
            self.module = sys.modules[modname]

        def __getattr__(self, key):
            if hasattr(self.module, key):
                return getattr(self.module, key)
            else:
                return self

        def __call__(self, *args, **kwargs):
            return self

        def __bool__(self):
            return False

    def __init__(self):
        self._plugins = []

    def load(self, plugin):
        self._plugins.append(PluginManager.Plugin(plugin))

    def _call(self, func, *args, **kwargs):
        """
        Calls the function called 'func', passing in args and kwargs, on every
        loaded plugin, aggregating the results into a list. Empty values are
        silently dropped (i.e. those evaluating to False in a boolean context).

        If every item of the list is itself a list, then the lists are
        collapsed. If every item is a dict, then they are collapsed and a single
        dict is returned (later dicts overwrite duplicate values in earlier
        dicts; since plugin load order is undefined, this means the overwrite
        order is also undefined). Otherwise, the list is simply returned.
        """
        retvals = []
        rettype = None
        for plugin in self._plugins:
            retvals.append(getattr(plugin, func)(*args, **kwargs))
            if not retvals[-1]:
                retvals = retvals[:-1]
                continue
            if not rettype:
                rettype = type(retvals[-1])
            elif rettype != type(None):
                if rettype != type(retvals[-1]):
                    rettype = type(None)

        # Collapse if necessary
        if rettype == list:
            retlist = []
            [retlist.extend(x) for x in retvals]
            return retlist
        elif rettype == dict:
            retdict = {}
            [retdict.update(x) for x in retvals]
            return retdict
        else:
            return retvals

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            # Slightly convoluted: the outer list comprehension removes empty
            # return values, while the inner one calls the func on each plugin
            #return lambda *args, **kwargs: [x for x in [getattr(plugin, func)(*args, **kwargs) for plugin in self._plugins] if x]
            # With the desire to collapse lists/dicts, needed a separate method
            return lambda *args, **kwargs: self._call(key, *args, **kwargs)

plugins = PluginManager()

def loadPlugins():
    cfg = Config()

    # Some plugins are "built-in"
    plugins.load('tiqit.customfields')
    plugins.load('tiqit.helppages')
    plugins.load('tiqit.recents')
    plugins.load('tiqit.summary')
    plugins.load('tiqit.baseinfo')

    for plugin in cfg.cfg.options('plugins'):
        if cfg.cfg.getboolean('plugins', plugin):
            plugins.load(plugin)

    # At this stage, we need to pre-populate some things from the plugins
    # Preferences.
    Prefs.defaults.update(plugins.getDefaultPrefs())

    # Some Prefs are required by the Tiqit core, but the defaults must be
    # filled in by plugins. Check that this has been done.
    unset = [k for k, v in Prefs.defaults.items() if v == None]
    assert len(unset) == 0, "Default prefs required for %s" % unset

#
# Messaging
#

# The Messaging APIs provide a mechanism to transfer messages from one page to
# another, via Cookies, and then display them in nice little bars at the top
# of a page. Use queueMessage() to queue up messages, and then printMessages()
# to display them all. printMessages() will also display warnings about browser
# and Bug Class compatibility, as well as any cookie'd messages.

msgQueue = []

MSG_WARNING = 0
MSG_INFO    = 1
MSG_ERROR   = 2
MSG_TIP     = 3
MSG_NEWS    = 4

msgIcons = {
    MSG_WARNING: ("/!\\", 'images/warning-small.png'),
    MSG_INFO:    ("(i)", 'images/about-small.png'),
    MSG_ERROR:   ("[x]", 'images/error-small.png'),
    MSG_TIP:     ("[Tip]", 'images/tip-small.png'),
    MSG_NEWS:    ("[News]", 'images/text_rich-small.png'),
}

msgText = {"/!\\": MSG_WARNING,
           "(i)": MSG_INFO,
           "[x]": MSG_ERROR,
           "[Tip]": MSG_TIP,
           "[News]": MSG_NEWS,
}

def _printMsg(msgType, msg, extraclass='', tick=None,
              clear=("this.parentNode.parentNode.removeChild(this.parentNode)",
                     "Clear Message", '')):
    """
    Actually print out a message.
    """
    tickStr = "<img src='%s' onclick=%s title='%s' alt='%s' style='float: right'>" % ('images/tick-small.png', encodeJS(tick[0]), encodeHTML(tick[1]), encodeHTML(tick[2])) if tick else ''
    print("""
<p class='tiqitMessage %s'>
  %s<img src='%s' alt='%s' onclick=%s title='%s' alt='%s'>
  %s
</p>""" % (extraclass, tickStr, msgIcons[msgType][1], msgIcons[msgType][0],
           encodeJS(clear[0]), encodeHTML(clear[1]), encodeHTML(clear[2]), msg))

def queueMessage(msgType, msg):
    """
    Queue up a message to be displayed when printMessages() is called,
    later. The first argument is the type of the message (one of the
    MSG_* values) and the second is an HTML string to be printed,
    """
    msgQueue.append((msgType, msg))

def sendMessage(msgType, msg):
    """
    Sends a message (via cookie) to the next page. This MUST be called
    before any headers are printed.
    """
    if currentPage:
        # We kind of assume it's OK to add a <script> tag right here
        sys.stdout.flush()
        print("<script type='text/javascript'>sendMessage(%d, %s);</script>" % \
              (msgType, encodeJS(msg)))
        sys.stdout.flush()
    else:
        queueMessage(msgType, msg)

def printMessages():
    """
    Prints all messages for this page. This includes messages passed on via cookie 
    and any queued messages.
    """
    # Let plugins print their own messages
    for typ, msg, cls in plugins.printExtraMessages():
        _printMsg(typ, msg, cls)

    # Print number of unread news items (if any)
    _printNewsBanner()

    # Print queued messages
    for t, m in msgQueue:
        _printMsg(t, m)

    # Print out any message in a cookie
    try:
        if 'HTTP_COOKIE' in os.environ:
            for cookie in os.environ['HTTP_COOKIE'].split(';'):
                name, update = (urllib.parse.unquote(x) for x in cookie.strip().split('=', 1))
                if name == 'update':
                    # Get the relevant icon
                    msgType = msgText[update[:3]]

                    _printMsg(msgType, update[4:])
                    break
    except:
        # Never mind
        _printMsg(MSG_ERROR, "Failed to parse cookies! Cookie string: '%s'" % os.environ['HTTP_COOKIE'])

def printXMLMessages():
    print(" <messages>")
    # Print queued messages
    for t, m in msgQueue:
        print("  <message type='%s'><![CDATA[%s]]></message>" % (t, m))
    print(" </messages>")

#
# Preferences
#

class Prefs(dict):
    """
    User preferences.
    """
    defaults = {
        'displayGeneral': 'show',
        'displayExtra': 'show',
        'displayNotes': 'show',
        'displayGraphs': 'show',
        'displayHistory': 'hide',
        'displayRelates': 'show',
        'selection1': None,
        'selection2': None,
        'selection3': None,
        'selection4': None,
        'selection5': None,
        'selection6': None,
        'selectionCount': '6',
        'sort1': 'Identifier',
        'sortOrder1': 'ASC',
        'miscOneBugResults': 'false',
        'miscHideSavedSearches': 'false',
        'miscHideNamedBugs': 'false',
        'miscHideFortunes': 'false',
        'miscGetDupedToRelates': 'false',
        'miscDefaultBugType': 'bug',
        'miscDefaultsPerBugView': {},
        'miscShowSearchName': 'false',
        'miscGroupByPrimaryKey': 'false',
        'miscPlaySound': 'false',
        'miscShowPlaySound': 'false',
        'miscNeverAutoRefreshResults': 'false',
        'miscHidePerRowAutoUpdateClear': 'false',
        'miscHideWatermark': 'false',
        'miscDisableDblclkEdit': 'false',
        'miscToolbar': 'both',
        'miscMaxAutoloadSize': '10485760',
        'miscAlwaysFullView': 'false',
        'viewOrderGeneral': '1',
        'viewOrderExtra': '2',
        'viewOrderNotes': '3',
        'viewOrderGraphs': '4',
        'viewOrderHistory': '5',
        'viewOrderRelates': '6',
        }

    def __init__(self):
        self['newsTimeStamp'] = time.time()

    def __getattr__(self, key):
        """
        Allows getting preferences by attribute access.
        """
        if key in self:
            return self[key]
        elif key in Prefs.defaults:
            return Prefs.defaults[key]
        else:
            return dict.__getattr__(self, key)
    def __setattr__(self, key, value):
        """
        Sets attributes in dict instead.
        """
        if key in Prefs.defaults and Prefs.defaults[key] == value:
            if key in self:
                del self[key]
        elif value:
            self[key] = value
        else:
            if key in self:
                del self[key]
    def __getitem__(self, key):
        """
        Allow getting defaults.
        """
        if key in self:
            return dict.__getitem__(self, key)
        elif key in Prefs.defaults:
            return Prefs.defaults[key]
        else:
            raise KeyError
    def ofType(self, prefix):
        """
        Gets a sub-dict of preferences that start with the given prefix.
        """
        temp = Prefs.defaults.copy()
        temp.update(self)
        return dict([(x, self[x]) for x in temp if x.startswith(prefix)])

    def iterType(self, prefix):
        """
        Iterate the numerically-indexed preferences that have the given prefix.
        """
        for index in itertools.count(1):
            value = getattr(self, "{}{:d}".format(prefix, index), None) 
            if value is not None:
                yield index, value
            else:
                break

    def printBool(self, name, desc=None):
        if not desc:
            desc = name
        return "<tr><td><input type='checkbox' name='%s'%s></td><td>%s</td></tr>" % (encodeHTML(name), self[name] != 'false' and ' checked' or '', encodeHTML(desc))


prefsCache = {}

def loadPrefs(username=None, saveTimestamp=False):
    """
    Load preferences for the given user. This function caches loads,
    so subsequent loads are fast. News is also loaded for the user, so
    only call this function for visible pages, or the news will be
    lost! If you must call it on a hidden page (or one that doesn't
    show news) pass True for the 'saveTimestamp' argument.
    """
    if 'REMOTE_USER' not in os.environ:
        raise TiqitError("User is not logged in")
    
    if not username:
        username = os.environ['REMOTE_USER']

    mine = (username == os.environ['REMOTE_USER'])

    if username in prefsCache:
        return prefsCache[username]

    profile = PROFILE_PATH + username

    if os.path.exists(profile):
        st = os.stat(profile)
        fd = open(profile, 'rb')
        try:
            prefs = pickle.load(fd)
            prefsCache[username] = prefs
            if username != os.environ['REMOTE_USER'] or saveTimestamp:
                os.utime(profile, (st.st_atime, st.st_mtime))
            else:
                os.utime(profile, None)
                
        finally:
            fd.close()
    else:
        # Only create a new profile if the user himself is getting the prefs
        if mine:
            prefs = savePrefs(Prefs())
        else:
            raise TiqitError("No such user '%s'" % username)

    return prefs

def savePrefs(prefs):
    """
    Save preferences.
    """

    if not os.path.exists(PROFILE_PATH):
        # Should only get here for a new instance
        os.mkdir(PROFILE_PATH)

    profile = PROFILE_PATH + os.environ['REMOTE_USER']

    fd = open(profile, 'wb')
    try:
        pickle.dump(prefs, fd)
        prefsCache[os.environ['REMOTE_USER']] = prefs
    finally:
        fd.close()

    return prefs

# SavedSearches and NamedBugs

def _getSearchName(ofType):
    """
    Get the search name associated with this page, if this is a search page (None otherwise).
    """
    out = None

    if len(os.environ['QUERY_STRING']) > 0:
        prefs = loadPrefs()

        namedPages = ((x[len(ofType):], prefs[x]) for x in prefs.ofType(ofType))

        for name, url in namedPages:
            if url.endswith(os.environ['QUERY_STRING']):
                out = name

    return out

def _getNamedPages(ofType):
    """
    Internal function to get named searches/bugs.
    """
    prefs = loadPrefs()

    namedPages = [(x[len(ofType):], prefs[x]) for x in prefs.ofType(ofType)]
    needSave = True

    for name, url in namedPages:
        if url.endswith(os.environ['QUERY_STRING']):
            needSave = False

    namedPages.sort()

    return namedPages, needSave

def getSavedSearches():
    """
    Load Saved Searches from the preferences. Return value is a
    2-tuple, the first item of which is a list of (name, url) tuples
    of saved searches, the second is a boolean saying whether the
    current page is not in the saved searches, and hence whether a
    save is required. If this is False, then the current page (query)
    is not yet saved.
    """
    return _getNamedPages('search')

def getNamedBugs():
    """
    As above, but for Named Bugs instead of Saved Searches.
    """
    return _getNamedPages('namedBug')

def _loadNamedPage(ofType):
    args = os.environ['QUERY_STRING'].split('&')
    searchName = None
    searchUser = None
    searchFormat = None
    for arg in args:
        if not arg:
            break
        if not arg.find('=') >= 0:
            break
        key, val = [urllib.parse.unquote(elem) for elem in arg.split('=', 1)]
        if key == 'byname':
            searchName = val
        elif key == 'fromuser':
            searchUser = val
        elif key == 'format':
            searchFormat = val

    if searchName:
        name = ofType + searchName
        if searchUser:
            sprefs = loadPrefs(searchUser)
        else:
            sprefs = loadPrefs()

        if hasattr(sprefs, name):
            os.environ['QUERY_STRING'] = getattr(sprefs, name).split('?', 1)[1]
            if searchFormat:
                os.environ['QUERY_STRING'] = re.sub(r'\bformat=.+?(&.*|)$', r'format=%s\1' % searchFormat, os.environ['QUERY_STRING'])
        else:
            raise TiqitError("No %s called '%s' exists." % 
                              ("saved search" if ofType == "search" else "named bug", searchName))

    return searchName, searchUser

def loadSavedSearch():
    searchName, searchUser = _loadNamedPage('search')
    name = searchName
    while name != None:
        name, user = _loadNamedPage('search')
    return searchName, searchUser

def loadNamedBug():
    return _loadNamedPage('namedBug')

def _printNamedPages(ofType, introStr, path, saverStr, saveType, bugid=None):
    """
    Print a bar out for named pages of the given type.

    First argument is the preference prefix of the named page type;
    second is a string to prefix the line with (e.g. 'Saved
    Searches'); third is the path to forward to for a named page -
    this string is appended with the
    name of the page; the last argument is a string to prefix the
    'save as' box with - if this is False (or None, or the empty
    string) then no save box is presented, even if _getNamedPages()
    says one is required.
    """
    namedPages, needSave = _getNamedPages(ofType)
    searchName = _getSearchName(ofType)

    # Box needed if at least one named page, or the 'save as' box is required.
    if namedPages or (needSave and saverStr):
        print(printToolbarHeader(introStr, ofType, path, saveType))
        print("<span class='tiqitBarIntroStr' style='display: %s;'>%s: </span>" % (len(namedPages) > 0 and 'inline' or 'none', introStr))

    # Generate output worthy strings
    if namedPages:
        namedPages = ["<a id='tiqitBar%s%s' class='%s' href='%s%s' tiqitPrefValue='%s' tiqitViewing=%s>%s</a>" %
            (saveType, urllib.parse.quote(x), ofType, path, urllib.parse.quote(x), y, "1" if x==searchName else "0", encodeHTML(x)) for (x, y) in namedPages]

    # Add separators to the left of each item, hiding the first item's
    # separator.
    for i in range(len(namedPages)):
        visible = True
        if i == 0:
            visible = False
        namedPages[i] = ("<span style='display: inline;'><span class='tiqitBarSep' style='display: %s;'> | </span>%s</span>"
            % ("inline" if visible else "none", namedPages[i]))

    # Append a 'save as' box if required.
    if saverStr:
        if bugid:
            bugidParam = ", \"%s\"" % bugid
        else:
            bugidParam = ""

        namedPages.append("""<span style='display: %s;'><span
                class='tiqitBarSep' style='display: %s;'> | </span>
                <span id=\"tiqitBar%sSaver\">%s:
          <input type='text' size='20' id='saveName'>
          <input type='button' value='Save' onclick='saveSearch(this,
              \"%s\"%s);'></span></span>
          """ % ("inline" if needSave else "none",             # Sep and box display
                 "none" if len(namedPages) == 0 else "inline", # Separator display
                 saveType,                                     # Span ID
                 saverStr, saveType, bugidParam))

    # Print it all out.
    if namedPages:
        print("".join(namedPages))
        print(printToolbarFooter())

#
# News
#

news = None

def _printNewsBanner():
    """
    Loads latest news and queues up messages for any new news.
    """
    global news

    try:
        latest = os.stat(NEWS_PATH + 'latest').st_mtime
    except:
        latest = 0

    prefs = loadPrefs()
    lastseen = prefs["newsTimeStamp"]

    if lastseen < latest:
        if not news:
            fd = open(NEWS_PATH + 'latest', 'rb')
            try:
                news = pickle.load(fd)
            except:
                news = []
            fd.close()
        unread_news = [item for when, item in news if when > lastseen]
        unread_count = len(unread_news)

        if unread_count > 0:
            msg = unread_news[-1]

            if unread_count > 1:
                msg += " (%d more <a href='news'>unread item%s</a>)" % \
                           (unread_count - 1, "" if unread_count == 2 else "s")

            _printMsg(MSG_NEWS, msg, "tiqitNewsMessage",
                      tick=("tiqitNewsMarkRead(event)",
                            "Mark all unread news as read", "[Read]"))


#
# HTML Page Printing Functions
#

def getBasePath():
    if '?' in os.environ['REQUEST_URI']:
        path, query = os.environ['REQUEST_URI'].split('?', 1)
    else:
        path = os.environ['REQUEST_URI']

    if path.endswith(os.environ['PATH_INFO']):
        basepath = '%s/' % path[:-len(os.environ['PATH_INFO'])]
    else:
        basepath = '/./'

    return basepath

def getBaseHost():
    return 'https://%s%s' % (os.environ['HTTP_HOST'], getBasePath())

def printMainGoto():
    return """
      <form id='tiqitGoto' action='bugbox.py' method='get'>
        Go to Bug: <input id='tiqitGotoField' type='text' name='bugid' size='10' accesskey='s'> <input type='submit' name='goto' value='Go'>
      </form>"""

class SubSite(object):
    def __init__(self, titlefmt, appleiconurl, imgurl, imgtype, searchfunc):
        self.titlefmt = titlefmt
        self.appleiconurl = appleiconurl
        self.imgurl = imgurl
        self.imgtype = imgtype
        self.searchfunc = searchfunc

class PageLink(object):
    def __init__(self, target, img, tooltip, title):
        self.target = target
        self.img = img
        self.tooltip = tooltip
        self.title = title

class PageInfo(object):
    def __init__(self, links, scripts, styles, site):
        self.links = links
        self.scripts = scripts
        self.styles = styles
        self.site = site

SITE_MAIN = SubSite("%s", 'images/bug-apple.png', 'images/bug.png', 'image/png', printMainGoto)
SITE_META = SubSite("%s Metadata Database", 'images/registry-apple.png', 'images/registry-tiny.png', 'image/png', lambda: "")

PAGE_HOME    = 'index'
PAGE_NEW     = 'new'
PAGE_VIEW    = 'view'
PAGE_SEARCH  = 'search'
PAGE_RESULTS = 'results'
PAGE_PREFS   = 'prefs'
PAGE_NEWS    = 'news'
PAGE_HOMEMETA = 'homemeta'
PAGE_FIELDS   = 'fields'
PAGE_PROJECTS = 'projects'
PAGE_DEFVALS  = 'defvals'


# Links to each Tiqit page
LINK_HOME   = PageLink('', 'images/home-small.png', 'Return to %s home page' % Config().section('general').get('sitename'), 'Home')
LINK_NEW    = PageLink('newbug', 'images/debug_add-small.png', 'Submit a new bug', 'Submit')
LINK_SEARCH = PageLink('search', 'images/find-small.png', 'Perform a new search for bugs', 'Search')
LINK_PREFS  = PageLink('prefs', 'images/preferences-small.png', 'View and edit your preferences', 'Preferences')
LINK_NEWS   = PageLink('news', 'images/text_rich-medium.png', 'See news about recent %s developments' % Config().section('general').get('sitename'), 'News')
LINK_HOMEMETA = PageLink('homemeta', 'images/registry-small.png', 'Return to the %s home page' % Config().section('general').get('sitename'), 'Home')
LINK_MAIN = PageLink(Config().section('general').get('siteurl'), 'images/bug-medium.png', 'Return to %s' % Config().section('general').get('sitename'), Config().section('general').get('sitename'))
LINK_META = PageLink(Config().section('general').get('metaurl'), 'images/registry-small.png', 'Go to %s' % Config().section('general').get('metaname'), Config().section('general').get('metaname'))
LINK_FIELDS = PageLink('fields', 'images/registry-small.png', 'View field metadata', 'Fields')
LINK_PROJECTS = PageLink('projects', 'images/registry-small.png', 'View project metadata', 'Projects')
LINK_DEFVALS = PageLink('defaultvals', 'images/component-small.png', 'Default field values', 'Default Values')
LINK_INFO   = PageLink(Config().section('general').get('infourl'), 'images/unknown-small.png', 'Get information about %s, report bugs and request features' % Config().section('general').get('sitename'), 'Information')

pages = {
    PAGE_HOME:    PageInfo([LINK_NEW, LINK_SEARCH, LINK_PREFS, LINK_NEWS, LINK_META],
                           ['customevents', 'plugin', 'toolbar'], ['toolbar'], SITE_MAIN),
    PAGE_NEW:     PageInfo([LINK_HOME, LINK_SEARCH, LINK_PREFS, LINK_NEWS, LINK_META],
                           ['customevents', 'plugin', 'toolbar', 'fields', 'fielddata', 'defaults', 'view', 'userdropdown', 'calendar'],
                           ['toolbar', 'userdropdown', 'calendar'], SITE_MAIN),
    PAGE_VIEW:    PageInfo([LINK_HOME, LINK_NEW, LINK_SEARCH, LINK_PREFS, LINK_NEWS, LINK_META],
                           ['customevents', 'plugin', 'toolbar', 'fields', 'fielddata', 'defaults', 'view', 'tableactions', 'userdropdown', 'filter', 'static', 'calendar'],
                           ['toolbar', 'userdropdown', 'graphs', 'calendar'], SITE_MAIN),
    PAGE_SEARCH:  PageInfo([LINK_HOME, LINK_NEW, LINK_PREFS, LINK_NEWS, LINK_META],
                           ['customevents', 'plugin', 'toolbar', 'fields', 'fielddata', 'defaults', 'userdropdown', 'search', 'calendar', 'selectfield'],
                           ['toolbar', 'calendar', 'selectfield'], SITE_MAIN),
    PAGE_RESULTS: PageInfo([LINK_HOME, LINK_NEW, LINK_SEARCH, LINK_PREFS, LINK_NEWS, LINK_META],
                           ['customevents', 'plugin', 'toolbar', 'fields', 'fielddata', 'defaults', 'results', 'userdropdown', 'tableactions', 'filter', 'calendar', 'updateresults', 'fortune', 'multiedit', 'historydropdown', 'coledit', 'api'],
                           ['toolbar', 'userdropdown', 'calendar', 'fortune', 'tableactions', 'multiedit', 'historydropdown', 'coledit'], SITE_MAIN),
    PAGE_PREFS:   PageInfo([LINK_HOME, LINK_NEW, LINK_SEARCH, LINK_NEWS, LINK_META],
                           ['customevents', 'plugin', 'toolbar', 'fields', 'fielddata', 'search', 'prefs', 'selectfield'],
                           ['toolbar', 'selectfield'], SITE_MAIN),
    PAGE_NEWS:    PageInfo([LINK_HOME, LINK_NEW, LINK_SEARCH, LINK_PREFS, LINK_META],
                           ['customevents', 'plugin', 'toolbar', 'fields'],
                           ['toolbar'], SITE_MAIN),
    PAGE_HOMEMETA: PageInfo([LINK_DEFVALS, LINK_MAIN],
                            ['customevents', 'plugin'], ['meta'], SITE_META),
    PAGE_FIELDS:   PageInfo([LINK_HOMEMETA, LINK_PROJECTS, LINK_DEFVALS, LINK_MAIN],
                            ['customevents', 'plugin'], ['meta'], SITE_META),
    PAGE_PROJECTS: PageInfo([LINK_HOMEMETA, LINK_FIELDS, LINK_DEFVALS, LINK_MAIN],
                            ['customevents', 'plugin'], ['meta'], SITE_META),
    PAGE_DEFVALS:  PageInfo([LINK_HOMEMETA, LINK_MAIN],
                            ['customevents', 'plugin', 'fields', 'fielddata', 'userdropdown', 'defaults'],
                            ['meta', 'userdropdown'], SITE_META),
}

currentPage = None

def printPageHeader(pageName, pageTitle="", initScript=None, otherHeaders=[],
                    hideSavedSearches=False, hideNamedBugs=False,
                    showSavedSearchSaver=False, showNamedBugSaver=False, bugView=None,
                    bugid=None):
    """
    Print out the standard page headers.
    """
    global currentPage
    if currentPage:
        raise TiqitError("Already started printing a page: %s" % currentPage)
    currentPage = pageName

    timeMark("header")

    # Some prep
    prefs = loadPrefs()
    cfg = Config()

    if pageTitle:
        pageTitle += " - " + pages[pageName].site.titlefmt % cfg.section('general').get('sitetitle')
    else:
        pageTitle = pages[pageName].site.titlefmt % cfg.section('general').get('sitetitle')

    baseurl = getBaseHost()

    bodyClass = bugView and bugView.bodyClass or ''
    
    # Print the HTTP header, including any cookies.
    outgoingCookies = plugins.getOutgoingCookies()
    if outgoingCookies:
        for c in outgoingCookies:
            print(c)
    print("Set-Cookie: update=; Max-Age=0; path=%s" % getBasePath())
    print("Content-Type: text/html; charset=utf-8")
    print("""
<html>
  <head>
    <title>%s</title>
    <base href='%s'>
    <link rel='apple-touch-icon' href='%s'>
    <link rel='shortcut icon' type='%s' href='%s'>
    <link rel='stylesheet' type='text/css' href='styles/print.css?version=%s' media='print'>""" % (
            pageTitle,
            baseurl,
            pages[pageName].site.appleiconurl,
            pages[pageName].site.imgtype,
            pages[pageName].site.imgurl,
            VERSION_STRING,
        )
    )
    
    for head in otherHeaders:
        print(head)

    # Print styles
    print("<link rel='stylesheet' type='text/css' href='styles/tiqit.css?version=%s' media='screen'>" % VERSION_STRING)
    for style in pages[pageName].styles:
        print("<link rel='stylesheet' type='text/css' href='styles/%s.css?version=%s' media='screen'>" % (style, VERSION_STRING))

    # Plugins may want to add styles too
    for style in plugins.getPageStyles(pageName):
        print("<link rel='stylesheet' type='text/css' href='styles/%s.css?version=%s' media='screen'>" % (style, VERSION_STRING))

    # Print custom styles (overrides any other styles)
    cfg_section = Config().section('general')
    if 'customstyles' in cfg_section:
        for style in cfg_section.getlist('customstyles'):
            print(("<link rel='stylesheet' type='text/css' " + 
                   "href='%s?version=%s' media='screen'>") % (style, VERSION_STRING))

    print("<script type='text/javascript' src='scripts/tiqit.js?version=%s'></script>" % VERSION_STRING)
    print("<script type='text/javascript' src='scripts/Sortable.js?version=%s'></script>" % VERSION_STRING)
    
    for script in pages[pageName].scripts: 
        print("<script type='text/javascript' src='scripts/%s.js?version=%s'></script>" % (script, VERSION_STRING))

    # Plugins may want to add scripts too
    for script in plugins.getPageScripts(pageName):
        # The plugin may provide a version along with the script
        # in which case it is added to the tiqit version
        pluginVersion = ""
        if isinstance(script, tuple):
            script, plugin_version = script
        print("<script type='text/javascript' src='scripts/%s.js?version=%s+%s'></script>" % (
            script,
            VERSION_STRING,
            plugin_version
        ))

    if bugView:
        print("<link rel='stylesheet' type='text/css' href='styles/%s.css?version=%s' media='screen'>" % (bugView.name, VERSION_STRING))
        print("<script type='text/javascript' src='scripts/%s.js?version=%s'></script>" % (bugView.name, VERSION_STRING))

    print("""
    <script type='text/javascript'>
    <!--
    Tiqit.version = "%s";""" % VERSION_STRING)
    print("    tiqitUserID = '%s'" % encodeHTML(os.environ['REMOTE_USER']) + ";")
    print("""    Tiqit.prefs = new Object();""")

    # Print all the lovely preferences
    for p in prefs.defaults:
        if type(prefs[p]) in (str, str):
            print("    Tiqit.prefs['%s'] = '%s';" % (encodeHTML(p), encodeHTML(prefs[p])))
        elif type(prefs[p]) == list:
            print("    Tiqit.prefs['%s'] = new Array('%s');" % (encodeHTML(p), "','".join(map(encodeHTML, prefs[p]))))
        elif type(prefs[p]) == dict:
            # Don't include it, if dict prefs ever needed in JS, add this
            None
        else:
            raise ValueError("Don't support prefs of type %s" % type(prefs[p]))

    print("""    Tiqit.config = new Object();""")

    # Print the configuration
    for s in cfg.cfg.sections():
        print("    Tiqit.config['%s'] = new Object();" % encodeHTML(s))
        for o, v in cfg.cfg.items(s, raw=True):
            print("    Tiqit.config['%s']['%s'] = '%s';" % (encodeHTML(s), encodeHTML(o), encodeHTML(v.replace('\n', '\\n'))))

    # If the page requires an initialisation script, print it
    if initScript:
        print(initScript)
    else:
        print("    function init() { };")

    print("""    -->
    </script>
  </head>
  <body class='%s' onload='runInitOnce()'>
   <!-- Attempt to use Application Cache <iframe style='display: none' src='cache.py'></iframe>-->
   <div id='tiqitContainer'%s>
    <div id='tiqitHeader'>""" % (bodyClass,
                                 " class='tiqitWatermark'" if
                                 prefs.miscHideWatermark == 'false' else
                                 ""))

    # Now we're on the page proper. Print the relevant search box
    print(pages[pageName].site.searchfunc())

    # Print the list of links for this page
    print("<p>")
    links = pages[pageName].links + [LINK_INFO]
    if prefs.miscToolbar == 'icons':
        print(" | ".join(["<a href='%s' title='%s'><img src='%s' alt='%s'></a>" % (x.target, x.tooltip, x.img, x.title) for x in links]))
    elif prefs.miscToolbar == 'text':
        print(" | ".join(["<a href='%s' title='%s'>%s</a>" % (x.target, x.tooltip, x.title) for x in links]))
    else:
        print(" | ".join(["<a href='%s' title='%s'><img src='%s' alt='%s'>%s</a>" % (x.target, x.tooltip, x.img, x.title, x.title) for x in links]))

    print("""</p>
    </div>""")

    # Print Saved Searches and Named Bugs now
    if prefs.miscHideSavedSearches != 'on' and not hideSavedSearches:
        _printNamedPages('search', 'Saved Searches', 'results/%s/' % os.environ['REMOTE_USER'],
                         showSavedSearchSaver and 'Save Search as' or None,
                         "search")

    if prefs.miscHideNamedBugs != 'on' and not hideNamedBugs:
        _printNamedPages('namedBug', 'Named Bugs', 'view/',
                         showNamedBugSaver and 'Name this bug' or None,
                         "bug", bugid=bugid)

    print('\n'.join(plugins.printToolbars(pages[pageName])))

    print("<div id='tiqitContent'>")

def printPageFooter():
    """
    Close anything that was opened in printPageHeader().
    """
    sys.stdout.flush()
    now = time.time()

    versions = ['TiQiT version %s' % VERSION_STRING]
    versions.extend(plugins.printVersion(currentPage))
    footerText = ' '.join(plugins.printFooterText())
    print("""
    </div>
    <div id='tiqitFooter'>
     <p>%s. Generated in %.2fs. %s</p>
    </div>""" % ('. '.join(versions),
                 now - times[0][1],
                 footerText))

    times.append(("end", now))
    print("<!--")
    for i in range(1, len(times)):
        print(times[i][0], times[i][1] - times[i - 1][1])
    print("""-->
    <!--
    Plugins installed:""")
    for i in plugins._plugins:
        vers = hasattr(i.module, 'VERSION') and i.module.VERSION or (1, 0)
        print(i.module.__name__, vers)
    print("""-->
   </div>
  </body>
</html>""")

def printSectionHeader(name, displayName=None, hide=False):
    """
    Print a section headers. Sections can be shown/hidden using the
    provided buttons, but only if they are enabled in the init
    function for the page. Sections show/hiding is enabled by calling
    [show|hide]Section(name); in your init() script.
    """
    if not displayName:
        displayName = name
    print("""
  <div id='tiqitSection%(name)s'%(hide)s>
    <h3>
     <span style='float:right;'>
      <input id='show%(name)sButton' type='button' onclick='showSection("%(name)s");' value='Show'>
      <input id='hide%(name)sButton' type='button' onclick='hideSection("%(name)s");' value='Hide'>
     </span>
     <a name='anchor%(name)s'>%(displayName)s</a>
    </h3>
    <div id='tiqitSectionContents%(name)s'>
    """ % {'name': name, 'displayName': displayName,
           'hide': hide and " style='display: none;'" or ''})

def printSectionFooter():
    """
    Close anything opened in printSectionHeader()
    """
    print("""
    </div>
  </div>""")

#
# Error handling
#

class TiqitException(Exception):
    def __init__(self, type, msg='', output='', cmd=''):
        Exception.__init__(self)
        self.type = type
        self.msg = msg
        if len(output) > 3000:
            self.output = output[:3000] + \
                "...(truncated)', which is longer than allowed length"
        else:
            self.output = output
        if len(cmd) > 3000:
            self.cmd = cmd[:3000] + "...(truncated)'" 
        else:
            self.cmd = cmd

class TiqitError(TiqitException):
    def __init__(self, msg='', output='', cmd=''):
        TiqitException.__init__(self, MSG_ERROR, msg, output, cmd)

class TiqitInfo(TiqitException):
    def __init__(self, msg=''):
        TiqitException.__init__(self, MSG_INFO, msg)

class TiqitWarning(TiqitException):
    def __init__(self, msg=''):
        TiqitException.__init__(self, MSG_WARNING, msg)

def errorHandler(exType, val, tb):
    """
    Handles expected error (subclasses of TiqitException) by redirecting to
    the error page with all the information. All other exception fall back to
    default cgitb handling.

    TBD: maybe add some 'this is an unexpected error' text.
    """
    if exType in (TiqitError, TiqitWarning, TiqitInfo):
        try:
            redirect("error?type=%d&msg=%s&cmd=%s&output=%s" \
                     % (val.type, urllib.parse.quote(val.msg.encode('utf-8')),
                        urllib.parse.quote(val.cmd.encode('utf-8')),
                        urllib.parse.quote(val.output.encode('utf-8'))))
        except:
            print("""Content-Type: text/plain

            Weirdness! Something seriously bad has happened.
            '%s'
            '%s'
            '%s'""" % (val.msg, val.cmd, val.output))
    else:
        tbhandler(exType, val, tb)

tbhandler = sys.excepthook
sys.excepthook = errorHandler

#
# Redirection
#

def redirect(location, code=303):
    newpath = '%s%s' % (getBasePath(), location.strip())
    print("Status: %d" % code)
    print("Location: %s" % newpath)
    for t, m in msgQueue:
        print("Set-Cookie: update=%s; path=%s" % \
              (urllib.parse.quote("%s %s" % (msgIcons[t][0], m)), getBasePath()))
    print()
    print("<a href='%s'>%s</a>" % (newpath, newpath))
    sys.exit()

#
# Time
#

def timeMark(reason):
    times.append((reason, time.time()))
