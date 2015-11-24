import base64
import importlib
import sys

from metamagic.json import dumps, dumpb, loadb

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import a model'

    def add_arguments(self, parser):
        parser.add_argument('-i,--import', dest='import', help='File to import from')
        parser.add_argument('-m,--model', dest='model', help='Models to restrict to')

    def class_for_name(self, class_name):
        class_parts = class_name.split('.')
        module_name = '.'.join(class_parts[0:-1])
        class_name = class_parts[-1]
        m = importlib.import_module(module_name)
        c = getattr(m, class_name)
        return c

    def handle(self, *args, **options):
        if 'import' not in options or not options['import']:
            print("-i <file> option required.")
            sys.exit(-1)

        models = None
        if 'model' in options and options['model']:
            models = options['model'].split(',')

        f = open(options['import'], "r")
        count = 0
        errors = 0
        for file_rec in f:
            dec_val = loadb(base64.b64decode(file_rec))

            model_class = self.class_for_name(dec_val['_class']['model'])
            if models and model_class not in models:
                continue

            rec = model_class()
            for field in dec_val.keys():
                if field == '_class':
                    continue
                setattr(rec, field, dec_val[field])

            try:
                rec.save()
                count += 1
                print(" ---- SAVED")
            except Exception as e:
                errors += 1
                print(" ---- ERROR - (%s) %s" % (dec_val['_class']['model'], e))

        print("Added %d, Errors %d" % (count, errors))
        f.close()
