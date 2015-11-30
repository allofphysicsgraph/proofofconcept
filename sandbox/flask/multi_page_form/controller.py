# https://github.com/hplgit/web4sciapps/blob/master/doc/src/web4sa/src-web4sa/apps/flask_apps/vib1/controller.py

from model import SelectInfRule,InfRuleArguments,AddAnotherStep
from flask import Flask, render_template, request
from compute import compute

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = AddAnotherStep(request.form)
    if request.method == 'POST' and form.validate():
        print form.addStep.data
        if (form.addStep.data=='y'):
            return render_template('choose_inf_rule_for_this_step.html')
        else:         
            return render_template('view_current_derivation.html', form=form)
    else:
        return render_template('view_current_derivation.html', form=form)

@app.route('/choose_inf_rule_for_this_step.html', methods=['GET', 'POST'])
def choose_inf_rule():
    form = SelectInfRule(request.form)
    return render_template('choose_inf_rule_for_this_step.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)

