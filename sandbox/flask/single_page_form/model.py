# https://github.com/hplgit/web4sciapps/blob/master/doc/src/web4sa/src-web4sa/apps/flask_apps/vib1/model.py

from wtforms import Form, TextField, SelectField, validators

class InputForm(Form): # http://wtforms.simplecodes.com/docs/0.6.1/fields.html
    input_expression  = TextField(u'Input Expression', [validators.required()])
    inference_rule    = SelectField(u'inference rule', choices=[('multbothsidesby', 'multiply both sides by'), 
                                                                ('simplify', 'simplify'), 
                                                                ('dividebothsidesby', 'divide both sides by')])
    feed              = TextField(u'Feed', [validators.required()])
    output_expression = TextField(u'Output Expression', [validators.required()])


