import os, sys
from textwrap import dedent
from hashlib import md5
import re
import keyring

from site_data import Site
from jira_if import JiraServer

class DevTask:
    def __init__(self, task_id, task_desc, estimated_mins=None, help=None):
        self.task_id = task_id
        self.task_desc = task_desc
        self.estimated_mins = estimated_mins



def gen_tasks(data):

    # Pages
    for page in data.pages:

        yield DevTask('page.%s.url' % (page.name),
                      "Create url for page %s" % (page.name),
                      estimated_mins=3)

        for feature in page.features:
            yield DevTask('page.%s.feature.%s' % (page.name, md5(feature.desc.encode('ascii')).hexdigest()),
                          "%s feature: %s" % (page.name, feature.desc),
                          estimated_mins=feature.estimate)

if __name__ == '__main__':

    try:
        site_data_path, server_url, username, project_name = sys.argv[1:]
    except:
        print("USAGE ERROR: gen_tasks.py site_data.yml url username porject_name")
        print("             where url is like: http://projects.spokanebaptist.net:8080")
        sys.exit(1)

    data = Site.load(site_data_path)

    jira = JiraServer(base_url=server_url, username=username)



    for task in gen_tasks(data):
        print(task.task_desc)


