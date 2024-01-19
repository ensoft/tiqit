#
# Module for parsing Cookies, and printing Set-cookie lines
#
import http.cookies

#
# Parse a HTTP_COOKIE environment variable into a dict mapping cookie keys to values
#
# Unlike the built-in Cookie module, this class attempts to parse the kinds of
# cookies seen "in the wild", rather than strictly conforming to RFC-2109 and
# RFC-2068.
#
def parseCookie(cookie_string):
    cookie_string_in = cookie_string

    # Cookies are split on semi-colons.
    # We're only interested in cookies with keys and values, anything without
    # an equals is invalid although they do occur (for example "secure;" is
    # sometimes set in the string).
    valid_cookies = [c.strip()
                     for c in cookie_string.split(";")
                     if "=" in c]

    return dict([c.split("=", 1) for c in valid_cookies])

#
# Take a dict of key value pairs, and generate a series of "Set-Cookie:" headers.
# 
# Keys and values must conform to RFC 2109 and RFC 2068
#
def getSetCookie(cookie):
    return http.cookies.SimpleCookie(cookie).output()
    
