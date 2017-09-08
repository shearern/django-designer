


class JiraIssue(object):

    def __init__(self, server, issue_key):
        '''An issue on the Jira server'''

        self.server = server
        self.issue_key = issue_key


    @property
    def status(self):
        data = self.server.get('issue/%s?fields=status' % (self.issue_key))
        try:
            return data['fields']['status']['name']
        except KeyError:
            return 'UNKNOWN'