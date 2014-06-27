import urllib
import requests
import logging

from pyquery import PyQuery as pq

""" This API only supports xml format, as it relies on the format for parsing
    the data into python data structures
"""
BASE_PARAMS = {'taskEnv': 'xml', 'taskContentType': 'xml'}
BASE_URL = 'http://hostname/MicroStrategy/asp/TaskProc.aspx?'
logger = logging.getLogger(__name__)

class MstrClient(object):
    
    def __init__(self, base_url, username, password, project_source,
            project_name):
        
        self._base_url = base_url
        self._session = self._login(project_source, project_name,
                username, password)

    def __del__(self):
        self._logout()

    def __str__(self):
        return 'MstrClient session: %s' % self._session

    def _login(self, project_source, project_name, username, password):
        arguments = {
            'taskId': 'login',
            'server': project_source,
            'project': project_name,
            'userid': username,
            'password': password 
        }
        logger.info("logging in.")
        response = self._request(arguments)
        d = pq(response)
        return d[0][0].find('sessionState').text

    def get_report(self, report_id):
        return Report(self, report_id)

    def get_folder_contents(self, folder_id=None):
        """Returns a dictionary with folder name, GUID, and description.

            args:
                folder_id - id of folder to list contents. If not supplied,
                            returns contents of root folder
            returns:
                dictionary with keys id, name, description, and type 
        """

        arguments = {'sessionState': self._session, 'taskID': 'folderBrowse'}
        if folder_id:
            arguments.update({'folderID': folder_id})
        response = self._request(arguments)
        return self._parse_folder_contents(response)

    def _parse_folder_contents(self, response):
        d = pq(response)
        result = []
        for folder in d('folders').find('obj'):
            result.append({
                'name': folder.find('n').text,
                'description': folder.find('d').text,
                'id': folder.find('id').text,
                'type': folder.find('t').text
            })
        return result

    def list_elements(self, attribute_id):
        """ returns the elements associated with the given attribute id.
            Note that if the call fails (i.e. MicroStrategy returns an
            out of memory stack trace) the returned list is empty

            args:
                attribute_id - the attribute id

            returns:
                a list of strings containing the names for attribute values
        """

        arguments = {'taskId': 'browseElements', 'attributeID': attribute_id,
                'sessionState': self._session}
        response = self._request(arguments)
        return self._parse_elements(response)
        
    def _parse_elements(self, response):
        d = pq(response)
        result = []
        for attr in d('block'):
            if attr.find('n').text:
                result.append(attr.find('n').text)
        return result


    def get_attribute(self, attribute_id):
        """ performs a lookup using MicroStrategy's API to return
            the attribute object for the given attribute id.

            args:
                attribute_id - the attribute guid
            
            returns:
                an Attribute object
        """

        if not attribute_id:
            raise MstrClientException("You must provide an attribute id")
            return
        arguments = {'taskId': 'getAttributeForms', 'attributeID': attribute_id,
                'sessionState': self._session}
        response = self._request(arguments)
        d = pq(response)
        return Attribute(d('dssid')[0].text, d('n')[0].text)

    def _logout(self):
        arguments = {'sessionState': self._session}
        arguments.update(BASE_PARAMS)
        result = self._request(arguments)
        logging.info("logging out returned %s" % result)


    def _request(self, arguments):
        """ assembles the url and performs a get request to
            the MicroStrategy Task Service API

            args:
                arguments - a dictionary mapping get key parameters to values

            returns: the xml text response
        """

        arguments.update(BASE_PARAMS)
        request = self._base_url + urllib.urlencode(arguments)
        logger.info("submitting request %s" % request)
        response = requests.get(request)
        logger.info("received response %s" % response.text)
        return response.text


class Singleton(type):
    def __call__(cls, *args, **kwargs):
        # see if guid is in instances
        if args[0] not in cls._instances:
            cls._instances[args[0]] = super(Singleton, cls).__call__(*args,
                **kwargs)
        return cls._instances[args[0]]


class Attribute(object):
    __metaclass__ = Singleton
    _instances = {}
    def __init__(self, guid, name):
        self.guid = guid
        self.name = name

    def __repr__(self):
        return "<Attribute: guid:%s name:%s>" % (self.guid, self.name)

    def __str__(self):
        return "Attribute: %s - %s" % (self.guid, self.name)


class Metric(object):
    __metaclass__ = Singleton
    _instances = {}
    def __init__(self, guid, name):
        self.guid = guid
        self.name = name

    def __repr__(self):
        return "<Metric: guid:%s name:%s>" % (self.guid, self.name)

    def __str__(self):
        return "Metric: %s - %s" % (self.guid, self.name)


