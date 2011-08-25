
from argh import arg
from svnmigrate.config import Config


class API(object):
    """ Defines our command line commands
    """

    def __iter__(self):
        for i in ['sync', 'export', 'cleanup', 'publish']:
            yield getattr(self, i)

    #
    # COMMANDS
    #

    @arg('-p', '--projects-file', required=True)
    @arg('-R', '--svn-repos', default=None)
    def sync(self, args):
        """ Create svn mirror, if they don't exists, and sync svn repositories.
        """
        
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

    def export(self, projects_file):
        """
        """

    def cleanup(self, args):
        """
        """
        
    def publish(self, args):
        """
        """

    def status(self, args):
        """
        """



