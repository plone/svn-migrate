import os
import os.path

REPOS = ('archetypes', 'plone') # collective?
REMOTE_BASE = 'http://svn.plone.org/svn/'

cwd = os.path.abspath(os.curdir)
repos_path = os.path.join(cwd, 'svn-repos')


def init_repo(repo):
    repo_path = os.path.join(repos_path, repo)
    repo_url = 'file://' + repo_path
    if not os.path.isdir(repo_path):
        os.system("svnadmin create %s" % repo_path)
    hook_path = os.path.join(repo_path, 'hooks', 'pre-revprop-change')
    with open(hook_path, 'w') as fd:
        fd.writelines(['#!/bin/sh\n', 'exit 0'])
    os.system('chmod 755 ' + hook_path)
    os.system('svnsync init %s %s%s' % (repo_url, REMOTE_BASE, repo))


def sync_repo(repo):
    repo_path = os.path.join(repos_path, repo)
    repo_url = 'file://' + repo_path
    print('Current remote revision:')
    os.system('svn info --xml %s%s | grep "revision=" | uniq' %
        (REMOTE_BASE, repo))
    print('Last synced revision:')
    os.system('svn propget svn:sync-last-merged-rev --revprop -r 0 ' + repo_url)
    os.system('svnsync --non-interactive sync ' + repo_url)


def main():
    if not os.path.isdir(repos_path):
        os.mkdir(repos_path)

    for repo in REPOS:
        init_repo(repo)

    for repo in REPOS:
        sync_repo(repo)


if __name__ == '__main__':
    main()
