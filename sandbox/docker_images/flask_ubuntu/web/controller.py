#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html

from flask import Flask, redirect, render_template, request, url_for
from wtforms import Form, StringField, FloatField, validators, FieldList, FormField
import compute 
from config import Config # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms


app = Flask(__name__, static_folder='static')
app.config.from_object(Config) # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

class EquationInputForm(Form):
#    r = FloatField(validators=[validators.InputRequired()])
#    r = FloatField()
    latex = StringField('LaTeX',validators=[validators.InputRequired()])

class infRuleInputsAndOutputs(Form):
    """
    a form with one or more latex entries 
    source: https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms
            https://stackoverflow.com/questions/30121763/how-to-use-a-wtforms-fieldlist-of-formfields
            https://gist.github.com/doobeh/5d0f965502b86fee80fe
            https://www.rmedgar.com/blog/dynamic_fields_flask_wtf

    docs: https://wtforms.readthedocs.io/en/latest/fields.html#field-enclosures
          https://wtforms.readthedocs.io/en/latest/fields.html#wtforms.fields.FieldList
          https://wtforms.readthedocs.io/en/latest/fields.html#wtforms.fields.FormField
    """
    inputs_and_outputs = FieldList(FormField(EquationInputForm,'late_x'), min_entries=1)
#    inputs_and_outputs = FieldList(EquationInputForm, min_entries=1)

# https://stackoverflow.com/questions/37837682/python-class-input-argument/37837766
class LatexIO(Form):
    #,num_feeds,num_inputs,num_outputs):
    def __init__(self, num_feeds, num_inputs, num_outputs):
        print('called class\nnum_feeds =',num_feeds)
        print('num_inputs =',num_inputs,'\nnum_outputs =',num_outputs)
        if num_feeds > 0: self.feed1 = StringField('feed LaTeX 1',validators=[validators.InputRequired()])
        if num_feeds > 1: self.feed2 = StringField('feed LaTeX 2'+str(feed_indx+1),validators=[validators.InputRequired()])
        if num_feeds > 2: self.feed3 = StringField('feed LaTeX 3'+str(feed_indx+1),validators=[validators.InputRequired()])
        if num_inputs > 0: self.input1 = StringField('input LaTeX 1'+str(input_indx+1),validators=[validators.InputRequired()])
        if num_inputs > 1: self.input2 = StringField('input LaTeX 2'+str(input_indx+1),validators=[validators.InputRequired()])
        if num_inputs > 2: self.input3 = StringField('input LaTeX 3'+str(input_indx+1),validators=[validators.InputRequired()])
        if num_outputs > 0: self.output1 = StringField('output LaTeX 1',validators=[validators.InputRequired()])
        if num_outputs > 1: self.output2 = StringField('output LaTeX 2',validators=[validators.InputRequired()])
        if num_outputs > 2: self.output3 = StringField('output LaTeX 3',validators=[validators.InputRequired()])
#        feed_list   = []
#        for feed_indx in range(num_feeds):
#            feed_list.append(   StringField('feed LaTeX '+str(feed_indx+1),validators=[validators.InputRequired()]))
#        self.feed_list = feed_list
#        input_list  = []
#        for input_indx in range(num_inputs):
#            input_list.append(  StringField('input LaTeX '+str(input_indx+1),validators=[validators.InputRequired()]))
#        self.input_list = input_list
#        output_list = []
#        for output_indx in range(num_outputs):
#            output_list.append( StringField('output LaTeX '+str(output_indx+1),validators=[validators.InputRequired()]))
#        self.output_list = output_list

class LatexOneInputZeroOutput(Form):
    latex_in_one = StringField('LaTeX',validators=[validators.InputRequired()])

class LatexOneInputOneOutput(Form):
    latex_in_one  = StringField('LaTeX',validators=[validators.InputRequired()])
    latex_out_one = StringField('LaTeX',validators=[validators.InputRequired()])

class LatexZeroInputOneOutput(Form):
    latex_out_one = StringField('LaTeX',validators=[validators.InputRequired()])

class LatexOneInputTwoOutput(Form):
    latex_in_one = StringField('LaTeX',validators=[validators.InputRequired()])
    latex_out_one = StringField('LaTeX',validators=[validators.InputRequired()])
    latex_out_two = StringField('LaTeX',validators=[validators.InputRequired()])

