============================
commando - argparse in style
============================

**Version 0.3a**

A simple wrapper for ``argparse`` that allows commands and arguments
to be defined declaratively using decorators. Note that this does
not support all the features of ``argparse`` yet.

Commando also bundles a few utilities that are useful when building 
command line applications.

Example
--------

Without commando::


    def main():
        parser = argparse.ArgumentParser(description='hyde - a python static website generator',
                                      epilog='Use %(prog)s {command} -h to get help on individual commands')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
        parser.add_argument('-s', '--sitepath', action='store', default='.', help="Location of the hyde site")
        subcommands = parser.add_subparsers(title="Hyde commands",
                                         description="Entry points for hyde")
        init_command = subcommands.add_parser('init', help='Create a new hyde site')
        init_command.set_defaults(run=init)
        init_command.add_argument('-t', '--template', action='store', default='basic', dest='template',
                         help='Overwrite the current site if it exists')
        init_command.add_argument('-f', '--force', action='store_true', default=False, dest='force',
                         help='Overwrite the current site if it exists')
        args = parser.parse_args()
        args.run(args)

    def init(self, params):
        print params.sitepath
        print params.template
        print params.overwrite


With commando::


    class Engine(Application):

        @command(description='hyde - a python static website generator',
                epilog='Use %(prog)s {command} -h to get help on individual commands')
        @param('-v', '--version', action='version', version='%(prog)s ' + __version__)
        @param('-s', '--sitepath', action='store', default='.', help="Location of the hyde site")
        def main(self, params): pass

        @subcommand('init', help='Create a new hyde site')
        @param('-t', '--template', action='store', default='basic', dest='template',
                help='Overwrite the current site if it exists')
        @param('-f', '--force', action='store_true', default=False, dest='overwrite',
                help='Overwrite the current site if it exists')
        def init(self, params):
            print params.sitepath
            print params.template
            print params.overwrite

Resources
---------

1.  `Changelog`_
2.  `License`_
3.  `Contributing`_
4.  `Authors`_


.. _Changelog: CHANGELOG.rst
.. _LICENSE: LICENSE
.. _Contributing: CONTRIBUTING.rst
.. _Authors: AUTHORS.rst

