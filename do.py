import argparse
import ConfigParser
import os
import os.path
import urllib2

REPOS = ('archetypes', 'collective', 'plone')
REMOTE_SVN_BASE = 'http://svn.plone.org/svn/'
SOURCES_URL = 'http://svn.plone.org/svn/plone/buildouts/plone-coredev/' \
    'branches/4.1/sources.cfg'

cwd = os.path.abspath(os.curdir)
repos_path = os.path.join(cwd, 'repos', 'svn-mirror')

parser = argparse.ArgumentParser(description='Do stuff!')
parser.add_argument('command', choices=[
    'svn-init', 'svn-sync', 'project-list'])


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


def svn_run_for_repos(func):
    for repo in REPOS:
        repo_path = os.path.join(repos_path, repo)
        repo_url = 'file://' + repo_path
        func(repo, repo_path, repo_url)


def project_list():
    resource = urllib2.urlopen(SOURCES_URL, timeout=10)
    sources_path = os.path.join(cwd, 'sources-4.1.cfg')
    with open(sources_path, 'w') as fd:
        fd.write(resource.read())

    config = ConfigParser.RawConfigParser()
    config.optionxform = lambda s: s
    config.read(sources_path)

    items = config.items('sources')
    projects = {}
    for repo in REPOS:
        projects[repo] = []
    base = 'https://svn.plone.org/svn/'
    plone_items = [(k, v.lstrip('svn ')) for k, v in items
        if v.startswith('svn ' + base)]

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

    projects_path = os.path.join(cwd, 'projects.cfg')

    config = ConfigParser.RawConfigParser()
    config.optionxform = lambda s: s

    for repo, values in projects.items():
        config.add_section(repo)
        for k, v in values:
            config.set(repo, k, v)

    with open(projects_path, 'w') as fd:
        config.write(fd)


def main():
    commands = {
        'svn-init': (svn_run_for_repos, svn_init),
        'svn-sync': (svn_run_for_repos, svn_sync),
        'project-list': (project_list, None),
    }

    arguments = parser.parse_args()
    command, argument = commands.get(arguments.command)
    if argument is None:
        command()
    else:
        command(argument)


if __name__ == '__main__':
    main()
