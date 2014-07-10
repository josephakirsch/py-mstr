.. default-domain:: py

===============================================
py-mstr - MicroStrategy Task API package
===============================================

.. toctree::
    :maxdepth: 2
    
    index
    source/modules

Features:

- Browse folders
- View ``Attribute`` and ``Metric`` objects
- Execute a ``Report`` with or without ``Prompt`` objects


.. _tutorial

Tutorial
========


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

.. _execute-report

Executing a Report
==================


Report Prompts
--------------

Currently, py-mstr supports Elements Prompt Answers (the most common
type) and Value Prompt Answers.

Element Prompt Answers:
    
    This is the most common type of prompt. Typically, the MicroStrategy web interface displays it in a 
    shopping cart style where you select from a list of elements for an ``Attribute``.

Value Prompt Answers:

    These prompts are where the user types a value into a text box, or chooses
    a date from a calendar view. Filters are also answered this way. Note that
    order matters because the answers are passed in a list, and the prompts appear
    in the same order as they do in the web interface.


Refer to http://www.bryanbrandow.com/2011/08/answering-prompts-via-url-api.html
for more information about answering prompts via the api.

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

    value_answers = [(prompts[0], 'v1'), (prompts[2], 'v2')]
    # You can pass multiple answers to one element prompt by including all values
    # in the list for the prompt
    element_answers = {prompts[1]: ['v3', 'v4']}

You can pass no value for an optional parameter. The empty string for Value Prompt Answers 
signfies there should be no answer supplied.::
    
    value_answers = [(prompts[0], ''), (prompts[2], 'v2')]

For Element Prompt Answers, you pass an empty list as the value for the prompt
key.::

    element_answers = {prompts[1]: []}
    
Pagination
----------

The default number of rows to be returned is 100,000. This number
should be a default parameter that retrieves all rows in the report, because
currently the maximum number of rows in a MicroStrategy report is ~60K. Note,
however, that when there are a large number of columns in the row that it would be prudent 
to consider pagination, otherwise the api may return a Java out of memory stack trace. 

Here is an example paging through rows rather than returning all rows in
one call.::

    min_row = 0
    max_rows_returned = MAX_ROWS / 10
    for i in range(10):
        report.execute(start_row=min_row, max_rows=max_rows_returned)
        values = acv_report.get_values()
        # values will be null if there are no rows left
        if not values:
            break
        for row in values:
            for attr, val in row:
                print val
        min_row = (i + 1) * max_rows_returned
    return result

Installation
============

Install py-mstr through pip.::

    pip install py-mstr


Contribute
==========

- Source Code: https://github.com/infoscout/py-mstr

License
=======

py-mstr is licensed under the MIT license.


