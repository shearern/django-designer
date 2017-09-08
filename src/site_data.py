import os, sys
import yaml
import re

class SiteData:
    def __init__(self, data):
        self.set_defaults()
        self.__dict__.update(data)
        self.process_data()
    def set_defaults(self):
        pass
    def process_data(self):
        pass
    def make_dict_object_list(self, attr_name, ob, name_attr='name'):
        rtn = list()
        for name, data in getattr(self, attr_name).items():
            rtn.append(ob(data))
            setattr(rtn[-1], name_attr, name)
        setattr(self, attr_name, rtn)
    def find_ob(self, lst, name, attr='name'):
        for item in lst:
            if getattr(item, attr) == name:
                return item
        raise KeyError("'%s' not found in .%s" % (name, attr))
    def lookup(self, items, attr, lookup_func):
        for item in items:
            name = getattr(item, attr)
            if name is not None:
                ref = lookup_func(name)
                setattr(item, attr, ref)


class Feature:
    FEATURE_WITH_TIME=re.compile(r'^(.*)\((\d+)\)$')
    def __init__(self, desc):
        self.desc = desc
        self.estimate = None
        m = self.FEATURE_WITH_TIME.match(self.desc)
        if m:
            self.desc = m.group(1)
            self.estimate = int(m.group(2))
    def __str__(self):
        return self.desc


class Page(SiteData):
    def set_defaults(self):
        self.name = None
        self.parent = None
        self.features = list()
    def process_data(self):
        self.features = [Feature(f) for f in self.features]

class Site(SiteData):
    def set_defaults(self):
        self.name = None
        self.pages = list()
    def process_data(self):
        self.make_dict_object_list('pages', Page)
        self.lookup(self.pages, 'parent', self.get_page)
    @staticmethod
    def load(path):
        with open(path, "rb") as fh:
            return Site(yaml.load(fh))
    def get_page(self, name):
        return self.find_ob(self.pages, name)


if __name__ == '__main__':
    data = Site.load(sys.argv[1])

    print("=== Pages ===")
    for page in data.pages:
        print(page.name)

