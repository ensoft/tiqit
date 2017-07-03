#
# generate an authentication token for the CLI
#

from tiqit import generateToken
from random import choice
import os

# generate a token and return it

def tokenPage():
    cookie = generateToken()

    print """Content-Type: text/plain

%s""" % cookie

tokenPage()
