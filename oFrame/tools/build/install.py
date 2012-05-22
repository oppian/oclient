#!/usr/bin/env python

# Author      : Stephen Hartley
# Copyright   : (c) Oppian Systems Ltd.
# Description : This tool triggers the install of the generated AdobeMobilePackager - it is completed manually by the user.

import sys
import os
import shutil
import subprocess

print 
print "Install"
print "-------"

on_mac = sys.platform == 'darwin'

def do_cmd(popenargs):
    sys.stdout.flush()
    print "CMD: [" + " ".join(popenargs) +"]",
    ret = subprocess.call(popenargs)
    print "ret %d" % ret
    if ret:
        error("Command returned error", ret)


def error(description, code=1):
    print "Error(%d): %s" %(code, description)
    #quit(code)

print "Doing install stage"

out_name = "oFrame"
air_file = os.path.join("%s.air"%out_name)

if on_mac:
    print "On Mac"
    
    print "Doing install..."
    do_cmd(["open", "-a", 'Adobe AIR Application Installer', air_file])
    
else:
    print "On Windows"
    
    print "Doing install..."
    do_cmd([air_file])

print "Finished install\n\n"