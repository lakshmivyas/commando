Version 0.3a
--------------

Thanks to `Julien Danjou`_ :

-   Add support for nested sub commands. 
    {0e26a6fe2571accb78d26318ab1b8dc65636d2b0}. (Pull #7)

Version 0.2.1a
--------------

Thanks to `Ben West`_ :

-   Allow commands to have no params.

Version 0.2a
--------------

-   Bundle various frequently used utilities with commando.
    (``ShellCommand``, ``ConfigDict``, ``autoprop`` and logging helpers).
    {63525646bb366f4def3c5065a51a404b18269873}. (Pull #4)


Version 0.1.3a
--------------

-   Commando must consume exceptions by default. Any exception should be
    communicated in a friendly manner to the user via the parser or the
    given logger. {0e26a6fe2571accb78d26318ab1b8dc65636d2b0}.

Version 0.1.2a
---------------

Thanks to `Brandon Philips`_ :

-   Use ``distribute_setup.py``.
-   Derive version from ``pkg_resources``.
-   Add ``argparse`` as a dependency.

Version 0.1.1a
---------------

-   Add more decorators that map to argparse parameters.

Version 0.1a
------------

-   Create a simple meta programmed wrapper around ``argparse``.

.. _Lakshmi Vyas: https://github.com/lakshmivyas
.. _Brandon Philips: https://github.com/philips
.. _Ben West: https://github.com/bewest
.. _Julien Danjou: https://github.com/jd