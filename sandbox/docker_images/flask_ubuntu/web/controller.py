# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html

from flask import Flask, render_template, request
from wtforms import Form, StringField, FloatField, validators
from compute import compute_sine, compute_latex

app = Flask(__name__, static_folder='static')

class InputForm(Form):
#    r = FloatField(validators=[validators.InputRequired()])
#    r = FloatField()
    latex = StringField(validators=[validators.InputRequired()])


# prevent cached responses; see https://stackoverflow.com/questions/47376744/how-to-prevent-cached-response-flask-server-using-chrome
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

