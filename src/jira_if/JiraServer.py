import os
import requests
import simplejson
from getpass import getuser, getpass
import keyring

from JiraIssue import JiraIssue

class JiraError(Exception): pass


class JiraCreateIssueLog:
    def __init__(self, path):
        self.path = None
        self.__created_tasks = dict()
        self.load(path)
    def load(self, path):
        self.path = path
        if os.path.exists(path):
            with open(path, 'r') as fh:
                self.__created_tasks = {k: v for (k, v) in [l.split("\t") for l in fh.readlines() if len(l.strip()) > 0]}
        else:
            self.__created_tasks = set()
    def save(self):
        with open(self.path, 'w') as fh:
            fh.write("\n".join(self.created_tasks))
    def get(self, key):
        try:
            return self.__created_tasks[key]
        except KeyError:
            return None
    def add(self, key, task_id):
        self.__created_tasks[key] = task_id
        self.save()


class JiraServer(object):
    '''Handle to interface with Jira server'''

    def __init__(self, base_url, username=None, log_path=None):
        '''
        Init

        :param base_url: URL to jira server.  e.g.: 'http://127.0.0.1:8080'
        :param username: Username to connect with
        '''
        self.base_url = base_url
        self.username = username
        self.log = None

        if log_path is not None:
            self.log = JiraCreateIssueLog(log_path)

        if self.username is None:
            self.username = getuser("Username to connect to %s: " % (self.base_url))

        self.password = keyring.get_password(base_url, username)
        if self.password is None:
            self.password = getpass("Password for %s: " % (self.username))
            keyring.set_password(base_url, username, self.password)


    def api_url(self, path):
        return '/'.join((self.base_url, 'rest/api/2', path))


    def _check_not_error(self, data):
        '''Check to see if rest response is an error'''
        if data.__class__ is dict:
            msg = "Jira Error:"
            if data.has_key('title'):
                if data['title'] == 'Error Collection':
                    try:
                        for item in data['properties']['errorMessages']['items']:
                            msg += "\n" + str(item)
                    except KeyError:
                        msg += "\n" + str(data)
                    raise JiraError(msg)
            elif data.has_key('errors') and len(data['errors']) > 0:
                msg += "\n" + str(data['errors'])
                raise JiraError(msg)
        return data


    def get(self, path):
        url = self.api_url(path)
        headers = {
            'Content-Type': 'application/json',
        }

        r = requests.get(url, auth=(self.username, self.password), headers=headers)

        return self._check_not_error(r.json())


    def post(self, path, data):
        url = self.api_url(path)
        headers = {
            'Content-Type': 'application/json',
        }
        data = simplejson.dumps(data)

        r = requests.post(url, auth=(self.username, self.password), headers=headers, data=data)

        return self._check_not_error(r.json())


    def issue(self, issue_key):
        return JiraIssue(self, issue_key)


    def create_issue(self, project, summary, issue_type='Task', description=None, estimated_mins=None, log_key=None):

        # Check to see if issue was already created
        if self.log is not None and log_key is not None:
            task_id = self.log.get(log_key)
            if task_id is not None:
                return 

        issue = {
            'fields': {
                'project': {
                    'key': project,
                },
                'summary': summary,
                'issuetype': {
                    'name': issue_type,
                }
            },
        }

        if description is not None:
            issue['fields']['description'] = str(description)

        if estimated_mins is not None:
            issue['fields']['timetracking'] =  {
                'originalEstimate': str(estimated_mins),
#                'remainingEstimate': "0",
            }

        response = self.post(path = 'issue', data = issue)

        print "Created Task %s: %s" % (response['key'], summary)

        return self.issue(response['key'])