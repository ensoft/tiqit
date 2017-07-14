#!/usr/bin/python

from tiqit import *
from tiqit.printing import *
import ldap

cfg = Config().section('userdetails')
args = Arguments()

name = 'unknown'
num = 0

if args.has_key('name'):
    name = args['name']
if args.has_key('num'):
    num = int(args['num'])

props = ['uname', 'unum', 'cname', 'title', 'company', 'dept', 'phone', 'phone2', 'manager']
mapnames = dict([(x, cfg.get('ldap_' + x)) for x in props])

# Is this the escape needed for the LDAP module?
name = name.replace("'", r"'\''")

base = cfg.get('ldap_base')
results = mapnames.values()
scope = ldap.SCOPE_SUBTREE

query = num and '%s=%d' % (mapnames['unum'], num) or '%s=%s' % (mapnames['uname'], name)

l = ldap.open(cfg.get('ldap_server'))
r = l.search(base, scope, query, results)

info = dict(zip(props, (name, num, 'Unknown', 'Unknown', '', '', '', '', 0)))
rtype, rdata = l.result(r, 0)
if rtype == ldap.RES_SEARCH_ENTRY:
    for cn, res in rdata:
        info = dict([(x, res.has_key(mapnames[x]) and res[mapnames[x]][0] or '') for x in props])

if info.has_key('phone2') and not info['phone']:
    info['phone'] = info['phone2']

printXMLPageHeader()
printXMLSectionHeader("userdetails")

for key, val in info.items():
    print "    <%s><![CDATA[%s]]></%s>" % (key, encodeCDATA(str(val)), key)

printXMLSectionFooter("userdetails")
printXMLPageFooter()
