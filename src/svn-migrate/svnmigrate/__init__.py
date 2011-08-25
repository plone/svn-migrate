
from argh import ArghParser
from svnmigrate.api import API


def main():
    parser = ArghParser()
    parser.add_commands(API())
    parser.dispatch()
