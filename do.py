import argparse
import ConfigParser
import os
import os.path
import shutil

REPOS = ('archetypes', 'collective', 'plone')
REMOTE_SVN_BASE = 'http://svn.plone.org/svn/'

cwd = os.path.abspath(os.curdir)
TOOLS_PATH = os.path.join(cwd, 'svn2git')
SVN_REPOS_PATH = os.path.join(cwd, 'repos', 'svn-mirror')
SVN_EXPORT_PATH = os.path.join(cwd, 'repos', 'svn-export')
GIT_REPOS_PATH = os.path.join(cwd, 'repos', 'git')
AUTHORS_PATH = os.path.join(cwd, 'authors-map')

parser = argparse.ArgumentParser(description='Do stuff!')
parser.add_argument('command', choices=[
    'svn-init', 'svn-sync', 'svn-authors', 'svn-export', 'git-copy'])


IGNORED = frozenset([
    'Products.kupu',
    'plone.app.locales',
])


def _create_config_parser():
    config = ConfigParser.RawConfigParser()
    config.optionxform = lambda s: s
    return config


def svn_run_for_repos(func):
    for repo in REPOS:
        repo_path = os.path.join(SVN_REPOS_PATH, repo)
        repo_url = 'file://' + repo_path
        func(repo, repo_path, repo_url)


def svn_init(repo, repo_path, repo_url):
    if not os.path.isdir(repo_path):
        os.system("svnadmin create %s" % repo_path)
    hook_path = os.path.join(repo_path, 'hooks', 'pre-revprop-change')
    with open(hook_path, 'w') as fd:
        fd.writelines(['#!/bin/sh\n', 'exit 0'])
    os.system('chmod 755 ' + hook_path)
    os.system('svnsync init %s %s%s' % (repo_url, REMOTE_SVN_BASE, repo))


def svn_sync(repo, repo_path, repo_url):
    os.system('svn propget svn:sync-last-merged-rev --revprop -r 0 ' + repo_url)
    os.system('svnsync --non-interactive sync ' + repo_url)
    os.system('svnadmin pack ' + repo_path)


def svn_authors(repo, repo_path, repo_url):
    repo_author_path = os.path.join(cwd, 'authors-%s.txt' % repo)
    if not os.path.isfile(repo_author_path):
        os.system('svn log --xml --with-revprop svn:author %s | '
            'grep "^<author>" | sort -u > %s' % (repo_url, repo_author_path))
    names = []
    with open(repo_author_path, 'r') as fd:
        for line in fd.readlines():
            name = line.replace('<author>', '').replace('</author>\n', '')
            names.append(name)
    out = '{name} {name} <{name}@localhost>\n'
    new_authors_path = os.path.join(cwd, 'authors-new')
    if not os.path.isfile(AUTHORS_PATH):
        os.system('touch %s' % AUTHORS_PATH)
    shutil.copyfile(AUTHORS_PATH, new_authors_path)
    with open(new_authors_path, 'a') as fd:
        for name in names:
            fd.write(out.format(name=name))
    os.system('cat %s | sort | uniq > %s' % (new_authors_path, AUTHORS_PATH))
    os.remove(new_authors_path)


def svn_export(repo, repo_path, repo_url):
    if repo != 'archetypes':
        return
    tool = os.path.join(TOOLS_PATH, 'svn-all-fast-export')
    rules = os.path.join(cwd, 'rules-%s.cfg' % repo)
    mirror = os.path.join(SVN_REPOS_PATH, repo)
    try:
        os.chdir(SVN_EXPORT_PATH)
        os.system('{tool} --identity-map={authors} --rules={rules} '
            '--add-metadata {mirror}'.format(tool=tool, authors=AUTHORS_PATH,
                rules=rules, mirror=mirror))
    finally:
        os.chdir(cwd)


def git_copy():
    git_svn_base_path = os.path.join(SVN_EXPORT_PATH)
    git_base_path = os.path.join(GIT_REPOS_PATH)
    names = [n for n in os.listdir(git_svn_base_path) if not n.startswith('.')]
    for name in names:
        svn_path = os.path.join(git_svn_base_path, name)
        if not os.path.isdir(svn_path):
            continue
        git_path = os.path.join(git_base_path, name)
        if os.path.isdir(git_path):
            print('Skipping git clone of ' + name)
            continue
        shutil.copytree(svn_path, git_path)
        try:
            os.chdir(git_path)
            os.system(os.path.join(TOOLS_PATH, 'git-svn-abandon-fix-refs'))
            # remove tags with revision specific information in them
            os.system('git tag -l | grep "@" | xargs git tag -d')
            os.system(os.path.join(TOOLS_PATH, 'git-svn-abandon-cleanup'))
            # XXX test-prefix
            os.system('git remote add origin git@github.com:plone/'
                'test-%s.git' % name)
        finally:
            os.chdir(cwd)


def main():
    commands = {
        'svn-init': (svn_run_for_repos, svn_init),
        'svn-sync': (svn_run_for_repos, svn_sync),
        'svn-authors': (svn_run_for_repos, svn_authors),
        'svn-export': (svn_run_for_repos, svn_export),
        'git-copy': (git_copy, None),
    }

    arguments = parser.parse_args()
    command, argument = commands.get(arguments.command)
    if argument is None:
        command()
    else:
        command(argument)


if __name__ == '__main__':
    main()
