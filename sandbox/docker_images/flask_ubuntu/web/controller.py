# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html

from flask import Flask, render_template, request
from wtforms import Form, StringField, FloatField, validators
from compute import compute_sine, compute_latex

app = Flask(__name__)

# Model
class InputForm(Form):
#    r = FloatField(validators=[validators.InputRequired()])
#    r = FloatField()
    latex = StringField(validators=[validators.InputRequired()])

# View
@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
#        r = form.r.data
        latex = form.latex.data
#        s = compute_sine(r)
        latex_stdout,latex_stderr,png_stdout,png_stderr,name_of_png = compute_latex(latex,print_debug)
        return render_template("view_output.html", form=form, #s=s, 
                               latex_stdout=latex_stdout,latex_stderr=latex_stderr,
                               png_stdout=png_stdout,png_stderr=png_stderr,name_of_png=name_of_png)
    else:
        return render_template("view_input.html", form=form)

if __name__ == '__main__':
    print_debug=False
    app.run(debug=True, host='0.0.0.0')

