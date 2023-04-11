import getpass
import json
import os
import pprint
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from configparser import ConfigParser

datadir = None
tokenfile = None
conffile = None
config = None


def initialise(default_siteurl, datadir_l, conffile_l=None, tokenfile_l=None):
    global datadir
    global tokenfile
    global conffile
    global config

    datadir = os.path.join(os.path.expanduser("~"), datadir_l)
    tokenfile = os.path.join(datadir, "token")
    conffile = os.path.join(datadir, "config")

    cp = ConfigParser({"siteurl": default_siteurl})
    if conffile_l is None:
        conffile_l = conffile
    cp.read(conffile_l)
    config = cp

    if tokenfile_l:
        tokenfile = tokenfile_l


def get_token():
    if not os.path.exists(tokenfile):

        class AuthTokenOpener(urllib.request.FancyURLopener):
            def prompt_user_passwd(self, host, realm):
                return getpass.getuser(), getpass.getpass()

        url = AuthTokenOpener()
        doc = url.open(config.get("DEFAULT", "siteurl") + "authtoken")
        token = doc.read()
        doc.close()
        url.close()

        if not os.path.exists(datadir):
            os.makedirs(datadir)
        os.chmod(datadir, 0o700)
        fd = open(tokenfile, "w")
        fd.write(token)
        fd.close()
        os.chmod(tokenfile, 0o600)

    # Check the file is safe
    # ... later

    fd = open(tokenfile, "r")
    token = fd.read().strip()
    fd.close()

    return token


def request_page(page):
    token = get_token()

    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(
        realm="Tiqit API",
        uri=config.get("DEFAULT", "siteurl"),
        user="tiqit-api",
        passwd="tiqit-api",
    )
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)

    # If 'page' already contains a query string we append ours to the existing
    # one; otherwise we append a new one.
    if len(urllib.parse.urlparse(page).query) == 0:
        separator = "?"
    else:
        separator = "&"

    req = urllib.request.Request(
        config.get("DEFAULT", "siteurl") + page + separator + "format=json"
    )
    if token is not None:
        req.add_header("X-Tiqit-Token", token)
    doc = urllib.request.urlopen(req)
    data = doc.read().strip()
    doc.close()

    # Convert JSON to Python
    data = json.loads(data)

    return data


def request_named_query(user, query):
    """
    Request the results of a named query for a specific username.
    """
    data = request_page(
        "api/results/{}/{}".format(
            urllib.request.quote(user), urllib.request.quote(query)
        )
    )
    return data


def request_specific_bugs(bugs, fields):
    """
    Fetch data for a named set of one or more bugs.

    The fields to fetch must also be specified.
    """
    if bugs is None or fields is None:
        print("Must specify at least 1 bug and 1 field")
        return None

    page = "api/results?sort1=Identifier&sortOrder1=ASC&selection1=Identifier"
    if fields is not None:
        for i in range(len(fields)):
            idx = i + 2
            page = page + "&selection{}={}".format(idx, urllib.request.quote(fields[i]))

    page = page + "&buglist=" + ",".join(urllib.request.quote(bug) for bug in bugs)
    data = request_page(page)

    return data


def parse_args(siteurl):
    # Create the top-level parser
    commands = ["meta", "submit", "view", "search", "get"]
    parser = ArgumentParser(description="TiQiT command line interface")
    parser.add_argument("--conffile", "-f")
    parser.add_argument("--siteurl", "-s", default=siteurl)
    parser.add_argument("--user", "-u", default=getpass.getuser())
    subparsers = parser.add_subparsers(dest="subparser_name", help="Choose sub-command")

    # Create the parser for the "search" command
    parser_search = subparsers.add_parser("search", help="Run a named query")
    parser_search.add_argument("--query", "-q", help="Name of query to run")

    # Create the parser for the "get" command
    parser_get = subparsers.add_parser("get", help="Get specific bugs")
    parser_get.add_argument("--bugs", "-b", nargs="+", help="IDs of bugs to fetch")
    parser_get.add_argument("--fields", nargs="+", help="Fields to fetch")

    return parser.parse_args()


def process_cli_args(args):
    pp = pprint.PrettyPrinter(indent=4)
    print("")
    if args.subparser_name == "search":
        assert args.user is not None
        data = request_named_query(args.user, args.query)
        if data is None or len(data) == 0:
            print("No results found")
        else:
            pp.pprint(data)
    elif args.subparser_name == "get":
        data = request_specific_bugs(args.bugs, args.fields)

        if data is None or len(data) == 0:
            print("No results found")
        else:
            pp.pprint(data)
    else:
        print("Nothing to do")
