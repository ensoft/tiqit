#
# Implement an AWESOME database using Pickle
#

import random
import cPickle as pickle
import os.path
from tiqit import *
from backend import *

BASE = os.path.join(DATA_PATH, 'pickle')

class PickledBugData(DataCommon):
    def __init__(self, vals):
        self.vals = vals
        self.history = []
        self.attachments = []

    def __setitem__(self, key, val):
        self.vals[key] = val

    def _getRawValue(self, key):
        return self.vals[key]

    def getHistory(self):
        # returns dicts with 'Date', 'Operation', 'NewValue', 'OldValue',
        # 'Field', 'User', 'DateVal'
        return []

    def getEnclosures(self):
        # returns dicts with 'Date', 'Creator', 'Updater', 'Type', 'Size',
        # 'Note', 'Title', 'Identifier'
        return []

    def getAttachments(self):
        # returns dicts with 'Date', 'Creator', 'Updater', 'Type', 'Size',
        # 'Name', 'Ext', 'Title', 'Identifier', 'LinkName'
        return []

    def getRelates(self):
        # returns (bugid, relationship, editable) tuples
        return []

#
# Getters
#

# Return some bug data for a list of bug-ids.
def loadBugs(bugids):
    results = []
    for bid in bugids:
        try:
            with open(os.path.join(BASE, bid), 'rb') as fd:
                results.append(pickle.load(fd))
        except Exception, e:
            raise TiqitException("Failed to load bug %s: %s" % (bid, str(e)))

    return results

#
# The updating stuff
#

def numToId(num):
    number = num % 100000
    let2 = chr(ord('a') + (num / 100000) % 26)
    let1 = chr(ord('a') + (num / 100000 / 26) % 26)
    assert num / 100000 / 26 / 26 == 0, "That number is out of range"
    return "%s%s%05u" % (let1, let2, number)

def genId(prefix):
    return prefix + numToId(random.randint(0, 100000 * 26 * 26 - 1))

def createBug(fields):
    data = PickledBugData(fields)

    prefix = fields['Project'][:3]
    newid = genId(prefix)
    while not os.path.exists(os.path.join(BASE, newid)):
        fd = open(os.path.join(BASE, newid), 'wb')

    data['Identifier'] = newid
    pickle.dump(data, fd)
    fd.close()

def updateBug(bugid, changes):
    assert 'Identifier' not in changes, "Can't change the ID of a bug"
    with open(os.path.join(BASE, bugid), 'rb') as fd:
        data = pickle.load(fd)
    data.vals.update(changes)
    with open(os.path.join(BASE, bugid), 'wb') as fd:
        pickle.dump(data, fd)

def addNote(bugid, noteType, noteTitle, noteContent, isUpdate=False):
    raise TiqitError("Sorry. You can't add notes to this bug.")

def deleteNote(bugid, noteTitle):
    raise TiqitError("Sorry. You can't delete notes from this bug.")

def renameNote(bugid, noteType, noteTitle, newTitle):
    raise TiqitError("Sorry. You can't rename notes on this bug.")

def addAttachment(bugid, fileTitle, filename):
    raise TiqitError("Sorry. You can't add attachments to this bug.")

def deleteAttachment(bugid, fileTitle):
    raise TiqitError("Sorry. You can't delete attachments from this bug.")

def renameAttachment(bugid, fileTitle, newTitle):
    raise TiqitError("Sorry. You can't rename attachments on this bug.")

def attachmentUrl(info):
    raise TiqitError("Sorry. What on earth have you done?!")

#
# Queries
#

def performQuery(query, fields, sortFields, states, project, buglist, debug):
    # Can't be arsed to implement search. Return everything!
    results = []
    for bid in os.listdir(BASE):
        with open(os.path.join(BASE, bid), 'rb') as fd:
            results.append(pickle.load(fd))

    return results

