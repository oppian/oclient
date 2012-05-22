#!/usr/bin/env python

# Author      : Stephen Hartley
# Copyright   : (c) Oppian Systems Ltd.
# Description : This tool erases the previous generated air files and rebuilds the air package
 
import sys
import os
import shutil
import subprocess

print
print "Build_AIR"
print "---------"

on_mac = sys.platform == 'darwin'
sdk_version = "4.0.1"

def do_cmd(popenargs):
    sys.stdout.flush()
    print "CMD: [" + " ".join(popenargs) +"]",
    ret = subprocess.call(popenargs)
    print "ret %d" % ret
    if ret:
        error("Command returned error", ret)

def erase(item):
    print 'Checking if "%s" exists' % item
    if on_mac:
        do_cmd(["rm", "-fr", item])
    else:
        if os.path.isdir(item):
            print 'Removing directory "%s"' % item
            for the_file in os.listdir(item):
                file_path = os.path.join(item, the_file)
                erase(file_path)
            shutil.rmtree(item)
        elif os.path.isfile(item):
            print 'Removing old version of "%s"' % item
            os.unlink(item)
        
def error(description, code=1):
    print "Error(%d): %s" %(code, description)
    quit(code)

adt = os.path.normpath(os.path.join("..", "SDK", sys.platform, sdk_version, "bin", "adt"))
if not on_mac:
    adt += ".bat"

if on_mac:
    out_root = "mac"

out_name = "oFrame"
certificate = os.path.join("certificate", "oppian.p12")
password = "nopassword"
src_dir = os.path.join("out", "debug")
app_xml = os.path.join(src_dir, out_name+"-app.xml")
out_dir = os.path.join("out", "release")
out_file = os.path.join(out_dir, out_name+".air")
swf = out_name+".swf"
swf_full = os.path.join(src_dir, swf)

print 'system = %s (on_mac=%d)' % (sys.platform, on_mac)
print "\nArguments:"
print '%20s : "%s" (exists:%d)' % ('adt tool', adt, os.path.exists(adt))
print '%20s : "%s" (exists:%d)' % ('certificate ', certificate, os.path.exists(certificate))
print '%20s : "%s"' % ('password', password)
print '%20s : "%s" (exists:%d)' %('app_xml', app_xml, os.path.exists(app_xml))
print '%20s : "%s" (exists:%d)' %('source dir', src_dir, os.path.exists(src_dir))
print '%20s : "%s" (exists:%d)' %('app swf', swf_full, os.path.exists(swf_full))
print '%20s : "%s"' % ('current directory', os.getcwd())
print

if not os.path.exists(adt):
	error("Cannot find adt tool (%s)" % adt)
if not os.path.exists(certificate):
	error("Cannot find certificate - %s" % certificate)
if not os.path.exists(app_xml):
    error("Cannot find application XML file (%s)"% app_xml)
if not os.path.exists(src_dir):
    error("Cannot find source directory (%s)" % src_dir)
if not os.path.exists(swf_full):
    error("Cannot find application SWF (%s)" % swf_full)

do_cmd([ adt, '-version'])
do_cmd([ adt,
         "-package",
         "-storetype", "pkcs12", "-keystore", certificate, "-storepass", password,
         '-target', 'air', out_file,
         app_xml, 
         '-C', src_dir, swf,
         '-C', src_dir, "assets",
        ])

print "Finished building air\n\n"