class Report(object):

    def __init__(self, mstr_client, report_id):
        self._mstr_client = mstr_client
        self._id = report_id
        self._args = {'reportID': self._id,'sessionState': mstr_client._session}
        self._attributes = []
        self._metrics = []
        self._headers = []
        self._values = []

    def __str__(self):
        return 'Report with id %s' % self._id

    def get_prompts(self):
        """ returns the prompts associated with this report. If there are
            no prompts, this method returns an error.

            args: None

            returns: a list of Attribute objects
        """

        arguments = {'taskId': 'reportExecute'}
        arguments.update(self._args)
        response = self._mstr_client._request(arguments)
        message = pq(response)('msg')('id')
        if not message:
            logger.debug("failed retrieval of msgID in response %s" % response)
            raise MstrReportException("Error retrieving msgID for report. Most" 
                + " likely the report does not have any prompts.")
            return
        message_id = message[0].text
        arguments = {
            'taskId': 'getPrompts', 
            'objectType': '3',
            'msgID': message_id,
            'sessionState': self._mstr_client._session
        }
        response = self._mstr_client._request(arguments)
        return self._parse_prompts(response)

    def _parse_prompts(self, response):
        prompts = []
        d = pq(response)[0][0]
        for prompt in d.find('prompts').iterchildren():
            data = prompt.find('orgn')
            prompts.append(Attribute(data.find('did').text, data.find('n').text))
        return prompts

    def get_headers(self):
        """ returns the column headers for the report. A report must have
            been executed before calling this method

            args: None
            
            returns: a list of Attribute/Metric objects
        """

        if self._headers:
            return self._headers
        logger.debug("Attempted to retrieve the headers for a report without" + 
                " prior successful execution.")
        raise MstrReportException("Execute a report before viewing the headers")

    def get_attributes(self):
        """ returns the attribute objects for the columns of this report.

            args: None

            returns: list of Attribute objects
        """

        if self._attributes:
            logger.info("Attributes have already been retrieved. Returning " +
                "saved objects.")
            return self._attributes
        arguments = {'taskId': 'browseAttributeForms', 'contentType': 3}
        arguments.update(self._args)
        response = self._mstr_client._request(arguments)
        self._parse_attributes(response)
        return self._attributes

    def _parse_attributes(self, response):
        d = pq(response)
        self._attributes = [Attribute(attr.find('did').text, attr.find('n').text)
                for attr in d('a')]

    def get_values(self):
        if self._values:
            return self._values
        raise MstrReportException("Execute a report before viewing the rows")

    def get_metrics(self):
        if self._metrics:
            return self._metrics
        logger.debug("Attempted to retrieve the metrics for a report without" + 
                " prior successful execution.")
        raise MstrReportException("Execute a report before viewing the metrics")

    def execute(self, start_row=0, start_col=0, max_rows=100000, max_cols=10,
                value_prompt_answers=None, element_prompt_answers=None):
        """
            args:
                start_row - first row number to be returned
                start_col - first column number to be returned
                max_rows - maximum number of rows to return
                max_cols - maximum number of columns to return
                value_prompt_answers - list of value prompt answers in order
                element_prompt_answers - element prompt answers represented as a
                                         dictionary of attribute objects mapping
                                         to a list of attribute values to pass
        """

        arguments = {
            'taskId': 'reportExecute',
            'startRow': start_row,
            'startCol': start_col,
            'maxRows': max_rows,
            'maxCols': max_cols,
            'styleName': 'ReportDataVisualizationXMLStyle',
            'resultFlags' :'393216'
        }
        if value_prompt_answers:
            arguments.update({'valuePromptAnswers':
                '^'.join(value_prompt_answers)})
        if element_prompt_answers:
            arguments.update(self._format_element_prompts(element_prompt_answers))
        arguments.update(self._args)
        response = self._mstr_client._request(arguments)
        self._values = self._parse_report(response)

    def _format_element_prompts(self, prompts):
        result = ''
        for attr, values in prompts.iteritems():
            if result:
                result += ","
            if values:
                prefix = ";" + attr.guid + ":"
                result = result + attr.guid + ";" + attr.guid + ":" + \
                    prefix.join(values)
            else:
                result += attr.guid + ";"
        return {'elementsPromptAnswers': result}

    def _parse_report(self, response):
        d = pq(response)
        if not self._headers:
            self._get_headers(d)
        # iterate through the columns while iterating through the rows
        # and create a list of tuples with the attribute and value for that
        # column for each row
        return [[(self._headers[index], val.text) for index, val
                in enumerate(row.iterchildren())] for row in d('r')]
                
    def _get_headers(self, d):
        obj = d('objects')
        headers = d('headers')
        for col in headers.children():
            elem = obj("[rfd='" + col.attrib['rfd'] + "']")
            if elem('attribute'):
                attr = Attribute(elem.attr('id'), elem.attr('name'))
                self._attributes.append(attr)
                self._headers.append(attr)
            else:
                metric = Metric(elem.attr('id'), elem.attr('name'))
                self._metrics.append(metric)
                self._headers.append(metric)

class MstrClientException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class MstrReportException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
