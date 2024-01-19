#!/usr/bin/python3
#
# Generate the JS containing all the fields and stuff
#

# Load plugins very early on!
from tiqit import loadPlugins, initialise
import backend
import utils

def genHeader(out):
    out.write("""//
// This file is autogenerated using the generatejs.py script. Do not modify by hand.
//

//
// Note types
//
noteTypes = new Array("%s");

(function() {
var T = TiqitField;
var F = allFields;
var M, P, B, I;
""" % '",\n  "'.join(backend.noteTypes))

class Intern(object):
   def __init__(self):
       alph = "abcdefghijklmnopqrstuvwxyz"
       alph += alph.upper()
       self.keys = list(alph)
       self.keys.extend(x + y for x in alph for y in alph)
       #self.keys.extend(x + y + z for x in alph for y in alph for z in alph)
       for dis in ["if", "in", "do", "T", "F", "M", "P", "B", "I"]:
           self.keys.remove(dis)
       self.keys.reverse()
       self.interns = {}
       self.counts = {}
   def intern(self):
       prio = [(v, k) for k, v in self.counts.items()]
       prio.sort(reverse=True)
       print(prio[:26])
       saved = 0
       print("Writing interning information to 'interning.dat'...")
       with open('interning.dat', 'a') as file:
          for v, key in prio:
              self.interns[key] = self.keys.pop()
              saved += v
              file.write("Interning {} saving {} characters\n".format(key, v))
              if not self.keys:
                  break
       print("Failed to optimise", len(prio) - len(self.interns), "strings")
       print("But saved", saved, "characters")

   def count(self, key):
       self.counts.setdefault(key, 0)
       self.counts[key] += (len(key) - 1)
   def __getitem__(self, key):
       return self.interns.get(key, key)

I = Intern()

def makeInterns(out):
    for f in backend.allFields.values():
        I.count(utils.encodeJS(f.name))
        I.count(utils.encodeJS(f.shortname))
        I.count(utils.encodeJS(f.longname))
        I.count(utils.encodeJS(f.type))
        I.count("%d" % f.maxlen)
        I.count("%d" % f.displaylen)
        I.count(f.req and 'true' or 'false')
        I.count(f.mvf and 'true' or 'false')
        I.count(f.searchable and 'true' or 'false')
        I.count(f.editable and 'true' or 'false')
        I.count(f.viewable and 'true' or 'false')
        I.count(f.filterable and 'true' or 'false')
        I.count(f.volatile and 'true' or 'false')

        if f.values:
            for v in f.values:
                I.count(utils.encodeJS(v))
            if f.values != f.descs:
                for x in ("%s - %s" % (v,d) if v else v for v,d in zip(f.values, f.descs)):
                    I.count(utils.encodeJS(x))
            else:
                for d in f.descs:
                    I.count(utils.encodeJS(d))
        elif f._perParentFieldValues:
            for key in f._perParentFieldValues:
                for k in key:
                    I.count(utils.encodeJS(k))
                for v in f._perParentFieldValues[key]:
                    I.count(utils.encodeJS(v))
                if f._perParentFieldDescs:
                    for x in ("%s - %s" % (v,d) if v else v for v,d in zip(f._perParentFieldValues[key], f._perParentFieldDescs[key])):
                        I.count(utils.encodeJS(x))

        if f._parentFields:
            for i in f._parentFields:
                I.count(utils.encodeJS(i))
        if f._childFields:
            for i in f._childFields:
                I.count(utils.encodeJS(i))
        if f.defaultsWith:
            for i in f.defaultsWith:
                I.count(utils.encodeJS(i))
        if f.defaultsFor:
            for i in f.defaultsFor:
                I.count(utils.encodeJS(i))
        if f._mandatoryIf:
            for k, v in f._mandatoryIf.items():
                I.count(utils.encodeJS(k))
                for i in v:
                    I.count(utils.encodeJS(i))
        if f._bannedIf:
            for k, v in f._bannedIf.items():
                I.count(utils.encodeJS(k))
                for i in v:
                    I.count(utils.encodeJS(i))
        if f.searchrels:
            for r in f.searchrels:
                I.count(r)
        if f.searchvals:
            for v in f.searchvals:
                for i in v:
                    I.count(utils.encodeJS(i))

    I.intern()
    for k, v in I.interns.items():
        out.write("const %s=%s;\n" % (v, k))
    out.write("\n")

def encodeJS(arg):
    return I[utils.encodeJS(arg)]

