'''Wizard to start new set of site files for generating a set of files'''
import os
import sys
import yaml
import gflags

from bunch import Bunch

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

        # Loop over models
        models = list()
        while True:

            print("="*60)
            print("Next Model")
            print("="*60)
            print("")

            # Model Name
            single_class = model = self.ask_name("modelname.%d" % (len(models)),
                "Class name (singular) of model #%d" % (len(models) + 1),
                optional = True)
            if model is None:
                break

            # Model naming details
            print("==== MODEL: %s ====" % (model))
            qid = lambda n: "model.%s.%s" % (model, n)

            plural_class = self.ask_simple(
                qid('plural_class'),
                "Plural name to use in any classes for %s" % (model),
                default = model[0].upper() + model[1:] + 's')
            single_name = self.ask_simple(
                qid('single_name'),
                "Singular lower case name for %s" % (model),
                default = model.lower())
            plural_name = self.ask_simple(
                qid('plural_name'),
                "Plural lower case name for %s" % (model),
                default = plural_class.lower())

            models.append(Bunch({
                'single_class': single_class,
                'plural_class': plural_class,
                'single_name': single_name,
                'plural_name': plural_name,
                'fields': list(),
            }))

            # Field Names
            while True:

                field = Bunch()

                name = field['name'] = self.ask_name("model.%s.fieldname.%d" % (model, len(models[-1].fields)+1),
                    "Name of field %d for %s" % (len(models[-1].fields)+1, model),
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

                field.yaml_inline_parms = list()
                field.yaml_parms = list()

                field.type = self.ask_select(
                    qid('type'),
                    "Model data type for field %s" % (name),
                    options=field_types)
                field.yaml_inline_parms.append(('type', field.type))

                field['allow_null'] = self.ask_yes_no(
                    qid('allow_null'),
                    "Allow field %s to be null?" % (name),
                    default=True)
                if field.allow_null is not None:
                    field.yaml_inline_parms.append(('allow_null', field.allow_null))

                if field['type'] in ('CharField', ):
                    field['maxlen'] = self.ask_int(
                        qid('maxlen'),
                        "Maximum length of %s" % (name),
                        optional=True)
                    if field.maxlen is not None:
                        field.yaml_inline_parms.append(('maxlen', int(field.maxlen)))

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

                models[-1].fields.append(field)


        # Format output
        path = os.path.join(self.target, 'site.yml')
        print("Writing " + path)
        with open(path, 'wt') as fh:
            print >>fh, "---"
            for model in models:
                print >>fh, "  - names: {sclass: %s, pclass: %s, sname: %s, pname: %s}" % (
                    model.single_class, model.plural_class, model.single_name, model.plural_name)
                if len(model.fields) > 0:
                    print >>fh, " "*4 + 'fields':
                for fields in model.fields:
                    fparms = list()
                    fparms['type']
                    print >>fh, " "*4 + '%s:' % (field.name)





if __name__ == '__main__':

    # Parse arguments
    try:
        argv = gflags.FLAGS(sys.argv)
    except gflags.FlagsError, e:
        print 'USAGE ERROR: %s\nUsage: %s ARGS\n%s' % (e, sys.argv[0], gflags.FLAGS)
        sys.exit(1)

    wiz = DjangoDesignNewProjectWizard()
    run_wizard(wiz)