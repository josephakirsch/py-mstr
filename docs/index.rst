.. default-domain:: py

===============================================
py-mstr - A MicroStrategy Task Proc Api package
===============================================

Features:

- Browse folders
- View ``Attribute`` and ``Metric`` objects
- Execute a ``Report`` with or without ``Prompt`` objects


.. _classes

Classes in py-mstr
==================

py-mstr is made up of multiple classes encapsulating different objects used
by MicroStrategy. These include
    
    - MstrClient
    - Attribute
    - Metric
    - Prompt
    - Report

MstrClient
----------
``MstrClient`` encapsulates the login, session, and logout logic for your project.


Public Methods:
    
    - ``get_folder_contents``
    - ``get_attribute``
    - ``list_elements``

Report
------
``Report`` encapsulates a report object. The most useful method will be the
use cases for ``execute``.

Public Methods:

    - ``get_prompts``
    - ``get_attributes``
    - ``execute``

The following may only be called once a report has been executed:

    - ``get_headers``
    - ``get_metrics``
    - ``get_values``


Prompt
------

A ``Prompt`` can take many forms. The supported prompt types are:

    - Element Prompt Answers
    - Value Prompt Answers

Element Prompt Answers:
    
    This is the most common type of prompt. Typically, the MicroStrategy web interface displays it in a shopping cart style where you select from a list of elements for an ``Attribute``.

Value Prompt Answers:

    These prompts are where the user types a value into a text box, or chooses
    a date from a calendar view. Filters are also answered this way. Note that
    order matters because the answers are passed in a list, and the prompts appear
    in the same order as they do in the web interface.


Refer to http://www.bryanbrandow.com/2011/08/answering-prompts-via-url-api.html
for more information about answering prompts via the api.

Attribute
---------

``Attribute`` objects are used in prompts, filters, and in columns for reports.
They are also essential to ``elements_prompt_answers`` prompts when executing
a ``Report``


Accessible instance variables:
    - ``guid``
    - ``name``

Metric
------

This class takes the same structure as ``Attribute``. A different class was created
to allow the client to determine what the type of each column in a ``Report`` is.

Accessible instance variables:
    - ``guid``
    - ``name``

Singleton
---------

Both ``Attribute`` and ``Metric`` have the defined ``Singleton`` class as their
``__metaclass__``. This ensures that ``Attribute`` objects with the same guid
are the same object, thus saving memory. The same applies to the ``Metric``
object. The ``Singleton`` class is based of the ``guid`` instance variable.


.. _tutorial

Tutorial
========

``pip install py-mstr``

Here is a sample use case of the api::

    from py_mstr import MstrClient
   
    BASE_URL = 'http://insights.infoscout.co/MicroStrategy/asp/TaskProc.aspx?"'
    USERNAME = 'johndoe'
    PASSWORD = 'password'
    PROJECT_SOURCE = 'ip-0AB4D138'
    PROJECT_NAME = 'MicroStrategy Tutorial Project'

    client = MstrClient(base_url=BASE_URL, username=MSTR_USERNAME,
        password=MSTR_PASSWORD, project_source=MSTR_PROJECT_SOURCE, project_name=MSTR_PROJECT_NAME)


View folder contents. Specify a folder guid to view the contents of a specific
folder. Otherwise, the contents of the base folder of the ``PROJECT_NAME`` will be returned::
    
    base_folder_contents = client.get_folder_contents()
    print 'There are %s folders in the base folder' % len(base_folder_contents)
    
    folder_contents = client.get_folder_contents(folder_id='parent_folder_guid')
    for f in folder_contents:
        print 'Folder: name - %s description - %s guid - %s type - %s' % (f['name'], f['description'], f['id'], f['type'])

Get the corresponding ``Attribute`` object from an ``attribute_id``. See ``Attribute`` section for details::
    
    attr = client.get_attribute('attribute_guid')
    print attr


List the values an ``attribute_id`` can take. Note that this call is prone to failure by the MicroStrategy Task Api. If an attribute id has a very large number of values,
a java stack trace is returned. py-mstr currently responds to this case by returning an empty list::

    elements = client.list_elements(attr.guid)
    for e in elements:
        print element


Get a ``Report`` and execute.::

    report = client.get_report('report_guid')
    report.execute()
    headers = report.get_headers()
    for header in headers:
        print header
    
    # metrics and attributes are together the headers
    metrics = report.get_metrics()
    attributes = report.get_attributes()

    # row is a list of tuples for each column
    for row in report.get_values():
        # the tuples for each column represent the header ``Attribute`` or 
        # ``Metric`` and the value
        for attr, val in row:
            print val

.. _execute-prompts

Understanding Report Execution Prompts
======================================

Currently, py-mstr supports Elements Prompt Answers (the most common
type) and Value Prompt Answers.

The user must understand what types of prompts make up the report
they wish to execute, so that there is a correct matching of ``Prompt``
objects to values. Prompts will be returned in the order that they are
listed in the web interface, making it easier to expect what prompts belong
with what values::

 prompts = report.get_prompts()

    for prompt in prompts:
        if prompt.attribute:
            print 'Prompt is an Elements Prompt Answer'
        else:
            print 'Prompt is a Value Prompt Answer'


    value_answers = ['v1', 'v2']
    

Installation
============

Install py-mstr by:


Contribute
==========

- Source Code: https://github.com/infoscout/py-mstr

License
=======

    py-mstr is licensed under the MIT license.