class LatexTwoInputOneOutput(Form):
    latex_in_one = StringField('input LaTeX 1',validators=[validators.InputRequired()])
    latex_in_two = StringField('input LaTeX 2',validators=[validators.InputRequired()])
    latex_out_one = StringField('output LaTeX',validators=[validators.InputRequired()])

class LatexTwoInputTwoOutput(Form):
    latex_in_one = StringField('LaTeX',validators=[validators.InputRequired()])
    latex_in_two = StringField('LaTeX',validators=[validators.InputRequired()])
    latex_out_one = StringField('LaTeX',validators=[validators.InputRequired()])
    latex_out_two = StringField('LaTeX',validators=[validators.InputRequired()])

class NameOfDerivationInputForm(Form):
    name_of_derivation = StringField(validators=[validators.InputRequired()])

# goal = prevent cached responses; see https://stackoverflow.com/questions/47376744/how-to-prevent-cached-response-flask-server-using-chrome
# The following doesn't work; F12 > Network > Disable cache
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

# View
@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    """ 
    index.html contains hyperlinks to pages like:
    * start new derivation
    * edit existing derivation
    * edit inference rule
    * view existing derivations
    """
    return render_template('index.html')

@app.route('/start_new_derivation/', methods=['GET', 'POST'])
def start_new_derivation():
    form = NameOfDerivationInputForm(request.form)
    if request.method == 'POST' and form.validate():
        name_of_derivation = form.name_of_derivation.data
        print('name of derivation:',name_of_derivation)
        return redirect(url_for('select_inference_rule', name_of_derivation=name_of_derivation))
              #select_inference_rule(name_of_derivation) 
              #render_template("select_inference_rule.html")
    else:
        return render_template("start_new_derivation.html",form=form,title='start new derivation')

@app.route('/edit_existing_derivation', methods=['GET', 'POST'])
def edit_existing_derivation():
    return render_template("edit_existing_derivation.html")

@app.route('/edit_inference_rule', methods=['GET', 'POST'])
def edit_inference_rule():
    return render_template("edit_inference_rule.html")

@app.route('/list_all_inference_rules', methods=['GET', 'POST'])
def list_all_inference_rules():
    return render_template("list_all_inference_rules.html")

@app.route('/select_derivation_to_edit', methods=['GET', 'POST'])
def select_derivation_to_edit():
    return render_template("select_derivation_to_edit.html")

@app.route('/select_derivation_step_to_edit', methods=['GET', 'POST'])
def select_derivation_step_to_edit():
    return render_template("select_derivation_step_to_edit.html")

@app.route('/list_all_expressions', methods=['GET', 'POST'])
def list_all_expressions():
    return render_template("list_all_expressions.html")


@app.route('/view_existing_derivations', methods=['GET', 'POST'])
def view_existing_derivations():
    return render_template("view_existing_derivations.html")

@app.route('/select_inference_rule/<name_of_derivation>/', methods=['GET', 'POST'])
def select_inference_rule(name_of_derivation):
    """
    TODO: rather than a local list, 
    this function should poll the SQL database
    """
    list_of_inf_rules = compute.get_list_of_inf_rules()

#    if request.method == 'POST':
#        print(request.args['inf_rule'])

    return render_template("select_inference_rule.html",
                           title=name_of_derivation,
                           inf_rule_list=list_of_inf_rules,
                           name_of_derivation=name_of_derivation)


@app.route('/inf_rule_selected/<name_of_derivation>', methods=['GET', 'POST'])
def inf_rule_selected(name_of_derivation):
    """
    TODO SQL interaction: for a given inf_rule, return number of inputs and outputs
    https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms
    """
    print('name of derivation=',name_of_derivation)
    select = request.form.get('inf_rul_select') # this comes from the POST 

    num_feeds, num_inputs, num_outputs = compute.input_output_count_for_infrule(select)

    form = LatexIO(num_feeds, num_inputs, num_outputs)

