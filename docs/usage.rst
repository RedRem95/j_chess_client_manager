=====
Usage
=====

Implement your AI by implementing the AI class from j-chess-lib_. See `j-chess-lib Usage`_ for usage instructions.

Then install the bot manager using

.. code-block::

    $pip install j_chess_bot_manager

Then start the manager by calling

.. code-block::

    $j_chess_client_manager --with-package to.your.package

Where ``to.your.package`` should be the import statement to the package/pythonfile with your implemented ai from the
current working directory.

Use

.. code-block::

    $j_chess_client_manager --help

to see all available options

.. _j-chess-lib: https://github.com/RedRem95/j-chess-lib
.. _`j-chess-lib Usage`: https://j-chess-lib.readthedocs.io/en/latest/usage.html
