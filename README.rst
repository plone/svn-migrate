This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

.. contents::


Setup
=====

You need to have libsvn-dev, qmake and qt-sdk installed for svn2git to be
compiled. Don't try this on a non-Linux OS, it won't work.

We'll need SVN mirrors of all three plone.org repositories. This will take
about 13gb of space. The uncleaned Git exports take about 0.5gb and the final
result is about 100mb.

First install the OS package dependencies. Then bootstrap the buildout::

  $ python2.7 bootstrap.py -d
  $ bin/buildout


Migrate
=======

Above setup should get everything ready for ``bin/svn-migrate``.::

    usage: svn-migrate [-h] {sync,export,cleanup,publish,status} ...
    
    positional arguments:
      {sync,export,cleanup,publish,status}
        sync                Create svn mirror if they don't exist, and sync svn
                            repositories.
        export              Export from svn-mirror to git repository
        cleanup             Cleanup exported repositories
        publish             Publish repos to github
        status              Show status
    
    optional arguments:
      -h, --help            show this help message and exit


1. Prepare local SVN mirrors and sync the data. This will take some days to
   finish. But if you run it again at a later stage, it will only update missing 
   commits. So only the initial run is expensive.
    
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

2. Export from svn mirrors we created in the previous step to git.
   
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

3. Cleanup previusly exported repositories (remove needed branches not needed, tags, etc..).
   
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

        $ bin/svn-migrate publish -p etc/projects.cfg
   
    ::

        usage: svn-migrate publish [-h] -p PROJECTS_FILE -u USERNAME -t API_TOKEN
                                   [-r REPOS]
        
        optional arguments:
          -h, --help            show this help message and exit
          -p PROJECTS_FILE, --projects-file PROJECTS_FILE
          -u USERNAME, --username USERNAME
          -t API_TOKEN, --api-token API_TOKEN
          -r REPOS, --repos REPOS


5. There is also a status command that will show you in which state this
   package is.

    ::

        $ bin/svn-migrate status -p status

    ::

        usage: svn-migrate status [-h] [-p PROJECTS_FILE] [-r REPOS]
        
        optional arguments:
            -h, --help            show this help message and exit
            -p PROJECTS_FILE, --projects-file PROJECTS_FILE
            -r REPOS, --repos REPOS


Example
=======

I will give example of how to work on a single repository, write rules for it
and test it.

1. Pull out the repository prior to any work.

2. Make sure you synced it with the svn repository.

    ::

        $ svn-migrate sync

3. Open ``etc/projects.cfg`` and find a repository you want to work on (check their
   statuses). Then you write 'IN-PROGRESS (Your Name)' into the selected repo. now
   commit and push this so others see you are working on it.

4. Write rules for you project in a file that is referring from
   ``etc/projects.cfg`` ... example: for ``Products.Marshall``. You write rules into
   ``etc/rules/rules-Products.Marshall.cfg``

5. Once your rules are written export them and cleanup git repository

    ::

        $ svn-migrate export -r Products.Marshall
        $ svn-migrate cleanup -r Products.Marshall

    When using the ``-r`` option, you will only run rules and cleanup for the
    selected repository. if you want to run it more repositories then separate them
    with ``;``. if the ``-r`` flag is skipped it will run for all repos defined in
    ``etc/projects.cfg`` file.

6. Analyze if the migration has been successful.

    ::

        $ svn-migrate analyze -r Products.Marshall

    This script will:
        - check if tags and branches are the same and if not it will display the
          difference
        - run ``diff`` command on all existing branches/tags in svn and compare
          them with their git equivalents.


    If error occur go back to step number 3 and try to fix the rules.

    If you have no errors, proceed.

7. After the project is ready, mark it as completed so I and others know that no
   work is needed on this.

    This meaning: open ``etc/projects.cfg``, find your repository you were migrating
    and change status to WORKS-FOR-ME (giving reasons why you think its ok) or
    COMPLETED (meaning that no error apeared during the analyze step)

8. Publish to github. (only if you have rights to create repositories on
   github.com/plone)

    ::

        WARNING! ACHTUNG!!

        it will ask you whether you want to delete the repository prior to pushing it
        to github. But I'm warning you here again that with publishing the repository
        to github it will delete it before publishing it. There, I said it again.

    ::

        $ svn-migrate publish -r Products.Marshall



TODO (for garbas): we need to also test this with ``plone-coredev``


Where to search for help
========================

Write more svn2git rules, examples and docs at:

- http://gitorious.org/svn2git/svn2git/trees/master/samples
- http://gitorious.org/svn2git/kde-ruleset/trees/master
- http://techbase.kde.org/Projects/MoveToGit/UsingSvn2Git

Especially this remark::

  Also try grepping the output from svn2git for the string '"copy from"'
  (with the double quotation marks). This will give you a list of
  revisions/paths that svn2git could not detect the origin of. That happens
  if someone did a svn cp/mv and the old path is not in the generated git
  repository.

Validate the Git data:

- run setup.py sdist on tags and compare to pypi uploads
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
