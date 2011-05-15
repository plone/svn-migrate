Overview
========

This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

Setup
=====

You need to have libsvn-dev and qt-sqk installed for svn2git to be compiled.
Don't try this on a non-Linux OS, it's won't work.

Bootstrap the buildout::

  $ python2.7 bootstrap.py -d
  $ bin/buildout

Migrate
=======

We use a three-step process for the migration. First get local SVN mirrors of
all plone.org repositories (via svnsync or bootstrap with a svndump). Then for
a subset of projects create local git exports. Finally create Git clones of
the git exports, run cleanup actions on them and finally publish those to
Github.

The first step is extremely time consuming, but uses a sync approach, which
makes it possible to update the data by new commits. The second and third step
are destructive and require a `downtime` for the affected project.

Detailed steps
--------------

Prepare local SVN mirrors::

  $ bin/py do.py svn-init

Now sync the data, which will take some hours to days::

  $ bin/py do.py svn-sync

If you need to Ctrl-C the sync process, you might be greeted with an error
message next time::

  Failed to get lock on destination repos, currently held by...

You can get rid of the lock by calling::

  $ svn propdel svn:sync-lock --revprop -r 0 file://$PWD/repos/svn-mirror/<repo name>/

Next up we need to get a mapping of SVN to Github usernames::

  $ bin/py do.py svn-authors

TODO: Currently this creates a dummy list of usernames for all users that
committed data to any of the repositories. We only want to map the users that
committed to one of the affected projects. Maybe a helpful command is:
`git log --all --format='%aN' | sort -u`

Now we want to run the actual export::

  $ bin/py do.py svn-export

This will take about 15 minutes in total. After this is done we can prepare
cleaned up Git repositories::

  $ bin/py do.py git-copy

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
