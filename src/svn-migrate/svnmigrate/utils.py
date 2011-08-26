
import os
import shlex
import subprocess


def path(*arg):
    return os.path.abspath(os.path.join(*arg))

def call(cmd, *arg, **kw):
    cwd = ''
    if 'cwd' in kw:
        cwd = ' ( at %s )' % kw['cwd']
    #print "COMMAND: " + cmd + cwd
    return subprocess.Popen(shlex.split(cmd), *arg, **kw).communicate()[0]

def header(txt):
    print
    print '-'*len(txt)
    print txt
    print '-'*len(txt)
    print

def line(txt, level=0):
    print ' '*level*4 + txt

def sha_checklist(directory):
    checklist = []
    for root, dirs, files in os.walk(directory):
        for names in files:
            checklist.append(
                    call('sha1sum '+path(root,names), stdout=subprocess.PIPE),
                    )
    return checklist

