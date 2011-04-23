Overview
========

This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

Todo
----

...

Setup
=====

Bootstrap the buildout::

  $ python2.6 bootstrap.py -d
  $ bin/buildout

Prepare local SVN mirrors::

  $ bin/py do.py svn-init

Now sync the data, which will take some hours::

  $ bin/py do.py svn-sync
