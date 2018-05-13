import os
import sys
from textwrap import dedent
from tempfile import NamedTemporaryFile
import subprocess

import yaml


classes = [[f.strip() for f in l.strip().split()] for l in """\
    recording   recordings      Recording   Recordings
    speaker     speakers        Speaker     Speakers
    class       classes         Class       Classes
    series      series          Series      Series
    session     sessions        Session     Sessions
    """.strip().split("\n")]

global_views = [l.strip() for l in """\
    list
    """.strip().split("\n")]

node_views = [l.strip() for l in """\
    show
    """.strip().split("\n")]

forms = [l.strip() for l in """\
    Edit
    Delete
    New
    """.strip().split("\n")]



def import_init(init_path, cls_name):
    import_line = 'from .%s import %s' % (cls_name, cls_name)
    with open(init_path, 'r+') as fh:
        fh.seek(0)
        if import_line not in fh.read():
            fh.seek(0, os.SEEK_END)
            fh.write("\n%s" % (import_line))


def create_view(view_cls_name, src):
    path = 'sbc_media_site/preachingdb/views/%s.py' % (view_cls_name)
    if not os.path.exists(path):
        print("Creating " + path)
        with open(path, 'wt') as fh:
            fh.write(dedent(src))
    import_init('sbc_media_site/preachingdb/views/__init__.py', view_cls_name)


def create_form(form_cls_name, src):
    form_path = 'sbc_media_site/preachingdb/forms/%s.py' % (form_cls_name)
    if not os.path.exists(form_path):
        print("Creating " + form_path)
        with open(form_path, 'wt') as fh:
            fh.write(dedent(src))
    import_init('sbc_media_site/preachingdb/forms/__init__.py', form_cls_name)


def create_template(template_name, src):
    path = 'sbc_media_site/preachingdb/templates/preachingdb/' + template_name
    if not os.path.exists(path):
        print("Creating " + path)
        with open(path, 'wt') as fh:
            fh.write(dedent(src))


def make_url(path, view_cls):
    return "    path(r'{path}', views.{view_cls}.as_view()),".format(
        path = path,
        view_cls = view_cls
    )


def indent(idt, txt):
    lines = dedent(txt).split("\n")
    lines = [idt + l for l in lines]
    return "\n".join(lines)


def merge(contents, path):

    wm = [
        r"C:\Program Files (x86)\WinMerge\WinMergeU.exe",
    ]
    wm = filter(lambda p: os.path.exists(p), wm)
    try:
        wm = wm[0]
    except:
        raise Exception("Failed to find WinMerge")

    tf = NamedTemporaryFile(delete=False, suffix=os.path.splitext(path)[1])
    tf.write(contents)
    tf.close()

    subprocess.check_call((wm, tf.name, path))

    os.unlink(tf.name)

# -- Model Files ------------------------------------------------------

def models(site_data):
    for sigl_cls_name, model_info in site_data['models'].items():
        model_info['singular'] = sigl_cls_name
        yield model_info


def format_model_fields(fields):
    for field in fields:
        parms = list()

        try:
            parms.append("max_length=%d" % (field['maxlen']))
        except KeyError:
            pass

        try:
            if field['allow_null']:
                parms.append("null=True")
        except KeyError:
            pass

        try:
            if field['blank']:
                parms.append("blank=True")
        except KeyError:
            pass

        yield '%s = models.%s(%s)' % (field['name'], field['type'], ', '.join(parms))


def generate_model_file(model):
    fields = "\n".join(format_model_fields(model['fields']))
    src = dedent("""\
        from django.db import models
        
        class {model_class}(models.Model):
            # -- DB Fields -----------------------------------------------------------
        {fields}
            # ------------------------------------------------------------------------
        """).format(
            model_class=model['singular'],
            fields = indent('    ', fields))
    return dedent(src)


