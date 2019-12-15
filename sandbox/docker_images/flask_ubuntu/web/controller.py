#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html

from flask import Flask, redirect, render_template, request, url_for
from wtforms import Form, StringField, FloatField, validators, FieldList, FormField
import compute 
from config import Config # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

global print_trace
print_trace = True

app = Flask(__name__, static_folder='static')
app.config.from_object(Config) # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

class EquationInputForm(Form):
    if print_trace: print('[trace] controller: class = EquationInputForm')
#    r = FloatField(validators=[validators.InputRequired()])
#    r = FloatField()
    latex = StringField('LaTeX',validators=[validators.InputRequired()])

class infRuleInputsAndOutputs(Form):
    if print_trace: print('[trace] controller: class = infRuleInputsAndOutputs')
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
    if print_trace: print('[trace] controller: class = LatexIO')
    feed1   = StringField('feed LaTeX 1',  validators=[validators.InputRequired()])
    feed2   = StringField('feed LaTeX 2',  validators=[validators.InputRequired()])
    feed3   = StringField('feed LaTeX 3',  validators=[validators.InputRequired()])
    input1  = StringField('input LaTeX 1', validators=[validators.InputRequired()])
    input2  = StringField('input LaTeX 2', validators=[validators.InputRequired()])
    input3  = StringField('input LaTeX 3', validators=[validators.InputRequired()])
    output1 = StringField('output LaTeX 1',validators=[validators.InputRequired()])
    output2 = StringField('output LaTeX 2',validators=[validators.InputRequired()])
    output3 = StringField('output LaTeX 3',validators=[validators.InputRequired()])

class NameOfDerivationInputForm(Form):
    if print_trace: print('[trace] controller: class = NameOfDerivationInputForm')
    name_of_derivation = StringField(validators=[validators.InputRequired()])

# goal is to prevent cached responses; 
# see https://stackoverflow.com/questions/47376744/how-to-prevent-cached-response-flask-server-using-chrome
# The following doesn't work; instead use "F12 > Network > Disable cache"
#@app.after_request
#def add_header(r):
#    """
#    Add headers to both force latest IE rendering engine or Chrome Frame,
#    and also to cache the rendered page for 10 minutes.
#    """
#    if print_trace: print('[trace] controller: add_header')
#    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    r.headers["Pragma"] = "no-cache"
#    r.headers["Expires"] = "0"
#    r.headers['Cache-Control'] = 'public, max-age=0'
#    return r

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
    if print_trace: print('[trace] controller: index')
    return render_template('index.html')

@app.route('/start_new_derivation/', methods=['GET', 'POST'])
def start_new_derivation():
    if print_trace: print('[trace] controller: start_new_derivation')
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
    if print_trace: print('[trace] controller: edit_existing_derivation')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')
    return render_template("edit_existing_derivation.html",
                           derivations_dict=derivations_dict)

@app.route('/edit_inference_rule', methods=['GET', 'POST'])
def edit_inference_rule():
    if print_trace: print('[trace] controller: edit_inference_rule')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')

    return render_template("edit_inference_rule.html",
                           inf_rules_dict=inf_rules_dict)

@app.route('/edit_expression', methods=['GET', 'POST'])
def edit_expression():
    if print_trace: print('[trace] controller: edit_expression')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')
    return render_template('edit_expression.html',
                           expressions_dict=expressions_dict)

@app.route('/list_all_inference_rules', methods=['GET', 'POST'])
def list_all_inference_rules():
    if print_trace: print('[trace] controller: list_all_inference_rules')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')
    return render_template("list_all_inference_rules.html",
                           inf_rules_dict=inf_rules_dict)

@app.route('/select_derivation_to_edit', methods=['GET', 'POST'])
def select_derivation_to_edit():
    if print_trace: print('[trace] controller: select_derivation_to_edit')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')
    return render_template("select_derivation_to_edit.html",
                           derivations_dict=derivations_dict)

@app.route('/select_derivation_step_to_edit', methods=['GET', 'POST'])
def select_derivation_step_to_edit():
    if print_trace: print('[trace] controller: select_derivation_step_to_edit')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')
    return render_template("select_derivation_step_to_edit.html",
                           derivations_dict=derivations_dict)

@app.route('/list_all_expressions', methods=['GET', 'POST'])
def list_all_expressions():
    if print_trace: print('[trace] controller: list_all_expressions')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')
    return render_template("list_all_expressions.html",
                           expressions_dict=expressions_dict)


@app.route('/view_existing_derivations', methods=['GET', 'POST'])
def view_existing_derivations():
    if print_trace: print('[trace] controller: view_existing_derivations')
    expressions_dict, inf_rules_dict, derivations_dict = compute.read_db('data.pkl')
    return render_template("view_existing_derivations.html",
                           derivations_dict=derivations_dict)

@app.route('/select_inference_rule/<name_of_derivation>/', methods=['GET', 'POST'])
def select_inference_rule(name_of_derivation):
    if print_trace: print('[trace] controller: select_inference_rule')
    list_of_inf_rules = compute.get_list_of_inf_rules('data.pkl')

    return render_template("select_inference_rule.html",
                           title=name_of_derivation,
                           inf_rule_list=list_of_inf_rules,
                           name_of_derivation=name_of_derivation)


