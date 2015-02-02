MlabPy - Mathlab frontend for Python
====================================

With this project I just tried to see whether it would be possible to run your
matlab scripts on the Python engine - now you can!


Requirements
------------

MlabPy needs the following to run:

- Python 3.4
- numpy 1.9
- ply 3.4

The following packages are also recommended:

- scipy 1.9


Installation
------------

Either install mlabpy using pip:

::

	pip3 install mplabpy

You can also download a packaged version. To install it, run:

::

	python3 setup.py install


Quickstart
----------

MlabPy can operation in three modes: module loader, stand alone and interactive.


Module loader
~~~~~~~~~~~~~

MlabPy can be configured to automatically import matlab-Files just as it were
Python modules. To enable this feature, you have to call
``mlabpy.loader.enable_matlab_import`` before you use this feature.

You can add this call to the ``__init__.py`` of the package containing your
matlab-Files. This way, you do not have to bother about when it's called.
However, as the creation of the parser takes some time (see parsetab issue
below), this might lead to slow downs of your program.


Stand alone
~~~~~~~~~~~

You can execute matlab-Files using the mlabpy command line tool:

::

    mlabpy file.m

If there is a function ``main`` defined, it will be executed.


Interactive
~~~~~~~~~~~

If you do not pass any files to the command line tool, an interactive shell will
be started. *The shell is currently VERY rudimentary.*


Fine tuning and debugging
-------------------------

There are several possibilities to adjust the behavior of MlabPy. Most important
is the automatic module import.


Automatic module import
~~~~~~~~~~~~~~~~~~~~~~~

MlabPy comes with an extensible runtime. It mainly enables you to import the
complete namespace of a module into your matlab environment. There are some
runtime extensions which are required and automatically imported. Those are
``mlabpy.runtime.core`` which provides basic functionality such as data types
and NumPy bindings. ``mlabpy.runtime.scipy`` is responsible for the optional
SciPy bindings.

You can extend the list modules that should be imported by simply adding their
full dotted name to ``mlabpy.autoload``. If you run the command line tool, you
can use the ``-u`` or ``--use`` option to add modules to that list.
Additionally, you can store a comma separated list of modules in the envrionment
variable ``MLABPY_AUTOLOAD``.


Debug output
~~~~~~~~~~~~

If you set ``mlabpy.loader.OUTPUT_TREE`` to ``True``, the Python AST will be
written to a ``.ast`` file next to the matlab-File.


History
-------

I used the great work of Victor Leikehman he has done with smop_ as a starting
point. Especially the lexer and paser modules were of great help. I changed the
parser to produce and Python AST which was surprisingly straight forward.

AFter successfully parsing my first matlab files, I started to collect some
"patches" in ``mlabpy.runtime`` to account for all the small differences...
Ideally, this wrapper layer should be replaced by patching the AST.

.. _smop: https://github.com/victorlei/smop


TODO
----

- Parse tab is generated every startup, very slow!
- Non-conforming syntax trees and grammar defects.

  - Copy-on-assign?
  - Slices.

- Some glitches in the docs.
