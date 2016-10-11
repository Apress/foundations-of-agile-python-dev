# Simulator from Music Player demo.
#legalStuff cc02 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff


# This discrete event simulator supports three events
# each of which is open coded in the body of the simulator.


import time as timeModule
from fit.ActionFixture import ActionFixture


time = timeModule.time() # Time is a float
time = int(time) * 1000 # convert to milliseconds as int.
# changed long to int above

nextSearchComplete = 0
nextPlayStarted = 0
nextPlayComplete = 0

def nextEvent(bound):
    result = bound
    result = sooner(result, nextSearchComplete)
    result = sooner(result, nextPlayStarted)
    result = sooner(result, nextPlayComplete)
    return result

def sooner(soon, event):
    if time < event < soon:
        return event
    return soon

def perform():
    if time == nextSearchComplete:
        MusicLibrary.searchComplete()
    if time == nextPlayStarted:
        MusicPlayer.playStarted()
    if time == nextPlayComplete:
        MusicPlayer.playComplete()

def advance(future):
    global time
    while time < future:
        time = nextEvent(future)
        perform()

def schedule(seconds):
    return time + int(seconds * 1000)

def delay(seconds):
    advance(schedule(seconds))

def waitSearchComplete():
    advance(nextSearchComplete)

def waitPlayStarted():
    advance(nextPlayStarted)

def waitPlayComplete():
    advance(nextPlayComplete)

def failLoadJam():
    ActionFixture.actor = Dialog("load jamed", ActionFixture.actor)


