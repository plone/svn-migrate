
import os
import github2
from argh import arg
from github2.client import Github
from svnmigrate.config import Config
from svnmigrate.utils import header
from svnmigrate.utils import line
from svnmigrate.utils import path
from svnmigrate.utils import call


class API(object):
    """ Defines our command line commands
    """

    def __iter__(self):
        for i in ['sync', 'export', 'cleanup', 'publish', 'analyze', 'status']:
            yield getattr(self, i)

    #
    # COMMANDS
    #

    @arg('-p', '--projects-file', required=True)
    @arg('-R', '--svn-repos', default=None)
    def sync(self, args):
        """Create svn mirror, if they don't exists, and sync svn repositories."""
        
        config = Config(args.projects_file)
        if args.svn_repos is not None:
            svn_repos_to_process = args.svn_repos.split(';')
        else:
            svn_repos_to_process = [i.name for i in config.svn_repos]

        for svn_repo in config.svn_repos:
            if svn_repo.name in svn_repos_to_process:
                svn_repo.initialize()

        for svn_repo in config.svn_repos:
            if svn_repo.name in svn_repos_to_process:
                svn_repo.sync()

    @arg('-p', '--projects-file', required=True)
    @arg('-a', '--authors-file', required=True)
    @arg('-R', '--svn-repos', default=None)
    @arg('-r', '--repos', default=None)
    def export(self, args):
        """Export from svn-mirror to git repository"""

        config = Config(args.projects_file)
        if args.svn_repos is not None:
            svn_repos_to_process = args.svn_repos.split(';')
        else:
            svn_repos_to_process = [i.name for i in config.svn_repos]

        for svn_repo in config.svn_repos:
            if svn_repo.name in svn_repos_to_process:
                svn_repo.export(path(args.authors_file), args.repos)


    @arg('-p', '--projects-file', required=True)
    @arg('-r', '--repos', default=None)
    def cleanup(self, args):
        """Cleanup exported repositories."""

        config = Config(args.projects_file)
        for repo in config.get_repos():
            if args.repos is None or \
               repo.name in args.repos.split(';'):
                repo.cleanup()

    @arg('-p', '--projects-file', required=True)
    @arg('-u', '--username', required=True)
    @arg('-t', '--api-token', required=True)
    @arg('-r', '--repos', default=None)
    def publish(self, args):
        """Publish repos to github"""

        #import logging
        #logging.basicConfig(level=logging.DEBUG)

        gh = Github(username=args.username, api_token=args.api_token)
        gh_repos = dict()
        for repo in gh.organizations.repositories('plone'):
            gh_repos[repo.name] = repo

        config = Config(args.projects_file)
        for repo in config.get_repos():
            if args.repos is None or \
               repo.name in args.repos.split(';'):
                repo.publish(gh, gh_repos)

    @arg('-p', '--projects-file', required=True)
    @arg('-r', '--repos', default=None)
    def analyze(self, args):
        """Analyze repos if they were migrated successfuly."""

        config = Config(args.projects_file)

        for repo in config.get_repos():
            if args.repos is None or \
               repo.name in args.repos.split(';'):
                repo.analyze()

        call('rm -rf %s' % config.analyze_path)

    @arg('-p', '--projects-file', required=True)
    @arg('-r', '--repos', default=None)
    def status(self, args):
        """Show status"""
        config = Config(args.projects_file)
        if args.repos is not None:
            repos_to_process = args.repos.split(';')
        else:
            repos_to_process = [i.name for i in config.repos]

        header('Status report')
        for repo in config.repos:
            if repo.name in repos_to_process:
                line('%s: %s' % (repo.name, repo.status))



