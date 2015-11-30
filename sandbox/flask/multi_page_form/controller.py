# https://github.com/hplgit/web4sciapps/blob/master/doc/src/web4sa/src-web4sa/apps/flask_apps/vib1/controller.py

from model import SelectInfRule,InfRuleArguments,AddAnotherStep
from flask import Flask, render_template, request, redirect, url_for
from compute import compute

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = AddAnotherStep(request.form)
    if request.method == 'POST' and form.validate():
        print form.addStep.data
        if (form.addStep.data=='y'):
            return redirect(url_for('choose_inf_rule'))
#             return render_template('choose_inf_rule_for_this_step.html')
    return render_template('view_current_derivation.html', form=form)

@app.route('/choose_inf_rule_for_this_step.html', methods=['GET', 'POST'])
def choose_inf_rule():
    form = SelectInfRule(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('provide_arguments_for_this_infrule'))
    return render_template('choose_inf_rule_for_this_step.html', form=form)
    
@app.route('/provide_arguments_for_this_infrule.html', methods=['GET', 'POST'])
def provide_arguments_for_this_infrule():
    form = InfRuleArguments(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('index'))
    return render_template('provide_arguments_for_this_infrule.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)

