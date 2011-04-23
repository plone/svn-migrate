import argparse
import os
import os.path

REPOS = ('archetypes', 'plone') # collective?
REMOTE_SVN_BASE = 'http://svn.plone.org/svn/'

cwd = os.path.abspath(os.curdir)
repos_path = os.path.join(cwd, 'svn-repos')

parser = argparse.ArgumentParser(description='Do stuff!')
parser.add_argument('command', choices=['svn-init', 'svn-sync'])


def init_svn_mirror(repo, repo_path, repo_url):
    if not os.path.isdir(repo_path):
        os.system("svnadmin create %s" % repo_path)
    hook_path = os.path.join(repo_path, 'hooks', 'pre-revprop-change')
    with open(hook_path, 'w') as fd:
        fd.writelines(['#!/bin/sh\n', 'exit 0'])
    os.system('chmod 755 ' + hook_path)
    os.system('svnsync init %s %s%s' % (repo_url, REMOTE_SVN_BASE, repo))


def sync_svn_mirror(repo, repo_path, repo_url):
    print('Current remote revision:')
    os.system('svn info --xml %s%s | grep "revision=" | uniq' %
        (REMOTE_SVN_BASE, repo))
    print('Last synced revision:')
    os.system('svn propget svn:sync-last-merged-rev --revprop -r 0 ' + repo_url)
    os.system('svnsync --non-interactive sync ' + repo_url)


def run(func):
    for repo in REPOS:
        repo_path = os.path.join(repos_path, repo)
        repo_url = 'file://' + repo_path
        func(repo, repo_path, repo_url)


def main():
    commands = {
        'svn-init': init_svn_mirror,
        'svn-sync': sync_svn_mirror,
    }

    arguments = parser.parse_args()
    command = commands.get(arguments.command)
    run(command)


if __name__ == '__main__':
    main()
