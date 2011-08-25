
import os
import ConfigParser
from svnmigrate.models import Repo
from svnmigrate.models import SvnRepo
from svnmigrate.utils import call
from svnmigrate.utils import path


class Config(object):

    def __init__(self, projects_file):
        self._raw = ConfigParser.SafeConfigParser({
                'here': path(os.path.dirname(projects_file)),
                })
        self._raw.read(path(projects_file))
        

    @property
    def svn_repos(self):
        for item in self._raw.get('base', 'svn-repos').split('\n'):
            item = item.strip()
            if not item:
                continue
            yield SvnRepo(self, *item.split(' '))

    @property
    def svn_mirror(self):
        svn_mirror = path(self._raw.get('base', 'svn-mirror-location'))
        if not os.path.isdir(svn_mirror):
            call('mkdir -p %s' % svn_mirror)
        return svn_mirror

    @property
    def svn_export(self):
        svn_export = path(self._raw.get('base', 'svn-export-location'))
        if not os.path.isdir(svn_export):
            call('mkdir -p %s' % svn_export)
        return svn_export

    @property
    def git_cleaned(self):
        git_cleaned = path(self._raw.get('base', 'git-cleaned-location'))
        if not os.path.isdir(git_cleaned):
            call('mkdir -p %s' % git_cleaned)
        return git_cleaned

    @property
    def repos(self):
        for section in self._raw.sections():
            if not section.startswith('repo:'):
                continue
            options = dict()
            for option in self._raw.options(section):
                options[option.replace('-', '_')] = self._raw.get(section, option)
            yield Repo(self, section[5:], **options)
