Overview
========

This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

Setup
=====

Bootstrap the buildout::

  $ python2.6 bootstrap.py -d
  $ bin/buildout

Prepare local SVN mirrors::

  $ bin/py do.py svn-init

Migrate
=======

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

To finally fetch the data::

  $ bin/py do.py git-svn-fetch
