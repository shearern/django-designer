import os
import sys
import string
from pathlib import Path

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

TEMPLATE_DIR = (Path(os.path.dirname(__file__)) / '..' / 'templates').absolute()

def load_template(filename):
    path = TEMPLATE_DIR / filename
    with open(str(path), 'r') as fh:
        tpl = Template(
            fh.read(),
            lookup=TemplateLookup(directories=[str(TEMPLATE_DIR), ]))
    return tpl


def render_template(filename, **kwargs):
    tpl = load_template(filename)
    try:
        src = tpl.render(**kwargs)
        return src
    except:
        print("================" + '='*len(filename))
        print("ERROR Rendering %s" % (filename))
        print("================" + '='*len(filename))
        print(exceptions.text_error_template().render())
        sys.exit(2)


def nvl(val, if_none):
    if val is None:
        return if_none
    return val


SAFE_CHARS = set(string.ascii_letters + string.digits)
def sanatize_name(name):
    global SAFE_CHARS
    name = list(str(name))
    for i, c in enumerate(name):
        if c not in SAFE_CHARS:
            name[i] = '_'
    return ''.join(name)


def ngroup(items, group_size, fill_none=False):
    '''
    Return items in groups of group_size length.

    :param items: Collection of items to split up
    :param group_size: Number of items in each group to yield
    :param fill_none: If True, then fill last group with None values to total size
    :return:
    '''
    remaining = list(items)
    while len(remaining) > 0:
        group = remaining[:group_size]
        if fill_none:
            group.extend([None, ] * (group_size - len(group)))
        yield group
        remaining = remaining[group_size:]


def group_by(items, attr_name):
    items_without_group = list()
    groups = dict()
    group_order = list()
    for item in items:
        try:
            group_key = getattr(item, attr_name)
            if group_key in group_order:
                groups[group_key].append(item)
            else:
                group_order.append(group_key)
                groups[group_key] = list((item, ))
        except AttributeError:
            items_without_group.append(item)

    for group_key in group_order:
        yield group_key, groups[group_key]

    if len(items_without_group) > 0:
        yield None, items_without_group
