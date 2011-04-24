Overview
========

This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

Setup
=====

Bootstrap the buildout::

  $ python2.6 bootstrap.py -d
  $ bin/buildout

Migrate
=======

We use a three-step process for the migration. First get local SVN mirrors of
all plone.org repositories (via svnsync or bootstrap with a svndump). Then for
a subset of projects create local git-svn mirrors. Finally create Git clones of
the git-svn mirrors, run cleanup actions on them and finally publish those to
Github.

The first two steps are extremely time consuming, but both use sync approaches,
which makes it possible to update them by new commits. Only the third step is
destructive and requires a `downtime` for the affected project.

Detailed steps
--------------

Prepare local SVN mirrors::

  $ bin/py do.py svn-init

Now sync the data, which will take some hours::

  $ bin/py do.py svn-sync

If you need to Ctrl-C the sync process, you might be greeted with an error
message next time::

  Failed to get lock on destination repos, currently held by...

You can get rid of the lock by calling::

  $ svn propdel svn:sync-lock --revprop -r 0 file://$PWD/repos/svn-mirror/<repo name>/

Next up we want to build the list of all projects we want to mirror::

  $ bin/py do.py project-list

And create empty git-svn mirrors for all projects::

  $ bin/py do.py git-svn-init

Now we need to get a mapping of SVN to Github usernames::

  $ bin/py do.py svn-authors

TODO: Currently this creates a dummy list of usernames for all users that
committed data to any of the repositories. We only want to map the users that
committed to one of the affected projects.

To finally fetch the data::

  $ bin/py do.py git-svn-fetch

Todo
----

Publish them to Github:

- Create Git repository
- Fix default Git repository settings (no issue tracker/wiki, teams)
- git push --all
- git push --tags

Remove from SVN:

- svn rm <svn base url>