if __name__ == '__main__':

    # Parse args
    try:
        site_file, app_root = sys.argv[1:]
    except ValueError:
        print("Usage Error: compile_site.py site_file app_root")
        sys.exit(1)

    # Load site data file
    try:
        with open(site_file, 'rt') as fh:
            site = yaml.load(fh)
    except Exception as e:
        print("ERROR: Can't load site file %s: %s" % (site_file, str(e)))
        sys.exit(1)

    # Check target path
    if not os.path.exists(os.path.join(app_root, 'apps.py')):
        print("ERROR: Missing %s" % (os.path.join(app_root, 'apps.py')))
        sys.exit(1)

    # Begin build

    urls = list()

    for model in models(site):

        # Build model file
        path = os.path.join(app_root, 'models', model['singular']+'.py')
        src = generate_model_file(model)
        merge(src, path)


    #     # Global views
    #     for view in global_views:
    #         url = '{model}/{view}'.format(model=plural_model, view=view)
    #
    #         template_name = '%s_%s.html' % (view, plural_model)
    #         template = """\
    #             <em>TODO</em>
    #             """
    #         create_template(template_name, template)
    #
    #         view_caps = view[0].upper() + view[1:]
    #         view_cls_name =  view_caps + plural_model_cls_name + 'View'
    #         view_src = """\
    #             from django.views.generic import TemplateView
    #
    #             class {name}(TemplateView):
    #                 template_name = "preachingdb/{template}"
    #             """.format(
    #                 name = view_cls_name,
    #                 template = template_name,
    #             )
    #         create_view(view_cls_name, view_src)
    #
    #         urls.append((single_model, make_url(url, view_cls_name)))
    #
    #
    #     # Node views
    #     for view in node_views:
    #         url = '{model}/<slug:slug>/{view}'.format(model=single_model, view=view)
    #
    #         view_caps = view[0].upper() + view[1:]
    #         view_cls_name =  view_caps + sgl_model_cls_name + 'View'
    #
    #         template_name = '%s_%s.html' % (view, single_model)
    #         template = """\
    #             <em>TODO</em>
    #             """
    #         create_template(template_name, template)
    #
    #         view_src = """\
    #             from django.views.generic import TemplateView
    #
    #             class {name}(TemplateView):
    #                 template_name = "preachingdb/{template}"
    #             """.format(
    #                 name = view_cls_name,
    #                 template = template_name,
    #             )
    #         create_view(view_cls_name, view_src)
    #
    #         urls.append((single_model, make_url(url, view_cls_name)))
    #
    #
    #     # Forms
    #     for form in forms:
    #
    #         url = '{model}/<slug:slug>/{form}'.format(model=single_model, form=form.lower())
    #
    #         form_cls_name = form + sgl_model_cls_name + 'Form'
    #         form_src = """\
    #             from django import forms
    #
    #             class {name}(forms.Form):
    #                 your_name = forms.CharField(label='Your name', max_length=100)
    #             """.format(
    #                 name=form_cls_name,
    #             )
    #         create_form(form_cls_name, form_src)
    #
    #         template_name = form.lower() + '_' + single_model + '.html'
    #         template = """\
    #             <form action="preachingdb/%s" method="post">
    #                 {%% csrf_token %%}
    #                 {{ form }}
    #                 <input type="submit" value="Submit" />
    #             </form>
    #             """ % (url)
    #         create_template(template_name, template)
    #
    #         form_view_cls_name = form_cls_name + 'View'
    #         form_view = """\
    #             from preachingdb.forms import {form_cls_name}
    #             from django.views.generic.edit import FormView
    #
    #             class {view_cls_name}(FormView):
    #                 template_name = 'preachingdb/{template_name}'
    #                 form_class = {form_cls_name}
    #                 success_url = '/success/'
    #
    #                 def form_valid(self, form):
    #                     # This method is called when valid form data has been POSTed.
    #                     # It should return an HttpResponse.
    #                     pass
    #             """.format(
    #                 view_cls_name = form_view_cls_name,
    #                 form_cls_name = form_cls_name,
    #                 template_name = template_name,
    #             )
    #         create_view(form_view_cls_name, form_view)
    #
    #         urls.append((single_model, make_url(url, form_view_cls_name)))
    #
    # print()
    # print("URLS:")
    # for url in sorted(urls):
    #     print(url[1])