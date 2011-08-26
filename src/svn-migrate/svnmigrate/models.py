
import os
import time
import shutil
from argh.helpers import confirm
from subprocess import PIPE
from svnmigrate.utils import path
from svnmigrate.utils import call
from svnmigrate.utils import header 
from svnmigrate.utils import line


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

    def cleanup(self):
        if not os.path.isdir(path(self.config.git_cleaned, self.svn_repo)):
            call('mkdir -p %s' % path(self.config.git_cleaned, self.svn_repo))

        svn_mirror = path(self.config.svn_mirror, self.svn_repo, self.name)
        svn_export = path(self.config.svn_export, self.svn_repo, self.name)
        git_cleaned = path(self.config.git_cleaned, self.svn_repo, self.name)

        if not os.path.isdir(svn_export):
            return

        #svn_repo_projects = dict(config.items(svn_repo))
        svn_repos = dict()
        for svn_repo in self.config.svn_repos:
            svn_repos[svn_repo.name] = svn_repo

        if os.path.isdir(git_cleaned):
            # be 100% that we are deleting something from git_cleaned folder
            if git_cleaned.startswith(self.config.git_cleaned):
                call('rm -rf %s' % git_cleaned)

        header('Cleaning: %s' % self.name)
        shutil.copytree(svn_export, git_cleaned)

        ## remove tags with revision specific information in them
        for tag in call('git tag -l', cwd=git_cleaned, stdout=PIPE).split('\n'):
            if '@' in tag and 'master' not in tag:
                call('git tag -d ' + tag.strip(), cwd=git_cleaned)

        ## get a list of svn/git branches
        svn_branches = [ item.strip().rstrip('/')
                for item in call('svn ls file://%s/%s%s/branches' % \
                    (self.config.svn_mirror, self.svn_repo, self.svn_path),
                    stdout=PIPE).split('\n') if item.strip() ]
        git_branches = [ item.strip().replace('* ', '') for item in
                call('git branch --no-color', cwd=git_cleaned,
                    stdout=PIPE).split('\n') if item.strip() ]

        ## remove branches
        for git_branch in ((set(git_branches) - set(svn_branches)) \
                - set(['master'])):
            if self.config.version_regex.match(git_branch) is None:
                call('git branch -D %s' % git_branch, cwd=git_cleaned)

        call('git gc --aggressive --prune=now --quiet', cwd=git_cleaned)
        call('git remote add origin git@github.com:plone/%s.git' % \
                self.name, cwd=git_cleaned)

    def publish(self, gh, gh_repos):

        git_cleaned = path(self.config.git_cleaned, self.svn_repo, self.name)
        if not os.path.isdir(git_cleaned):
            return
        
        gh_repo_name = 'plone/' + self.name
        if self.name in gh_repos.keys():
            if confirm('Do you want to delete "%s" repository from '
                       'github?' % gh_repo_name):
                gh.repos.delete(gh_repo_name)
                header('"%s" deleted!' % gh_repo_name)
                time.sleep(5)
            else:
                header('"%s" SKIPPED.' % gh_repo_name)
                return

        gh.repos.create(gh_repo_name)
        header('"%s" created.' % gh_repo_name)

        call('git push --all', cwd=git_cleaned)
        call('git push --tags', cwd=git_cleaned)


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

    def export(self, authors_file, repos):
        header('Exporting %s repository.' % self.name)

        svn_mirror = path(self.config.svn_mirror, self.name)
        svn_export = path(self.config.svn_export, self.name)

        if not os.path.isdir(svn_export):
            call('mkdir -p %s' % svn_export)

        repos_to_process = []
        for repo in self.config.get_repos(self.name):
            if os.path.isfile(repo.rules) and \
               (repos is None or repo.name in repos.split(';')):
                repos_to_process.append(repo)

        # remove all previously exported repositories
        for repo in repos_to_process:
            repo_path = path(svn_export, repo.name)
            if os.path.isdir(repo_path):
                # just to be 100% we are removing something from svn_export folder
                if repo_path.startswith(svn_export):
                    call('rm -rf %s' % repo_path)

        call('%s --identity-map %s --rules %s --add-metadata %s' % (
                self.config.svn_all_fast_export, authors_file,
                ','.join([ repo.rules for repo in repos_to_process ]),
                svn_mirror), cwd=svn_export)
