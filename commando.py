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

    @staticmethod
    def build_commands(commands, parent_func=None):
        for func in commands[parent_func]:
            if parent_func == None:
                # This is the main command
                func.parser = ArgumentParser(*func.command.args,
                                              **func.command.kwargs)
            else:
                func.parser = parent_func.subparser.add_parser(*func.command.args,
                                                                **func.command.kwargs)

            if hasattr(func, "params"):
                for param in func.params:
                    func.parser.add_argument(*param.args, **param.kwargs)

            # Check if func has children
            if func in commands:
                # It does, so create a subparser, and build subcommands
                func.subparser = func.parser.add_subparsers()
                Commando.build_commands(commands, func)
            else:
                func.parser.set_defaults(run=func)

    def __new__(mcs, name, bases, attrs):
        instance = super(Commando, mcs).__new__(mcs, name, bases, attrs)

        # This is a tree: key is the parent, value is the list of children
        # The key `None' points to a value which is a list of function that
        # is the command.
        # The special key "__main__" is used for @subcommand that have no parent defined.
        commands = {}

        for func in attrs.itervalues():
            if hasattr(func, "command"):
                if func.parent in commands:
                    commands[func.parent].append(func)
                else:
                    commands[func.parent] = [ func ]

        if commands:
            if None not in commands:
                raise Exception("No main command found.")
            elif len(commands[None]) > 1:
                raise Exception("Too much main command found", commands)

            # If there's a key __main__, that means some commands were added
            # with the @subcommand decorator, and without specifying the
            # parent, so we set the parent to be commands[None][0], meaning
            # the main command.
            if '__main__' in commands:
                main_command = commands[None][0]
                if main_command in commands:
                    commands[main_command].append(commands['__main__'])
                else:
                    commands[main_command] = commands['__main__']
                del commands['__main__']

            Commando.build_commands(commands)

            instance.__parser__ = commands[None][0].parser
            instance.__main__ = commands[None][0]

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
    Used to decorate the commands and subcommands
    """

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.get("parent")
        try:
            del kwargs['parent']
        except KeyError:
            pass
        super(command, self).__init__(*args, **kwargs)

    def __call__(self, func):
        setattr(func, "parent", self.parent)
        return self.metarate(func, name='command')


class subcommand(command):
    """
    Used to decorate the subcommands
    """

    def __init__(self, *args, **kwargs):
        kwargs['parent'] = kwargs.get("parent", '__main__')
        super(subcommand, self).__init__(*args, **kwargs)


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
