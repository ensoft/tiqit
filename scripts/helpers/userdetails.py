#!/usr/bin/python3

from tiqit import *
from tiqit.printing import *
import ldap

cfg = Config().section('userdetails')
args = Arguments()

name = 'unknown'
num = 0

if 'name' in args:
    name = args['name']
if 'num' in args:
    num = int(args['num'])

props = ['uname', 'unum', 'cname', 'title', 'company', 'dept', 'phone', 'phone2', 'manager']
mapnames = dict([(x, cfg.get('ldap_' + x)) for x in props])

# Is this the escape needed for the LDAP module?
name = name.replace("'", r"'\''")

base = cfg.get('ldap_base')
results = list(mapnames.values())
scope = ldap.SCOPE_SUBTREE

query = num and '%s=%d' % (mapnames['unum'], num) or '%s=%s' % (mapnames['uname'], name)

l = ldap.open(cfg.get('ldap_server'))
r = l.search(base, scope, query, results)

info = dict(list(zip(props, (name, num, 'Unknown', 'Unknown', '', '', '', '', 0))))
rtype, rdata = l.result(r, 0)
if rtype == ldap.RES_SEARCH_ENTRY:
    for cn, res in rdata:
        info = dict([(x, mapnames[x] in res and res[mapnames[x]][0] or '') for x in props])

if 'phone2' in info and not info['phone']:
    info['phone'] = info['phone2']

printXMLPageHeader()
printXMLSectionHeader("userdetails")

for key, val in list(info.items()):
    print("    <%s><![CDATA[%s]]></%s>" % (key, encodeCDATA(str(val)), key))

printXMLSectionFooter("userdetails")
printXMLPageFooter()
