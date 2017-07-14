#

from tiqit import *
from utils import *
import backend

__all__ = [
    'clearDefaults',
    'fetchDefaults',
    'fetchReverseDefaults',
    'getDict',
    'iterDefaults',
    'loadDefaultsFromBackend',
    'saveDefaults',
    'saveManyDefaults',
]

def _encodeValue(field, data):
    vals = []
    for key in field.defaultsWith:
        vals.append(data[key])
    return '&'.join(map(encodeHTML, vals))

def _decodeValue(field, value):
    return dict(zip(field.defaultsWith, map(decodeHTML, value.split('&'))))

def fetchDefaults(field, data, useDatabase=True, preCache=False):
    value = _encodeValue(field, data)
    defs = {}

    if useDatabase:
        cu = database.cursor()
        cu.execute('SELECT defaultField, defaultValue FROM [tiqit#defaults] WHERE field = ? AND value = ?', (field.name, value))

        for f, val in cu.fetchall():
            defs[f] = val
        cu.close()

    if not defs:
        # Let's see if a plugin can find the defaults for us
        defs = plugins.getDefaults(field, data, preCache=preCache)

        # Now save any defaults we've been given
        if defs:
            saveDefaults(field, data, defs)
        else:
           defs = {}

    return defs


def clearDefaults():
    """
    Clear all entries from the defaults database.

    """

    cu = database.cursor()
    cu.execute('DELETE FROM [tiqit#defaults]')
    cu.close()

def loadDefaultsFromBackend():
    """
    Update the database with authoritative data from the backend.

    """
    plugins.loadDefaultsFromBackend()

def iterDefaults(field, defaultField):
    """
    Generator for defaults in the DB.

    field: Name of field which when changed will trigger `defaultField` to
           change.
    defaultField: Name of field which is changed when field is changed.

    Yields: `(values, defaultValue)`. `values` are the values for the
            `defaultsWith` fields of `field`. `defaultValue` is the
            corresponding value that `defaultField` is set to.

    """
    cu = database.cursor()
    cu.execute('SELECT value, defaultValue FROM [tiqit#defaults] WHERE field '
               '= ? AND defaultField = ?', (field, defaultField))

    for values, defaultValue in cu.fetchall():
        values = _decodeValue(backend.allFields[field], values)
        yield values, {defaultField: defaultValue}

    cu.close()

def getDict():
    """
    Return a dictionary containing all the default value information.

    """
    cu = database.cursor()
    cu.execute('SELECT field, value, defaultField, defaultValue FROM '
            '[tiqit#defaults]')

    d = {}
    for field, values, defaultField, defaultValue in cu.fetchall():
        values = _decodeValue(backend.allFields[field], values)
        values = tuple(values[k] for k in
                backend.allFields[field].defaultsWith)

        d[(field, values, defaultField)] = defaultValue

    cu.close()

    return d


def _saveDefaultsInternal(field, data, defs, cu):
    """
    Save default mappings into the database, with an already open cursor.

    field: Field whose default values are being saved.
    data: Mapping from elements of field.defaultsWith to values that trigger
          these defaults.
    defs: Mapping of default values set by the above data.
    cu: Database cursor.

    """

    value = _encodeValue(field, data)

    # First throw out any defs that are already in the DB (or aren't in the DB
    # fo delete operations).
    newdefs = dict((k, v) for k, v in defs.iteritems() if v)
    for key, val in defs.items():
        cu.execute('SELECT defaultField, defaultValue FROM [tiqit#defaults] WHERE field = ? AND value = ? AND defaultField = ? AND defaultValue = ?', (field.name, value, key, val))
        rowcount = len(cu.fetchall())
        if rowcount > 0:
            assert rowcount == 1
            if val:
                del newdefs[key]
            else:
                newdefs[key] = val
    defs = newdefs
                
    # Do the update.
    for key, val in defs.items():
        if val:
            cu.execute("INSERT INTO [tiqit#defaults] (field, value, defaultField, defaultValue) SELECT ?, ?, ?, ? WHERE ? NOT IN (SELECT field FROM [tiqit#defaults] WHERE field = ? AND value = ? AND defaultField = ?)", (field.name, value, key, val, field.name, field.name, value, key))
            cu.execute('UPDATE [tiqit#defaults] SET field = ?, value = ?, defaultField = ?, defaultValue = ? WHERE field = ? AND value = ? AND defaultField = ?', (field.name, value, key, val, field.name, value, key))
        else:
            cu.execute('DELETE FROM [tiqit#defaults] WHERE field = ? AND value = ? AND defaultField = ?', (field.name, value, key))

    queueMessage(MSG_INFO, "Successfully updated defaults for %s." % (", ".join(map(": ".join, [(x, data[x]) for x in field.defaultsWith]))))

    # Let plugins know
    plugins.defaultsSaved(field, data, defs)

    queueMessage(MSG_INFO, "Successfully updated defaults for %s." % (", ".join(map(": ".join, [(x, data[x]) for x in field.defaultsWith]))))

def saveManyDefaults(it):
    """
    Save default mappings into the database.

    it: Iterable of (field, data, defs) pairs:
        field: Field whose default values are being saved.
        data: Mapping from elements of field.defaultsWith to values that trigger
              these defaults.
        defs: Mapping of default values set by the above data.

    """

    cu = database.cursor()

    for field, data, defs in it:
        _saveDefaultsInternal(field, data, defs, cu)

    database.commit()
    cu.close()

def saveDefaults(field, data, defs):
    """
    Save default mappings into the database.

    field: Field whose default values are being saved.
    data: Mapping from elements of field.defaultsWith to values that trigger
          these defaults.
    defs: Mapping of default values set by the above data.

    """
    saveManyDefaults(((field, data, defs),))

def fetchReverseDefaults(field, value):
    revs = {}
    cu = database.cursor()
    cu.execute("SELECT field, value FROM [tiqit#defaults] WHERE defaultField = ? AND defaultValue = ?", (field.name, value))

    for f, v in cu.fetchall():
        revs.setdefault(f, []).append(_decodeValue(backend.allFields[f], v))
    cu.close()

    return revs
