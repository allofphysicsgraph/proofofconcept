# https://github.com/hplgit/web4sciapps/blob/master/doc/src/web4sa/src-web4sa/apps/flask_apps/vib1/model.py

from wtforms import Form, TextField, SelectField, validators

class AddAnotherStep(Form):
    addStep    = SelectField(u'Add another step?', choices=[('y', 'yes'), 
                                                            ('n', 'no, produce file')])

class SelectInfRule(Form): # http://wtforms.simplecodes.com/docs/0.6.1/fields.html
    inference_rule    = SelectField(u'inference rule:', choices=[('multbothsidesby', 'multiply both sides by'), 
                                                                ('simplify', 'simplify'), 
                                                                ('dividebothsidesby', 'divide both sides by')])


class InfRuleArguments(Form): # http://wtforms.simplecodes.com/docs/0.6.1/fields.html
    input_expression  = TextField(u'Input Expression', [validators.required()])
    feed              = TextField(u'Feed', [validators.required()])
    output_expression = TextField(u'Output Expression', [validators.required()])


