# -*- coding: utf-8 -*-
"""
Declarative interface for argparse
"""
from argparse import ArgumentParser
from collections import namedtuple

# pylint: disable-msg=R0903,C0103,C0301

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution('commando').version
except Exception:
    __version__ = 'unknown'

__all__ = ['command',
           'subcommand',
           'param',
           'version',
           'store',
           'true',
           'false',
           'append',
           'const',
           'append_const',
           'Application']

class Commando(type):
    """
    Meta class that enables declarative command definitions
    """

    def __new__(mcs, name, bases, attrs):
        instance = super(Commando, mcs).__new__(mcs, name, bases, attrs)
        subcommands = []
        main_command = None
        for name, member in attrs.iteritems():
            if hasattr(member, "command"):
                main_command = member
            elif hasattr(member, "subcommand"):
                subcommands.append(member)
        main_parser = None

        def add_arguments(parser, params):
            """
            Adds parameters to the parser
            """
            for parameter in params:
                parser.add_argument(*parameter.args, **parameter.kwargs)

        if main_command:
            main_parser = ArgumentParser(*main_command.command.args,
                                        **main_command.command.kwargs)
            add_arguments(main_parser, getattr(main_command, 'params', []))
            subparsers = None
            if len(subcommands):
                subparsers = main_parser.add_subparsers()
                for sub in subcommands:
                    parser = subparsers.add_parser(*sub.subcommand.args,
                                                  **sub.subcommand.kwargs)
                    parser.set_defaults(run=sub)
                    add_arguments(parser, getattr(sub, 'params', []))

        instance.__parser__ = main_parser
        instance.__main__ = main_command
        return instance

values = namedtuple('__meta_values', 'args, kwargs')


class metarator(object):
    """
    A generic decorator that tags the decorated method with
    the passed in arguments for meta classes to process them.
    """

    def __init__(self, *args, **kwargs):
        self.values = values._make((args, kwargs)) #pylint: disable-msg=W0212

    def metarate(self, func, name='values'):
        """
        Set the values object to the function object's namespace
        """
        setattr(func, name, self.values)
        return func

    def __call__(self, func):
        return self.metarate(func)


class command(metarator):
    """
    Used to decorate the main entry point
    """

    def __call__(self, func):
        return self.metarate(func, name='command')


class subcommand(metarator):
    """
    Used to decorate the subcommands
    """

    def __call__(self, func):
        return self.metarate(func, name='subcommand')


class param(metarator):
    """
    Use this decorator instead of `ArgumentParser.add_argument`.
    """

    def __call__(self, func):
        func.params = func.params if hasattr(func, 'params') else []
        func.params.append(self.values)
        return func


class version(param):
    """
    Use this decorator for adding the version argument.
    """

    def __init__(self, *args, **kwargs):
        super(version, self).__init__(*args, action='version', **kwargs)

class store(param):
    """
    Use this decorator for adding the simple params that store data.
    """

    def __init__(self, *args, **kwargs):
        super(store, self).__init__(*args, action='store', **kwargs)

class true(param):
    """
    Use this decorator as a substitute for 'store_true' action.
    """

    def __init__(self, *args, **kwargs):
        super(true, self).__init__(*args, action='store_true', **kwargs)

class false(param):
    """
    Use this decorator as a substitute for 'store_false' action.
    """

    def __init__(self, *args, **kwargs):
        super(false, self).__init__(*args, action='store_false', **kwargs)

class const(param):
    """
    Use this decorator as a substitute for 'store_const' action.
    """

    def __init__(self, *args, **kwargs):
        super(const, self).__init__(*args, action='store_const', **kwargs)

class append(param):
    """
    Use this decorator as a substitute for 'append' action.
    """

    def __init__(self, *args, **kwargs):
        super(append, self).__init__(*args, action='append', **kwargs)

class append_const(param):
    """
    Use this decorator as a substitute for 'append_const' action.
    """

    def __init__(self, *args, **kwargs):
        super(append_const, self).__init__(*args, action='append_const', **kwargs)

class Application(object):
    """
    Barebones base class for command line applications.
    """
    __metaclass__ = Commando

    def parse(self, argv):
        """
        Simple method that delegates to the ArgumentParser
        """
        return self.__parser__.parse_args(argv) #pylint: disable-msg=E1101

    def run(self, args=None):
        """
        Runs the main command or sub command based on user input
        """

        if not args:
            import sys
            args = self.parse(sys.argv[1:])

        if hasattr(args, 'run'):
            args.run(self, args)
        else:
            self.__main__(args)  #pylint: disable-msg=E1101
