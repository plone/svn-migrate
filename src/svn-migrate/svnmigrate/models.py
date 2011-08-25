
import os
from svnmigrate.utils import path
from svnmigrate.utils import call
from svnmigrate.utils import header 


class SvnRepo(object):

    def __init__(self, config, name, remote_url):
        self.config = config
        self.name = name
        self.remote_url = remote_url

    def initialize(self):
        svn_mirror = path(self.config.svn_mirror, self.name)
        if not os.path.isdir(svn_mirror):
            header('Initializing %s repository.' % self.name)
            call("svnadmin create %s" % svn_mirror)
            hook_path = path(svn_mirror, 'hooks', 'pre-revprop-change')
            with open(hook_path, 'w') as fd:
                fd.writelines(['#!/bin/sh\n', 'exit 0'])
            call('chmod 755 ' + hook_path)
            call('svnsync init file://%s %s' % (svn_mirror, self.remote_url))

    def sync(self):
        header('Syncing %s repository.' % self.name)
        svn_mirror = path(self.config.svn_mirror, self.name)
        call('svn propget svn:sync-last-merged-rev --revprop -r 0 file://%s' % svn_mirror)
        call('svnsync --non-interactive sync file://%s' % svn_mirror)
        call('svnadmin pack %s' % svn_mirror)
