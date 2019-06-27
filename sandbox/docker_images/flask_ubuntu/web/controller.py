# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html

from flask import Flask, render_template, request
from wtforms import Form, StringField, FloatField, validators
import compute 

app = Flask(__name__, static_folder='static')

class EquationInputForm(Form):
#    r = FloatField(validators=[validators.InputRequired()])
#    r = FloatField()
    latex = StringField(validators=[validators.InputRequired()])

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
        print(name_of_derivation)
        return render_template("select_inference_rule.html")
    else:
        return render_template("start_new_derivation.html",form=form)

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

@app.route('/select_inference_rule/', methods=['GET', 'POST'])
def select_inference_rule():
    """
    rather than a local list, 
    this function should poll the SQL database
    """
    list_of_inf_rules = ['add X to both sides','multiply both sides by X']

    return render_template("select_inference_rule.html",inf_rule_list=list_of_inf_rules)

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

