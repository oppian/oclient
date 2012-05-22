#!/usr/bin/env python

# Author      : Stephen Hartley
# Copyright   : (c) Oppian Systems Ltd.
# Description : This tool automatically uninstalls the oFrame.  Note that if the tool or installer is currently running, then they are forcibly exited.

import sys
import os
import shutil
import subprocess

print "Uninstall"
print "---------"

on_mac = sys.platform == 'darwin'

if not on_mac:
    
    import _winreg as reg
    
    # convenience dicts
    vTyp={
        reg.REG_BINARY : 'BIN',
        reg.REG_DWORD : 'DW',
        reg.REG_DWORD_BIG_ENDIAN : 'DWB',
        reg.REG_DWORD_LITTLE_ENDIAN : 'DWL',
        reg.REG_EXPAND_SZ : 'XSZ',
        reg.REG_LINK : 'LNK',
        reg.REG_MULTI_SZ : 'MSZ',
        reg.REG_RESOURCE_LIST : 'RES',
        reg.REG_SZ : 'STR',
        reg.REG_NONE : 'NUL',
        }
    rTyp=dict((v, k) for k, v in vTyp.items())
    
    indent='\t'     # the string used for indented output
    
    class Val(object):
        # Registry Value
        def __init__(self, key, name, val, typ):
            self.key, self.name, self.val, self.typ = key, name, val, typ
        @property
        def indented(self):
            return '%s%s' % (indent*(self.key.level+1), self.__str__())
        def __str__(self):
            val=' - bin -' if self.typ==rTyp['BIN']  else self.val
            return '%s : %s' % (self.name, val)
    
    class Key(object):
        # Registry Key
        def __init__(self, parent, name):
            self.parent, self.name = parent, name
            self.level=parent.level+1
            # ! ! ! opens keys in read/write mode ! ! !
            self.wrk=reg.OpenKey(parent.wrk, self.name, 0, reg.KEY_ALL_ACCESS)
            self._keys = self._vals = None
        @property
        def keys(self):
            # returns a dict of subkeys
            if not self._keys:
                self._keys={}
                for i in xrange(reg.QueryInfoKey(self.wrk)[0]):
                    name=reg.EnumKey(self.wrk, i).lower()
                    try:
                        self._keys[name]=Key(self, name)
                    except WindowsError: pass
            return self._keys
        @property
        def vals(self):
            # returns the list of values
            if not self._vals:
                self._vals=[]
                for i in xrange(reg.QueryInfoKey(self.wrk)[1]):
                    try:
                        self._vals.append(Val(self, *reg.EnumValue(self.wrk, i)))
                    except WindowsError: pass
            return self._vals
        def __call__(self, path):
            # access to a key
            path=path.lower()
            key=self
            for p in path.split('/'):
                key=key.keys[p]
            return key
        def __str__(self):
            return '%s%s/' % (self.parent.__str__(), self.name)
        @property
        def indented(self):
            return '%s%s' % (indent*self.level, self.name)
        def walk(self):
            # walk thru the subkeys tree
            for key in self.keys.itervalues():
                yield key
                for k in key.walk():
                    yield k
        def grep(self, text, kv='both', typ=(rTyp['STR'],)):
            # searching keys and/or values for some text
            for k in self.walk():
                if kv in ('keys', 'both') and text in k.name:
                    yield k, None
                if kv in ('vals', 'both'):
                    for v in k.vals:
                        if (v.typ in typ) and (text in v.val):
                            yield k, v
        def grep2(self, text, kv='both', typ=(rTyp['STR'],)):
            # a grep variant, might be more convinient in some cases
            kb=None
            for k in self.walk():
                if kv in ('keys', 'both') and text in k.name:
                    if kv=='both':
                        yield k, False
                        kb=k
                    else:
                        yield k
                if kv in ('vals', 'both'):
                    for v in k.vals:
                        if (v.typ in typ) and (text in v.val):
                            if kv=='both':
                                if k!=kb:
                                    yield k, False
                                    kb=k
                                yield v, True
                            else:
                                yield v
        def create(self, path):
            # create a subkey, and the path to it if necessary
            k=self
            for p in path.split('/'):
                if p in k.keys:
                    k=k.keys[p]
                else:
                    reg.CreateKey(k.wrk, p)
                    k=Key(k, p)
            return k
        def setVal(self, name, val, typ='str'):
            # set value
            typ=typ.upper()
            if typ=='DW': typ='DWL'
            typ=rTyp[typ]
            reg.SetValueEx(self.wrk, name, 0, typ, val)
    
    class Hkey(Key):
        # Registry HKey
        def __init__(self, name):
            self.parent=None
            self.level=0
            self.name=name
            self.wrk=reg.ConnectRegistry(None, getattr(reg, name))
            self._keys=None
            self._vals=None
        def __str__(self):
            return '/%s/' % self.name
    
    class Root(Key):
        # Registry Root
        def __init__(self):
            self.hkey={}
            for key in (k for k in dir(reg) if k.startswith('HKEY_')):
                try:
                    chk = reg.ConnectRegistry(None, getattr(reg, key))
                    inf = reg.QueryInfoKey(chk)
                    reg.CloseKey(chk)
                except WindowsError: pass           # some keys may appear in _winreg but can't be reached
                else:
                    hk = Hkey(key)
                    try:
                        chk=hk.keys
                    except WindowsError: pass       # some keys can be accessed but not enumerated
                    else:                           # some keys work fine ...
                        name=key[5:].lower()
                        self.hkey[name]=hk          # for iterating
                        setattr(self, name, hk)     # for easy access
        @property
        def keys(self):
            return self.hkey
    
    root=Root()         # we should need only one Root per application, so let's instanciate it here.

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
    #quit(code)

print "Doing install/uninstall stage"

out_name = "oFrame"

if on_mac:
    print "On Mac"
    
    print "Closing the app, if running"
    do_cmd(['killall', '-v', '-e', '-z','-SIGKILL', '-c', out_name])
    
    print "Closing the installer, if running"
    do_cmd(['killall', '-v', '-e', '-z','-SIGKILL', '-c', 'Install '+out_name])
    do_cmd(['killall', '-v', '-e', '-z','-SIGKILL', '-c', 'Adobe AIR Application Installer'])
    
    print "Doing uninstall..."
    erase('/Applications/'+out_name+'.app')
    
    print "Unmounting "+out_name+" DMG"
    lines = subprocess.Popen(["mount"], stdout=subprocess.PIPE).communicate()[0].split('\n')
    for line in lines:
        if line.find(out_name)>0:
            device=line.split(' ')[0]
            do_cmd(['hdiutil', 'unmount', device])
    
    print "Doing uninstall..."
    erase('/Applications/'+out_name+'.app')
    
else:
    print "On Windows"
    
    print "Closing the app if running"
    do_cmd(['taskkill', '/t', '/f', '/im', '%s.exe'%out_name]) 
    do_cmd(['taskkill', '/t', '/f', '/im', 'Install %s.exe'%out_name]) 
    
    print "Doing uninstall..."
    import re
    p = re.compile('/(?P<productCode>{.+})/$')
    try:
        kb=root.local_machine('software/microsoft/windows/currentversion/uninstall')
        for k, v in kb.grep(out_name, kv='vals'):
            m = p.search(str(k))
            if m:
                do_cmd(['msiexec', '/x', m.group('productCode'), '/quiet'])
                break
    except UnicodeError: pass
    
    erase('c:\Program Files\%s'%out_name)
    
print "Finished uninstall\n\n"