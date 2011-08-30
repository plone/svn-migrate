#!/bin/sh

svn-migrate export -p etc/projects.cfg -a authors.cfg -r $1 && svn-migrate cleanup -p etc/projects.cfg -r $1 && svn-migrate analyze -p etc/projects.cfg -r $1
