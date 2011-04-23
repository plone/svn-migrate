Overview
========

This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

Todo
----

...

Setup
=====

Bootstrap the buildout:

  $ python2.6 bootstrap.py -d
  $ bin/buildout

Prepare local SVN mirrors:

  $ bin/py prepare.py

This will take a long time, at least some hours.
