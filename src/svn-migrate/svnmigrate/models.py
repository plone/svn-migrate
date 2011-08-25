
import os
from svnmigrate.utils import path
from svnmigrate.utils import call
from svnmigrate.utils import header 


class Repo(object):

    def __init__(self, config, name, rules, svn_repo, svn_path,
            git_url, status, *arg, **kw):
        self.config = config
        self.name = name
        self.rules = rules
        self.svn_repo = svn_repo
        self.svn_path = svn_path
        self.git_url = git_url
        self.status = status


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

    def export(self):
        svn_mirror = path(self.config.svn_mirror, self.name)
        svn_export = path(self.config.svn_export, self.name)

        if args.rules_file is None:
            rules = path(CWD, 'rules-%s.cfg' % svn_repo)
        else:
            rules = path(args.rules_file)

        if not os.path.isdir(svn_repo_export):
            call('mkdir %s -p' % svn_repo_export)

        call('%s --identity-map %s --rules %s --add-metadata %s' % (
                args.svn_all_fast_export, args.authors, rules, svn_repo_mirror),
                cwd=svn_repo_export)
