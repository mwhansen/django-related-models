========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/django-related-models/badge/?style=flat
    :target: https://readthedocs.org/projects/django-related-models
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/roverdotcom/django-related-models.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/roverdotcom/django-related-models

.. |codecov| image:: https://codecov.io/github/roverdotcom/django-related-models/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/roverdotcom/django-related-models

.. |version| image:: https://img.shields.io/pypi/v/django-related-models.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/django-related-models

.. |commits-since| image:: https://img.shields.io/github/commits-since/roverdotcom/django-related-models/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/roverdotcom/django-related-models/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/django-related-models.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/django-related-models

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/django-related-models.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/django-related-models

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/django-related-models.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/django-related-models


.. end-badges

A library designed such that, when provided with a model instance it will return a QuerySet for the rows that are
associated with that model instance.

* Free software: BSD 3-Clause License

Installation
============

::

    pip install django-related-models

Documentation
=============

https://django-related-models.readthedocs.io/

Development
===========

To run the all tests run::

    tox
