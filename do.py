import argparse
import ConfigParser
import os
import os.path
import shutil
import urllib2

REPOS = ('archetypes', 'collective', 'plone')
REMOTE_SVN_BASE = 'http://svn.plone.org/svn/'
SOURCES_URL = 'http://svn.plone.org/svn/plone/buildouts/plone-coredev/' \
    'branches/4.1/sources.cfg'

cwd = os.path.abspath(os.curdir)
TOOLS_PATH = os.path.join(cwd, 'git-svn-abandon')
SVN_REPOS_PATH = os.path.join(cwd, 'repos', 'svn-mirror')
GIT_SVN_REPOS_PATH = os.path.join(cwd, 'repos', 'git-svn')
GIT_REPOS_PATH = os.path.join(cwd, 'repos', 'git')
AUTHORS_PATH = os.path.join(cwd, 'authors.txt')
PROJECTS_PATH = os.path.join(cwd, 'projects.cfg')

parser = argparse.ArgumentParser(description='Do stuff!')
parser.add_argument('command', choices=[
    'svn-init', 'svn-sync', 'svn-authors', 'project-list',
    'git-svn-init', 'git-svn-fetch', 'git-copy'])


IGNORED = frozenset([
    'Products.kupu',
    'plone.app.locales',
])


def _create_config_parser():
    config = ConfigParser.RawConfigParser()
    config.optionxform = lambda s: s
    return config


def svn_init(repo, repo_path, repo_url):
    if not os.path.isdir(repo_path):
        os.system("svnadmin create %s" % repo_path)
    hook_path = os.path.join(repo_path, 'hooks', 'pre-revprop-change')
    with open(hook_path, 'w') as fd:
        fd.writelines(['#!/bin/sh\n', 'exit 0'])
    os.system('chmod 755 ' + hook_path)
    os.system('svnsync init %s %s%s' % (repo_url, REMOTE_SVN_BASE, repo))


def svn_sync(repo, repo_path, repo_url):
    print('Current remote revision:')
    os.system('svn info --xml %s%s | grep "revision=" | uniq' %
        (REMOTE_SVN_BASE, repo))
    print('Last synced revision:')
    os.system('svn propget svn:sync-last-merged-rev --revprop -r 0 ' + repo_url)
    os.system('svnsync --non-interactive sync ' + repo_url)


def svn_authors(repo, repo_path, repo_url):
    repo_author_path = os.path.join(cwd, 'authors-%s.txt' % repo)
    if not os.path.isfile(repo_author_path):
        os.system('svn log --xml %s | grep "^<author>" | '
            'sort | uniq > %s' % (repo_url, repo_author_path))
    names = []
    with open(repo_author_path, 'r') as fd:
        for line in fd.readlines():
            name = line.replace('<author>', '').replace('</author>\n', '')
            names.append(name)
    out = '{name} = {name} <{name}@localhost>\n'
    new_authors_path = os.path.join(cwd, 'authors-new.txt')
    shutil.copyfile(AUTHORS_PATH, new_authors_path)
    with open(new_authors_path, 'a') as fd:
        for name in names:
            fd.write(out.format(name=name))
    os.system('cat %s | sort | uniq > authors.txt' % new_authors_path)
    os.remove(new_authors_path)


def svn_run_for_repos(func):
    for repo in REPOS:
        repo_path = os.path.join(SVN_REPOS_PATH, repo)
        repo_url = 'file://' + repo_path
        func(repo, repo_path, repo_url)


def project_list():
    resource = urllib2.urlopen(SOURCES_URL, timeout=10)
    sources_path = os.path.join(cwd, 'sources-4.1.cfg')
    with open(sources_path, 'w') as fd:
        fd.write(resource.read())

    config = _create_config_parser()
    config.read(sources_path)

    items = config.items('sources')
    projects = {}
    for repo in REPOS:
        projects[repo] = []
    base = 'https://svn.plone.org/svn/'
    plone_items = [(k, v.lstrip('svn ')) for k, v in items
        if v.startswith('svn ' + base) and k not in IGNORED]

    for repo in REPOS:
        repo_base = base + repo + '/'
        for k, v in plone_items:
            if v.startswith(repo_base):
                if k in v:
                    name = k
                else:
                    name = k.replace('Products.', '')
                base_url = v[:v.find(name) + len(name)]
                base_url = base_url.replace('https:', 'http:')
                projects[repo].append((k, base_url))

    config = _create_config_parser()
    for repo, values in projects.items():
        config.add_section(repo)
        for k, v in values:
            config.set(repo, k, v)

    with open(PROJECTS_PATH, 'w') as fd:
        config.write(fd)


def git_svn_init(repo, repo_path, repo_url):
    config = _create_config_parser()
    config.read(PROJECTS_PATH)
    git_base_path = os.path.join(GIT_SVN_REPOS_PATH)
    projects = config.items(repo)
    for name, url in projects:
        git_repo_path = os.path.join(git_base_path, name)
        if os.path.isdir(git_repo_path):
            continue
        local_svn_url = url.replace(REMOTE_SVN_BASE + repo, repo_url)
        os.system('git svn init --prefix=svn/ --stdlayout %s %s' %
            (local_svn_url, git_repo_path))


def git_svn_fetch():
    git_svn_base_path = os.path.join(GIT_SVN_REPOS_PATH)
    names = [n for n in os.listdir(git_svn_base_path) if not n.startswith('.')]
    for name in names:
        path = os.path.join(git_svn_base_path, name)
        if not os.path.isdir(path):
            continue
        try:
            os.chdir(path)
            os.system('git svn fetch --authors-file=' + AUTHORS_PATH)
        finally:
            os.chdir(cwd)


def git_copy():
    git_svn_base_path = os.path.join(GIT_SVN_REPOS_PATH)
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
        'project-list': (project_list, None),
        'git-svn-init': (svn_run_for_repos, git_svn_init),
        'git-svn-fetch': (git_svn_fetch, None),
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