#    if number_of_inputs == 0 and number_of_outputs == 1: 
#        print('no inputs, 1 output')
#        form = LatexZeroInputOneOutput(request.form)
#    elif number_of_inputs == 2 and number_of_outputs == 1:
#        print('2 inputs, 1 output')
#        form = LatexTwoInputOneOutput(request.form)
#    elif number_of_inputs == 2 and number_of_outputs == 1:
#        print('2 inputs, 1 output')
#        form = LatexTwoInputOneOutput(request.form)
#    else:
#        raise Exception('invalid number of arguments passed')
#    print('user selected inference rule:',select)

    #form = infRuleInputsAndOutputs(input_latex=inputs, output_latex = outputs)
    #form = infRuleInputsAndOutputs(inputs=inputs) # "form" is an instance of the class "infRuleInputsAndOutputs"
    #form = infRuleInputsAndOutputs()
    #form = infRuleInputsAndOutputs(request.form,inputs=inputs)
    #form = FieldList(StringField(validators=[validators.InputRequired()]),min_entries=1)

    #print(form.errors)

    #print('form',form) # instance of class
    #print(form.latex_in_one)
    #print(form.inputs_and_outputs) # inputs_and_outputs is an attribute in the class "infRuleInputsAndOutputs"

    return render_template('inf_rule_selected.html',
                            name_of_derivation=name_of_derivation,
                            number_of_feeds=num_feeds,
                            number_of_inputs=num_inputs,
                            number_of_outputs=num_outputs,
                            inf_rule=select,
                            form=form)

@app.route('/step_review/<name_of_derivation>/<inf_rule>/', methods=['GET', 'POST'])
def step_review(name_of_derivation,inf_rule):
    """
    https://teamtreehouse.com/community/getting-data-from-wtforms-formfield
    """
    if request.method == 'POST':
        res = request.form
        print(res) # form from inf_rule_selected()
        # looks like {'latex_in_one':'asdf', 'latex_in_two':'afdm','latex_out_one':'imfa'}
        inf_rule_local_id = compute.create_local_id(print_debug)
        inf_rule_png      = compute.create_png_from_latex(inf_rule,print_debug)
        eq_and_png={}
        for which_eq, this_eq in res.items():
            name_of_png = compute.create_png_from_latex(this_eq,print_debug)
            eq_and_png[which_eq] = {'equation text':this_eq, 
                                    'equation picture':name_of_png,
                                    'local identifier':compute.create_local_id(print_debug)}
        name_of_graphviz_png = compute.create_step_graphviz_png(eq_and_png,
                                                           inf_rule,inf_rule_local_id,inf_rule_png,
                                                           name_of_derivation,
                                                           print_debug)
        return render_template("step_review.html",
                               eq_and_png=eq_and_png,
                               name_of_graphviz_png=name_of_graphviz_png,
                               name_of_derivation=name_of_derivation,
                               inf_rule=inf_rule)
    return render_template('step_review.html')

@app.route('/accept_step_or_modify_step/<name_of_derivation>/', methods=['GET', 'POST'])
def accept_step_or_modify_step(name_of_derivation):
    if request.method == 'POST':
        if request.form['accept and add or accept and return to derivation or modify']=='accept and review derivation':
            render_template('review_derivation.html')
        elif request.form['accept and add or accept and return to derivation or modify']=='modify this step':
            render_template('modify_step.html')
        elif request.form['accept and add or accept and return to derivation or modify']=='accept and add another step':
            render_template('select_inference_rule.html')
        else:
            raise Exception('undefined choice in form')
    else:
        raise Exception('submit form to get to this page')

@app.route('/review_derivation/<name_of_derivation>/', methods=['GET', 'POST'])
def review_derivation(name_of_derivation):

    return render_template('review_derivation.html')

@app.route('/modify_step/<name_of_derivation>/', methods=['GET', 'POST'])
def modify_step(name_of_derivation):
    return render_template('modify_step.html')


@app.route('/enter_equation/', methods=['GET', 'POST'])
def create_eq_as_png():
    form = EquationInputForm(request.form)
    if request.method == 'POST' and form.validate():
        latex_as_str = form.latex.data
        #latex_stdout,latex_stderr,png_stdout,png_stderr,name_of_png = compute_latex(latex_as_str,print_debug)
        name_of_png = compute.create_png_from_latex(latex_as_str,print_debug)
        compute.add_latex_to_sql("app/sqlite.db",latex_as_str,print_debug)
        return render_template("view_output.html", #form=form, #s=s, 
                               #latex_stdout=latex_stdout,latex_stderr=latex_stderr,
                               #png_stdout=png_stdout,png_stderr=png_stderr,
                               name_of_png=name_of_png)
    else:
        return render_template("view_input.html", form=form)

if __name__ == '__main__':
    print_debug=False
    app.run(debug=True, host='0.0.0.0')

