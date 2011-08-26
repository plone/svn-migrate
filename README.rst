Overview
========

This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

Setup
=====

You need to have libsvn-dev, qmake and qt-sqk installed for svn2git to be
compiled. Don't try this on a non-Linux OS, it won't work.

We'll need SVN mirrors of all three plone.org repositories. This will take
about 13gb of space. The uncleaned Git exports take about 0.5gb and the final
result only ways in at about 100mb.

First install the OS package dependencies. Then bootstrap the buildout::

  $ python2.7 bootstrap.py -d
  $ bin/buildout

Migrate
=======

Above setup should get you ready everything for ``bin/svn-migrate``.::

    usage: svn-migrate [-h] {sync,export,cleanup,publish,status} ...
    
    positional arguments:
      {sync,export,cleanup,publish,status}
        sync                Create svn mirror, if they don't exists, and sync svn
                            repositories.
        export              Export from svn-mirror to git repository
        cleanup             Cleanup exported repositories.
        publish             Publish repos to github
        status              Show status
    
    optional arguments:
      -h, --help            show this help message and exit


1. Prepare local SVN mirrors and sync the data, which will take some days to
   finish. But if you run afterwards it will only update missing commits. So
   only initial run is exspensive.
    
    ::

        $ bin/svn-migrate sync -p etc/projects.cfg

    ::

        usage: svn-migrate sync [-h] -p PROJECTS_FILE [-R SVN_REPOS]

        optional arguments:
          -h, --help            show this help message and exit
          -p PROJECTS_FILE, --projects-file PROJECTS_FILE
          -R SVN_REPOS, --svn-repos SVN_REPOS

    If you need to Ctrl-C the sync process, you might be greeted with an error
    message next time.::
    
        Failed to get lock on destination repos, currently held by...

    You can get rid of the lock by calling.::

        $ svn propdel svn:sync-lock --revprop -r 0 file://$PWD/repos/svn-mirror/<repo name>/

2. Export from svn mirrors we created in previous step to git.
   
    ::
    
        $ bin/svn-migrate export -p etc/projects.cfg -a authors.cfg

    ::

        usage: svn-migrate export [-h] -p PROJECTS_FILE -a AUTHORS_FILE [-R SVN_REPOS]
                                  [-r REPOS]
        
        optional arguments:
          -h, --help            show this help message and exit
          -p PROJECTS_FILE, --projects-file PROJECTS_FILE
          -a AUTHORS_FILE, --authors-file AUTHORS_FILE
          -R SVN_REPOS, --svn-repos SVN_REPOS
          -r REPOS, --repos REPOS

3. Cleanup previusly exported repositories (remove not not needed branches, tags, etc..).
   
    ::

        $ bin/svn-migrate cleanup -p etc/projects.cfg

    ::

        usage: svn-migrate cleanup [-h] -p PROJECTS_FILE [-r REPOS]
        
        optional arguments:
          -h, --help            show this help message and exit
          -p PROJECTS_FILE, --projects-file PROJECTS_FILE
          -r REPOS, --repos REPOS


4. Publish repos to new location (github.com/plone).
   
    ::

        $ bin/svn-migrate publish
   
    ::

        usage: svn-migrate publish [-h] -p PROJECTS_FILE -u USERNAME -t API_TOKEN
                                   [-r REPOS]
        
        optional arguments:
          -h, --help            show this help message and exit
          -p PROJECTS_FILE, --projects-file PROJECTS_FILE
          -u USERNAME, --username USERNAME
          -t API_TOKEN, --api-token API_TOKEN
          -r REPOS, --repos REPOS

Todo
----

Write more svn2git rules, examples and docs at:

- http://gitorious.org/svn2git/svn2git/trees/master/samples
- http://gitorious.org/svn2git/kde-ruleset/trees/master
- http://techbase.kde.org/Projects/MoveToGit/UsingSvn2Git

Especially this remark::

  Also try grepping the output from svn2git for the string '"copy from"'
  (with the double quotation marks). This will give you a list of
  revisions/paths that svn2git could not detect the origin of. That is
  someone did a svn cp/mv and the old path is not in the generated git
  repository.

Validate the Git data:

- run setup.py sdist on tags and compare to pypi uploads?
- check number of tags / branches
- `diff -ur` trunk / master and tags?

Publish Git repos to Github:

- Create Git repository
- Fix default Git repository settings (no issue tracker/wiki, teams)
- git push --all
- git push --tags

Look at http://pypi.python.org/pypi/github2 for talking to the Github API.

Remove from SVN:

- svn rm <svn base url>
