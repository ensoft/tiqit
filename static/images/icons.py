#!/usr/bin/python3

import os

print("""Content-Type: text/html

<html>
<head><title>Tiqit Icons</title></head>
<body>
<table border='0'>""")

files = os.listdir('.')
files.sort()

for f in files:
    if f.split('.')[-1].lower() in ('png', 'gif', 'jpg'):
      print("<tr><td><img src='%s'></td><td>%s</td></tr>" % (f, f))

print("""</table>
</body>
</html>
""")
