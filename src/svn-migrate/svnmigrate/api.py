
from argh import arg
from svnmigrate.config import Config
from svnmigrate.utils import header
from svnmigrate.utils import line


class API(object):
    """ Defines our command line commands
    """

    def __iter__(self):
        for i in ['sync', 'export', 'cleanup', 'publish', 'status']:
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
    @arg('-R', '--svn-repos', default=None)
    def export(self, args):
        """Export from svn-mirror to git repository"""

        config = Config(args.projects_file)
        if args.svn_repos is not None:
            svn_repos_to_process = args.svn_repos.split(';')
        else:
            svn_repos_to_process = [i.name for i in config.svn_repos]

        for svn_repo in config.svn_repos:
            if svn_repo.name in svn_repos_to_process:
                svn_repo.export()

    def cleanup(self, args):
        """"""
        
    def publish(self, args):
        """Publish repos to github"""

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



