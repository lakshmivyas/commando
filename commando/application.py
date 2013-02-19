# -*- coding: utf-8 -*-
"""
Declarative interface for argparse
"""
from argparse import ArgumentParser
from collections import namedtuple
from commando.util import getLoggerWithConsoleHandler

import logging

# pylint: disable-msg=R0903,C0103,C0301

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution('commando').version
except Exception:
    __version__ = 'unknown'

__all__ = [
    '__version__',
    'command',
    'subcommand',
    'param',
    'version',
    'store',
    'true',
    'false',
    'append',
    'const',
    'append_const',
    'Application'
]


class Commando(type):
    """
    Meta class that enables declarative command definitions
    """

    def __new__(mcs, name, bases, attrs):
        instance = super(Commando, mcs).__new__(mcs, name, bases, attrs)
        subcommands = []
        main_command = None
        main_parser = None

        # Collect commands based on decorators
        for member in attrs.itervalues():
            if hasattr(member, "command"):
                main_command = member
            elif hasattr(member, "subcommand"):
                subcommands.append(member)

        def add_arguments(func):
            params = getattr(func, 'params', [])
            for parameter in reversed(params):
                func.parser.add_argument(*parameter.args, **parameter.kwargs)

        def add_subparser(func):
            if getattr(func, 'parser', None):
                # Already initialized
                return
            if not func.parent:
                # Sub of main
                func.parent = main_command
            else:
                # Sub of something else
                if not getattr(func.parent, 'parser', None):
                    # Parser doesn't exist for the parent.
                    add_subparser(func.parent)
                if not getattr(func.parent, 'subparsers', None):
                    # Subparser collection doesn't exist for the parent.
                    func.parent.subparsers = func.parent.parser.add_subparsers()

            func.parser = func.parent.subparsers.add_parser(
                                                    *func.subcommand.args,
                                                    **func.subcommand.kwargs)
            add_arguments(func)

        if main_command:
            main_parser = ArgumentParser(*main_command.command.args,
                                        **main_command.command.kwargs)

            main_command.parser = main_parser
            add_arguments(main_command)

            if len(subcommands):
                main_command.subparsers = main_parser.add_subparsers()
                for sub in subcommands:
                    add_subparser(sub)

        for sub in subcommands:
            # Map the functions to the subparser actions
            if not getattr(sub, 'subparsers', None):
                # Only if there are no subcommands
                sub.parser.set_defaults(run=sub)

        instance.__main__ = main_command
        instance.__parser__ = main_parser

        return instance

values = namedtuple('__meta_values', 'args, kwargs')


class metarator(object):
    """
    A generic decorator that tags the decorated method with
    the passed in arguments for meta classes to process them.
    """

    def __init__(self, *args, **kwargs):
        self.values = values._make((args, kwargs))  # pylint: disable-msg=W0212

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

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.get('parent')
        try:
            del kwargs['parent']
        except KeyError:
            pass
        super(subcommand, self).__init__(*args, **kwargs)

    def __call__(self, func):
        func.parent = self.parent
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
        super(append_const, self).__init__(*args,
                                                action='append_const',
                                                **kwargs)


class Application(object):
    """
    Barebones base class for command line applications.
    """
    __metaclass__ = Commando

    def __init__(self, raise_exceptions=False, logger=None):
        self.raise_exceptions = raise_exceptions
        self.logger = logger or getLoggerWithConsoleHandler()

    def parse(self, argv):
        """
        Simple method that delegates to the ArgumentParser
        """
        return self.__parser__.parse_args(argv)  # pylint: disable-msg=E1101

    def run(self, args=None):
        """
        Runs the main command or sub command based on user input
        """

        if not args:
            import sys
            args = self.parse(sys.argv[1:])

        if getattr(args, 'verbose', False):
            self.logger.setLevel(logging.DEBUG)

        try:
            if hasattr(args, 'run'):
                args.run(self, args)
            else:
                self.__main__(args)  # pylint: disable-msg=E1101
        except Exception, e:
            if self.raise_exceptions:
                raise
            elif self.__parser__:
                self.__parser__.error(e.message)
            else:
                self.logger.error(e.message)
                return -1
