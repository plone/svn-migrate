Overview
========

This repository contains scripts and docs to migrate Plone Core from Subversion
to Github.

Setup
=====

We assume debian system.

First we clone this svn-migrate project.

::

    ~/ % git clone git://github.com/plone/svn-migrate.git
    ~/ % cd svn-migrate

Next we create virtualenv and bootstrap environment. Use python 2.7 since I
didn't test with other versions.

::

    ~/svn-migrate % virtualenv-2.7 --no-site-packages 
    ~/svn-migrate % . bin/activate
    (svn-migrate) ~/svn-migrate % pip install -r requirements.txt

Install svn2git.

::

    (svn-migrate) ~/svn-migrate % sudo apt-get install git-core git-svn ruby rubygems
    (svn-migrate) ~/svn-migrate % sudo gem install svn2git --source http://gemcutter.org


Migrate
=======

#TODO: need to rewrite this section
We use a three-step process for the migration. First get local SVN mirrors of
all plone.org repositories (via svnsync or bootstrap with a svndump). Then for
a subset of projects create local git exports. Finally create copies of the
Git exports, run cleanup actions on them and finally publish those to Github.

The first step is extremely time consuming. If you don't have a svndump it will
take several days depending on your network connection and the load on the
plone.org servers. But this step uses a sync approach, so you can update the
data by new commits. The second and third step are destructive and require a
`downtime/freeze` for the affected project.

Detailed steps
--------------

1. Prepare local SVN mirrors and sync the data, which will take some days to
finish. But if you run afterwards it will only update missing commits. So
only initial run is exspensive.::

    (svn-migrate) ~/svn-migrate % ./migrate sync

If you need to Ctrl-C the sync process, you might be greeted with an error
message next time.::

  Failed to get lock on destination repos, currently held by...

You can get rid of the lock by calling.::

  $ svn propdel svn:sync-lock --revprop -r 0 file://$PWD/repos/svn-mirror/<repo name>/

4. Get authors from svn projects (via plone's ldap). Migrate to new git
repositories or if this is not the first time, also update/rebase git
repositories with changes from svn.::

    (svn-migrate) ~/svn-migrate % ./migrate mirror

5. Publish repos to new location (github.com/plone).::

    (svn-migrate) ~/svn-migrate % ./migrate publish



