#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import lib_physics_graph as physgraf
import yaml  # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('../lib')
db_path = os.path.abspath('database')
output_path = os.path.abspath('output')
sys.path.append(lib_path)  # this has to proceed use of physgraph


input_stream = file('config.input', 'r')
input_data = yaml.load(input_stream)
extension = input_data["file_extension_string"]
redraw_feed_pictures_boolean = input_data["redraw_feed_pictures_boolean"]
redraw_statement_pictures_boolean = input_data["redraw_statement_pictures_boolean"]

statement_pictures = lib_path + '/images_eq_' + extension
feed_pictures = lib_path + '/images_feed_' + extension

statementsDB = physgraf.parse_XML_file(db_path + '/expressions_database.xml')
statementPicsDrawnCount = 0
statementCount = 0
for item in statementsDB.getElementsByTagName('statement'):
    statementCount = statementCount + 1
    statement_indx = physgraf.convert_tag_to_content(
        item, 'statement_punid', 0)
    statement_latex = physgraf.convert_tag_to_content(
        item, 'statement_latex', 0)
    statement_latex_math = '\\begin{equation*}\n' + \
        statement_latex + '\\end{equation*}\n'
    # http://stackoverflow.com/questions/82831/how-do-i-check-if-a-file-exists-using-python
    if (
        (redraw_statement_pictures_boolean) or (
            (not redraw_statement_pictures_boolean) and not (
            os.path.isfile(
                statement_pictures +
                '/' +
                statement_indx +
                '.' +
                extension)))):  # if file does not exist, redraw
        physgraf.make_picture_from_latex(
            statement_indx,
            statement_pictures,
            statement_latex_math,
            extension)
        statementPicsDrawnCount = statementPicsDrawnCount + 1

print("found " + str(statementCount) + " statements")
if (statementPicsDrawnCount == 0):
    print("no new statement pictures created because they already existed")
else:
    print("made " + str(statementPicsDrawnCount) + " statement pictures")

feedDB = physgraf.parse_XML_file(db_path + '/feed_database.xml')
feedPicsDrawnCount = 0
feedCount = 0

for item in feedDB.getElementsByTagName('feed'):
    feedCount = feedCount + 1
    feed_tunid = physgraf.convert_tag_to_content(item, 'feed_tunid', 0)
    feed_latex = physgraf.convert_tag_to_content(item, 'feed_latex', 0)
    feed_latex_math = '\\begin{equation*}\n' + \
        feed_latex + '\\end{equation*}\n'
    # http://stackoverflow.com/questions/82831/how-do-i-check-if-a-file-exists-using-python
    if (
        (redraw_feed_pictures_boolean) or (
            (not redraw_feed_pictures_boolean) and not (
            os.path.isfile(
                feed_pictures +
                '/' +
                feed_tunid +
                '.' +
                extension)))):  # if file does not exist, redraw
        physgraf.make_picture_from_latex(
            feed_tunid, feed_pictures, feed_latex_math, extension)
        feedPicsDrawnCount = feedPicsDrawnCount + 1

print("found " + str(feedCount) + " feeds")
if (feedPicsDrawnCount == 0):
    print("no new feed pictures created because they already existed")
else:
    print("made " + str(feedPicsDrawnCount) + " feed pictures")


sys.exit("done")