def JSListFromSequence(arg):
    return "[%s]" % ",".join(I[utils.encodeJS(x)] for x in arg)

def JSListOfListsFromSequence(arg):
    return "[%s]" % ",".join(map(JSListFromSequence, arg))

def genFieldLists(out):
    for f in backend.allFields.values():
        # Need to create the values if this has limited values
        out.write("""new T(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);\n""" % (encodeJS(f.name), encodeJS(f.shortname), encodeJS(f.longname), encodeJS(f.type), I[str(f.maxlen)], I[str(f.displaylen)], I[f.req and 'true' or 'false'], I[f.mvf and 'true' or 'false'], I[f.searchable and 'true' or 'false'], I[f.editable and 'true' or 'false'], I[f.viewable and 'true' or 'false'], I[f.filterable and 'true' or 'false'], I[f.volatile and 'true' or 'false']))
    out.write("""allEditableFields.sort();\n""");
    out.write("""allSearchableFields.sort();\n""");
    out.write("""allViewableFields.sort();\n""");

def genRelationships(out):
    # Calculate reverseDefaultsWith first.
    reverseDefaultsWith = {}
    for f in backend.allFields.values():
        for f2name in f.defaultsWith:
            reverseDefaultsWith.setdefault(f2name, set()).add(f.name)

    # Only generates rels and vals for ones with multiple options
    for f in backend.allFields.values():
        out.write("I=F[%s];\n" % encodeJS(f.name))
        rewriterels = False
        def getOptions(values, descs):
            return ("%s - %s" % (v,d) if v else v for v,d in zip(values,descs))
        if f.values:
            if f.descs != f.values:
                vals = [list(item) for item in zip(f.values, getOptions(f.values, f.descs))]
            else:
                vals = [list(item) for item in zip(f.values, f.descs)]
            out.write("""I.values=%s;\n""" % JSListOfListsFromSequence(vals))
            rewriterels = True
        elif f._perParentFieldValues:
            out.write("P=I.perparentvalues;\n")
            for key in f._perParentFieldValues:
                if f._perParentFieldDescs:
                    vals = [list(item) for item in zip(f._perParentFieldValues[key], getOptions(f._perParentFieldValues[key], f._perParentFieldDescs[key]))]
                else:
                    vals = [list(item) for item in zip(f._perParentFieldValues[key], f._perParentFieldValues[key])]
                out.write("""P[%s]=%s;\n""" % (JSListFromSequence(key), JSListOfListsFromSequence(vals)))
                rewriterels = True

        parent_list = []
        if f._parentFields:
            out.write("""I.parentfields=%s;\n""" % JSListFromSequence(f._parentFields))
        if f._childFields:
            out.write("""I.childfields=%s;\n""" % JSListFromSequence(f._childFields))
        if f.defaultsWith:
            out.write("""I.defaultsWith=%s;\n""" % JSListFromSequence(f.defaultsWith))
        if f.defaultsFor:
            out.write("""I.defaultsFor=%s;\n""" % JSListFromSequence(f.defaultsFor))
        if f.name in reverseDefaultsWith:
            out.write("""I.reverseDefaultsWith=%s;\n""" % JSListFromSequence(reverseDefaultsWith[f.name]))
        if f._mandatoryIf:
            out.write("M=I.mandatoryif;\n")
        for key in f._mandatoryIf:
            out.write("""M[%s]=%s;\n""" % (encodeJS(key), JSListFromSequence(f._mandatoryIf[key])))
        if f._bannedIf:
            out.write("B=I.bannedif;\n")
        for key in f._bannedIf:
            out.write("""B[%s]=%s;\n""" % (encodeJS(key), JSListFromSequence(f._bannedIf[key])))

        # Some of them have their own rels
        if f.searchrels:
            out.write("""I.rels=%s;\n""" % f.searchrels)
        elif rewriterels and f.type != "Number":
            out.write("""I.rels=relSelect;\n""")

        if f.searchvals:
            out.write("""I.searchvals=%s;\n""" % JSListOfListsFromSequence(f.searchvals))
        else:
            out.write("""I.searchvals=I.values;\n""")

def genFooter(out):
    out.write("})();\n");

def genEverything():
    initialise()
    file = open('../static/scripts/fielddata.js', 'w')
    genHeader(file)
    makeInterns(file)
    genFieldLists(file)
    genRelationships(file)
    genFooter(file)
    file.close()

if __name__ == "__main__":
    genEverything()
