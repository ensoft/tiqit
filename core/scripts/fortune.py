#!/usr/bin/python

import signal, commands, time, sys, os
from tiqit import *

__all__ = ['startFortunes', 'stopFortunes']

pid = 0
keepgoing = True

def doFortunes():
    def handler(signum, frame):
        global keepgoing
        keepgoing = False

    signal.signal(signal.SIGTERM, handler)

    while keepgoing:
        joke = commands.getoutput('/usr/games/fortune -s')
        if keepgoing:
            print """
    <div id='tiqitFortuneNew' class='tiqitFortune'>
      <img src='images/fortune.gif' onload='nextFortune()' onclick='hideFortune(this);' title='Hide Fortune Cookie'>
      <pre>%s</pre></div>""" % encodeHTML(joke)
            sys.stdout.flush()
            time.sleep(len(joke) < 100 and 10 or len(joke) / 10)

    sys.exit()

def startFortunes():
    global pid
    sys.stdout.flush()
    pid = os.fork()
    if pid == 0:
        doFortunes()

def stopFortunes():
    global pid
    if pid != 0:
        os.kill(pid, signal.SIGKILL)
