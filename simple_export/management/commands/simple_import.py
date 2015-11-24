import base64
import sys

from metamagic.json import dumps, dumpb, loadb

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import a model'

    def add_arguments(self, parser):
        parser.add_argument('-i,--import', dest='import', help='File to import from')

    def class_for_name(self, class_name):
        class_parts = class_name.split('.')
        module_name = '.'.join(class_parts[0:-1])
        class_name = class_parts[-1]
        m = importlib.import_module(module_name)
        c = getattr(m, class_name)
        return c

    def handle(self, *args, **options):
        if not options['import']:
            print("-i <file> option required.")
            sys.exit(-1)

        f = open(options['import'], "r")
        for file_rec in f:
            dec_val = loadb(base64.b64decode(file_rec))

            model_class = dec_val['_class']['model']
            print(model_class)

            #file_rec = file_rec.decode('base64')
            #print(base64.b64decode(file_rec).decode('utf-8'))
        f.close()
