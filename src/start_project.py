'''Wizard to start new set of site files for generating a set of files'''
import os

from py_wizard.PyMainWizard import PyMainWizard
from py_wizard.runner import run_wizard


class DjangoDesignNewProjectWizard(PyMainWizard):

    def ask_presave_questions(self):

        # Django-design root
        self.root = os.path.abspath('django-design.sites')
        self.root = self.ask_simple('root', "Root folder for django-design.sites",
                                    default=self.root)
        if not os.path.exists(self.root):
            try:
                print("mkdir %s" % (self.root))
                os.mkdir(self.root)
            except Exception as e:
                raise Exception("ERROR: Failed to create output directory: %s" % (self.root))

        # Site Name
        sites_file = os.path.join(self.root, 'sites.txt')
        options = list()
        if os.path.exists(sites_file):
            with open(sites_file, 'rt') as fh:
                options.extend([line.strip() for line in fh.readlines() if line.strip() != ''])
        options.append("new")
        self.site_name = self.ask_select('site_name', "Site Name", options=options)
        if self.site_name == 'new':
            self.site_name = self.ask_simple('site_name', "Site Name")
        with open(os.path.join(self.root, 'sites.txt'), 'wt') as fh:
            options.remove('new')
            if self.site_name not in options:
                options.append(self.site_name)
            fh.write("\n".join(options))

        # Create output directory
        self.target = os.path.join(self.root, self.site_name)
        if not os.path.exists(self.target):
            try:
                print("mkdir %s" % (self.target))
                os.mkdir(self.target)
            except Exception as e:
                raise Exception("ERROR: Failed to create output directory: %s" % (self.target_dir))


    def _calc_autosave_path(self):
        return os.path.join(self.target, 'wizard.answers')

    def execute(self):

        # List model classes
        models = self.ask_list('models', "List the model class names to start with")

        # Get different names for each model
        models_file = list()
        models_file.append(("Class", "Singular Class", "Plural Class", "Single Name", "Plural Name"))
        for model in models:
            print("==== %s ====" % (model))
            qid = lambda n: "model.%s.%s" % (model, n)
            single_class = self.ask_simple(
                qid('single_class'),
                "Singlure class name for %s" % (model),
                default = model[0].upper() + model[1:])
            plural_class = self.ask_simple(
                qid('plural_class'),
                "Plural Class Name for %s" % (model),
                default = model[0].upper() + model[1:] + 's')
            single_name = self.ask_simple(
                qid('single_name'),
                "Singlure Name for %s" % (model),
                default = model.lower())
            plural_name = self.ask_simple(
                qid('plural_name'),
                "Plural Name for %s" % (model),
                default = plural_class.lower())
            models_file.append((single_class, plural_class, single_name, plural_name))

        path = os.path.join(self.target, 'models.tsv')
        print("Writing " + path)
        with open(path, 'wt') as fh:
            for line in models_file:
                fh.write("\t".join(line) + "\n")



if __name__ == '__main__':

    wiz = DjangoDesignNewProjectWizard()
    run_wizard(wiz)