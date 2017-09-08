from JiraServer import JiraServer


class WorkJira(JiraServer):
    def __init__(self, password=None):
        super(WorkJira, self).__init__(base_url='http://10.101.61.12:8080',
                                       username='nshearer@ewu.edu',
                                       password=password)



