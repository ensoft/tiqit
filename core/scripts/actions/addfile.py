#! /usr/bin/python

import os
from tiqit import *
from backend import *

args = Arguments()

# Get a temporary file to put the attachment into
filename = args.writeToTempFile('theFile')

try:
    addAttachment(args['bugid'], args['fileTitle'], filename)

    redirect("%s" % args['bugid'])
finally:
    #
    # In any case, delete the file!
    #
    os.unlink(filename)
