from JiraServer import JiraServer


class SbcJira(JiraServer):
    def __init__(self):
        super(SbcJira, self).__init__(base_url='http://projects.spokanebaptist.net:8080',
                                       username='nate')



