'''Wizard to start new set of site files for generating a set of files'''
import os
import yaml

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

        site_data = dict()

        # List model classes
        models = self.ask_list('models', "List the model class names to start with")

        # Get details for each model
        site_data['models'] = dict()
        for model in models:

            print("==== MODEL: %s ====" % (model))
            qid = lambda n: "model.%s.%s" % (model, n)
            single_class = self.ask_simple(
                qid('single_class'),
                "Singular class name for %s" % (model),
                default = model[0].upper() + model[1:])
            plural_class = self.ask_simple(
                qid('plural_class'),
                "Plural Class Name for %s" % (model),
                default = model[0].upper() + model[1:] + 's')
            single_name = self.ask_simple(
                qid('single_name'),
                "Singular Name for %s" % (model),
                default = model.lower())
            plural_name = self.ask_simple(
                qid('plural_name'),
                "Plural Name for %s" % (model),
                default = plural_class.lower())
            site_data['models'][single_class] = {
                'plural': plural_class,
                'single_name': single_name,
                'plural_name': plural_name,
            }

            # Field Names
            i = 0
            site_data['models'][single_class]['fields'] = list()
            while True:
                i += 1

                field = dict()

                name = field['name'] = self.ask_name("model.%s.fieldname.%d" % (model, i),
                    "Name of field %d" % (i),
                    optional = True)
                if name is None:
                    break

                qid = lambda n: "model.%s.fields.%s.%s" % (model, name, n)

                field_types = [n.strip() for n in """\
                    CharField
                    TextField
                    BooleanField
                    DateField
                    DateTimeField
                    FileField
                    ImageField
                    IntegerField
                    BinaryField
                    BigIntegerField
                    FloatField
                    DecimalField
                    
                    ForeignKey
                    ManyToManyField

                    AutoField
                    BigAutoField
                    DurationField
                    EmailField
                    FieldFile
                    FilePathField
                    GenericIPAddressField
                    NullBooleanField
                    PositiveIntegerField
                    PositiveSmallIntegerField
                    SmallIntegerField
                    TimeField
                    URLField
                    UUIDField          
                    """.split("\n") if len(n.strip()) > 0]

                field['type'] = self.ask_select(
                    qid('type'),
                    "Model data type for field %s" % (name),
                    options=field_types)

                field['allow_null'] = self.ask_yes_no(
                    qid('allow_null'),
                    "Allow field %s to be null?" % (name),
                    default=True)

                if field['type'] in ('CharField', ):
                    field['maxlen'] = self.ask_int(
                        qid('maxlen'),
                        "Maximum length of %s" % (name),
                        optional=True)

                if field['type'] in ('ForeignKey', 'ManyToManyField'):
                    field['foreign_model'] = self.ask_name(
                        qid('foreign_model'),
                        "Name of foreign model for %s" % (name),
                        optional=True)
                    field['foreign_on_delete'] = self.ask_select(
                        qid('foreign_on_delete'),
                        "When %s is deleted, do to %s" % (field['foreign_model'], name),
                        options = ('CASCADE', 'PROTECT', 'SET_NULL', 'SET_DEFAULT', 'DO_NOTHING'),
                        optional=True)

                site_data['models'][single_class]['fields'].append(field)


        path = os.path.join(self.target, 'site.yml')
        print("Writing " + path)
        with open(path, 'wb') as fh:
            yaml.dump(site_data, fh, default_flow_style=False)


if __name__ == '__main__':

    wiz = DjangoDesignNewProjectWizard()
    run_wizard(wiz)