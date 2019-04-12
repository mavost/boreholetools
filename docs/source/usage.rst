Usage
*****

boreholetools is a collection of modules to QC geoscientific borehole data of various types.

Main features:

* convert/verify/interpolate well trajectory data, i.e. deviation surveys
* convert apparent bed dip/dip azimuth data referenced to a wellbore coordinate system into true bed dip/dip azimuth
* calculate true vertical/stratigraphic thickness of beds using a dip model

Default behavior unless specified otherwise:

* reads a list of well data in the form of CSV spread sheet files
* processes one or many well data in one iteration
* output generated will be another set of CSV files replacing the previous run

.. note:: Documentation in progress...

Getting Started
===============

Prerequisites
-------------
Only Python 3 standard library modules are used currently.

Installation
------------

1. Install Python version 3.6.3 or later
2. Clone the respective project repository from github::

    git clone https://github.com/mavost/boreholetools.git

3. Invoke a test run of all modules using no arguments and default input files residing in ``/data``::

    python boreholetools.py --testing

4. If testing run was successful a default run requires a number of keyword arguments for accessing the desired behavior and input files to support the processing::

    python boreholetools.py KEYWORDS

Function and Keyword Description
================================

The workflow of ``boreholetools`` is directed by operational keywords and parameters

Built With
==========
The project was developed using Python version 3.6.3 on a Windows 7 x64 machine.

Versioning
==========
We use `Git <http://git-scm.com/>`_ for versioning and `Sphinx <http://www.sphinx-doc.org/>`_ for documentation.
