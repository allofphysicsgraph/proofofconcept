import shutil
import os

directories = ['dev', 'dev/images_expression_png/', 'dev/images_feed_png/', 'dev/output/', 'dev/site/',
               'dev/site/pictures/',
               'dev/site/pictures/images_expression_png/', 'dev/site/pictures/images_feed_png/',
               'dev/site/pictures/images_infrule_png',
               'dev/site/json/']

if os.path.exists('dev/'):
    shutil.rmtree('dev/')

[os.mkdir(directory) for directory in directories]
