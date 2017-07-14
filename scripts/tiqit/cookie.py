#
# Module for parsing Cookies, and printing Set-cookie lines
#
import re, Cookie

#
# Parse a HTTP_COOKIE environment variable into a dict mapping cookie keys to values
#
# Unlike the built-in Cookie module, this class attempts to parse the kinds of
# cookies seen "in the wild", rather than strictly conforming to RFC-2109 and
# RFC-2068.
#
def parseCookie(cookie_string):
    cookie_string_in = cookie_string

    # Split into an array of key-value pair strings. Cope with last element
    # being terminated with a semi-colon.
    pairs = re.split("; *", cookie_string)
    if re.match("^ *$" , pairs[-1]):
        pairs = pairs[:-1]

    # Split each string into a individual key and value, and return as an array.
    return dict(map(lambda x: x.split("=", 1), pairs))

#
# Take a dict of key value pairs, and generate a series of "Set-Cookie:" headers.
# 
# Keys and values must conform to RFC 2109 and RFC 2068
#
def getSetCookie(cookie):
    return Cookie.SimpleCookie(cookie).output()
    