@app.route('/inf_rule_selected/<name_of_derivation>', methods=['GET', 'POST'])
def inf_rule_selected(name_of_derivation):
    """
    https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms
    """
    if print_trace: print('[trace] controller: inf_rule_selected')
    print('name of derivation=',name_of_derivation)
    selected_inf_rule = request.form.get('inf_rul_select') # this comes from the POST 
    num_feeds, num_inputs, num_outputs = compute.input_output_count_for_infrule(selected_inf_rule, 'data.pkl')
    return render_template('inf_rule_selected.html',
                            name_of_derivation=name_of_derivation,
                            number_of_feeds=int(num_feeds),
                            number_of_inputs=int(num_inputs),
                            number_of_outputs=int(num_outputs),
                            inf_rule=selected_inf_rule,
                            form=LatexIO(request.form))

@app.route('/step_review/<name_of_derivation>/<inf_rule>/', methods=['GET', 'POST'])
def step_review(name_of_derivation,inf_rule):
    """
    https://teamtreehouse.com/community/getting-data-from-wtforms-formfield
    """
    if print_trace: print('[trace] controller: step_review')
    if request.method == 'POST':
        latex_for_step_dict = request.form
        print('latex_for_step_dict = ',latex_for_step_dict) # form from inf_rule_selected()
        # looks like {'input1':'asdf', 'input2':'afdm','output1':'imfa'}
        # save this "step" information to database
        step_graphviz_png = compute.create_step(latex_for_step_dict, inf_rule, name_of_derivation, print_debug, 'data.pkl')

        return render_template("step_review.html",
                               name_of_graphviz_png=step_graphviz_png,
                               name_of_derivation=name_of_derivation,
                               inf_rule=inf_rule)
    else:
        print('controller: step_review -- reached else')
        return render_template('index.html')
    print('controller: step_review - reached end of function')
    return render_template('step_review.html')

#@app.route('/accept_step_or_modify_step/<name_of_derivation>/', methods=['GET', 'POST'])
#def accept_step_or_modify_step(name_of_derivation):
#    if print_trace: print('[trace] controller: accept_step_or_modify_step')
#    if request.method == 'POST':
#        #print('accept_step_or_modify_step POSTed')
#        #print(request)
#        print('request form:',request.form)
#        if request.form['accept and add or accept and return to derivation or modify']=='accept and review derivation':
#            print('accept and review')
#            return render_template('review_derivation.html',
#                                   name_of_derivation=name_of_derivation)
#        elif request.form['accept and add or accept and return to derivation or modify']=='modify this step':
#            print('modify step')
#            return render_template('modify_step.html')
#        elif request.form['accept and add or accept and return to derivation or modify']=='accept and add another step':
#            print('accept and add')
#            return render_template('select_inference_rule.html')
#        else:
#            raise Exception('undefined choice in form')
#    else:
#        print('accept_step_or_modify_step: GET?')
#        return render_template('index.html')
#        #raise Exception('submit form to get to this page')
#    print('accept_step_or_modify_step -- returning')
#    return rander_template('index.html')

@app.route('/review_derivation/<name_of_derivation>/', methods=['GET', 'POST'])
def review_derivation(name_of_derivation):
    if print_trace: print('[trace] controller: review_derivation')
    if request.method == 'POST':
        derivation_png = compute.create_derivation_png(name_of_derivation, print_debug, 'data.pkl')
        return render_template('review_derivation.html',
                               name_of_derivation=name_of_derivation,
                               name_of_graphviz_png=derivation_png)
    else:
        return render_template('index.html')

@app.route('/modify_step/<name_of_derivation>/', methods=['GET', 'POST'])
def modify_step(name_of_derivation):
    if print_trace: print('[trace] controller: modify_step')
    if request.method == 'POST':
        print('request form:',request.form)
    return render_template('modify_step.html')


#@app.route('/enter_equation/', methods=['GET', 'POST'])
#def create_eq_as_png():
#    if print_trace: print('[trace] controller: create_eq_as_png')
#    form = EquationInputForm(request.form)
#    if request.method == 'POST' and form.validate():
#        latex_as_str = form.latex.data
#        #latex_stdout,latex_stderr,png_stdout,png_stderr,name_of_png = compute_latex(latex_as_str,print_debug)
#        name_of_png = compute.create_png_from_latex(latex_as_str,print_debug)
#        compute.add_latex_to_sql("app/sqlite.db",latex_as_str,print_debug)
#        return render_template("view_output.html", #form=form, #s=s, 
#                               #latex_stdout=latex_stdout,latex_stderr=latex_stderr,
#                               #png_stdout=png_stdout,png_stderr=png_stderr,
#                               name_of_png=name_of_png)
#    else:
#        return render_template("view_input.html", form=form)

if __name__ == '__main__':
    print_debug = False
    print_trace = True
    app.run(debug=True, host='0.0.0.0')

