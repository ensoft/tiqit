#! /usr/bin/python3

import sys, pickle, os, getopt

def usage():
    print("""Usage: convert.py -f <from> -t <to> [-p <profiles>]
  -f  Tiqit scripts dir where profiles are being copied from
  -t  Tiqit scripts dir where profiles are being copied to
  -p  Profile storage directory. By defaults, this is ../profiles relative to
      the 'from' directory
  -v  Tell us about the files being copied
  Profiles are always copied to ../profiles relative to the 'to' directory.""")

def readArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:t:p:v", ["help", "from=", "to=", "profiles="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    profiledir = None
    fromdir = None
    todir = None
    verbose = False
    for o, a in opts:
        if o in ("-f", "--from"):
            fromdir = a
        elif o in ("-t", "--to"):
            todir = a
        elif o in ("-p", "--profile"):
            profiledir = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "-v":
            verbose = True
        else:
            assert False, "unhandled option"

    if not fromdir or not todir:
        print("Must specify -f and -t")
        usage()
        sys.exit(3)

    if not profiledir:
        profiledir = os.path.join(fromdir, '..', 'profiles')

    return fromdir, todir, profiledir, verbose

fromdir, todir, profiledir, verbose = readArgs()

sys.path.append(fromdir)

oldPrefs = {}

for f in os.listdir(profiledir):
  if verbose:
      print("Loading profile for", f)
  fd = open(os.path.join(profiledir, f), 'rb')
  oldPrefs[f] = pickle.load(fd)
  fd.close()

sys.path[-1] = todir

from tiqit import Prefs

newPrefs = {}

for p in oldPrefs:
  print("Copying profile for", p)
  newP = Prefs()

  for v in dict.keys(oldPrefs[p]):
    newP[v] = oldPrefs[p][v]
  fd = open(os.path.join(todir, '..', 'profiles', p), 'wb')
  pickle.dump(newP, fd)
  fd.close()

