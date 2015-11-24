import base64
import importlib
import sys

from metamagic.json import dumps, dumpb, loadb

from django.core.management.base import BaseCommand

from simple_export import DJANGO_SIMPLE_FORMAT_VERSION


class Command(BaseCommand):
    help = 'Export a model'

    def add_arguments(self, parser):
        parser.add_argument('-o,--output', dest='output', help='File to output export to')
        parser.add_argument('-m,--model', dest='model', help='Fully qualified model to export')

    def class_for_name(self, class_name):
        class_parts = class_name.split('.')
        module_name = '.'.join(class_parts[0:-1])
        class_name = class_parts[-1]
        m = importlib.import_module(module_name)
        c = getattr(m, class_name)
        return c

    def get_class_fields(self, cls):
        if hasattr(cls, '_fields'):
            return list(cls._fields.keys())
        if cls._meta.fields:
            return cls._meta.fields
        return cls._meta.model._meta.fields + cls._meta.model._meta.many_to_many

    def handle(self, *args, **options):
        if not options['output']:
            print("-o <file> option required.")
            sys.exit(-1)

        if not options['model']:
            print("-m <model> option required.")
            sys.exit(-1)

        f = open(options['output'], "wb")
        count = 0
        for model in options['model'].split(','):
            count += self._process_model(f, model)

        f.close()

        print("Exported %d records" % (count))

    def _process_model(self, f, model):
        model_class = self.class_for_name(model)
        fields = self.get_class_fields(model_class)
        qs = model_class.objects.all()

        if hasattr(qs, 'iterator'):
            qs = qs.iterator()

        count = 0
        for rec in qs:
            export_data = {}
            for field in fields:
                field, export_data[field] = self._get_field_data(rec, field)

            export_data['_class'] = {
                'format_version': DJANGO_SIMPLE_FORMAT_VERSION,
                'model': "{0}.{1}".format(rec.__class__.__module__, rec.__class__.__name__)
            }

            enc_val = base64.b64encode(dumpb(export_data))
            f.write(enc_val)
            f.write(b'\n')
            count += 1
        return count

    def _get_field_data(self, rec, field):
        val = getattr(rec, field)
        if field == 'id':
            return field, str(val)
        if hasattr(val, "id"):
            return field + "_id", str(val.id)
        return field, val
