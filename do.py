import argparse
import ConfigParser
import os
import os.path
import re
import shutil
import subprocess

REPOS = ('archetypes', 'collective', 'plone')
REMOTE_SVN_BASE = 'http://svn.plone.org/svn/'

cwd = os.path.abspath(os.curdir)
TOOLS_PATH = os.path.join(cwd, 'svn2git')
SVN_REPOS_PATH = os.path.join(cwd, 'repos', 'svn-mirror')
SVN_EXPORT_PATH = os.path.join(cwd, 'repos', 'svn-export')
GIT_REPOS_PATH = os.path.join(cwd, 'repos', 'git')
AUTHORS_PATH = os.path.join(cwd, 'authors-map')
PROJECTS_PATH = os.path.join(cwd, 'projects.cfg')
VERSION_RE = re.compile(r'^(plone|v)?[\d._-]+'
    '(alpha|beta|branch|rc|RC|final|a|b|c|x)?(\d)*$')

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


def run_for_repos(func):
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
    tool = os.path.join(TOOLS_PATH, 'svn-all-fast-export')
    rules = os.path.join(cwd, 'rules-%s.cfg' % repo)
    mirror = os.path.join(SVN_REPOS_PATH, repo)
    target = os.path.join(SVN_EXPORT_PATH, repo)
    if not os.path.isdir(target):
        os.mkdir(target)
    try:
        os.chdir(target)
        os.system('{tool} --identity-map={authors} --rules={rules} '
            '--add-metadata {mirror}'.format(tool=tool, authors=AUTHORS_PATH,
                rules=rules, mirror=mirror))
    finally:
        os.chdir(cwd)


def git_copy(repo, repo_path, repo_url):
    mirror = os.path.join(SVN_EXPORT_PATH, repo)
    if not os.path.isdir(mirror):
        print('Skipping copy of repository ' + repo)
        return
    config = _create_config_parser()
    config.read(PROJECTS_PATH)
    projects = dict(config.items(repo))
    git_base_path = os.path.join(GIT_REPOS_PATH, repo)
    if not os.path.isdir(git_base_path):
        os.mkdir(git_base_path)
    names = [n for n in os.listdir(mirror) if not n.startswith('.') and
        os.path.isdir(os.path.join(mirror, n))]
    for name in names:
        bare_git_path = os.path.join(mirror, name)
        git_path = os.path.join(git_base_path, name)
        if os.path.isdir(git_path):
            print('Skipping copy of ' + name)
            continue
        print('Processing: %s' % name)
        shutil.copytree(bare_git_path, git_path)
        # get a list of current active svn branches
        remote_svn_url = projects.get(name)
        svn_url = remote_svn_url.replace(REMOTE_SVN_BASE + repo, repo_url)
        output = subprocess.check_output(['svn', 'ls', svn_url + '/branches'])
        svn_branches = [o.strip().rstrip('/') for o in
            output.split('\n') if o.strip()]
        try:
            os.chdir(git_path)
            # remove tags with revision specific information in them
            os.system('git tag -l | grep "@" | xargs git tag -d')
            output = subprocess.check_output(['git', 'branch', '--no-color'])
            git_branches = [o.strip() for o in output.split('\n') if o.strip()]
            git_branches = [b.replace('* ', '') for b in git_branches]
            extra_branches = set(git_branches) - set(svn_branches)
            extra_branches = extra_branches - set(['master'])
            for e in extra_branches:
                match = VERSION_RE.match(e)
                if match is None:
                    os.system('git branch -D %s' % e)
            print('Running garbage collection')
            os.system('git gc --aggressive --prune=now --quiet')
            # TODO test-prefix
            os.system('git remote add origin git@github.com:plone/'
                'test-%s.git' % name)
        finally:
            os.chdir(cwd)
        print('Processed %s\n' % name)


def main():
    commands = {
        'svn-init': (run_for_repos, svn_init),
        'svn-sync': (run_for_repos, svn_sync),
        'svn-authors': (run_for_repos, svn_authors),
        'svn-export': (run_for_repos, svn_export),
        'git-copy': (run_for_repos, git_copy),
    }

    arguments = parser.parse_args()
    command, argument = commands.get(arguments.command)
    if argument is None:
        command()
    else:
        command(argument)


if __name__ == '__main__':
    main()
