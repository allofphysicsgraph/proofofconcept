# https://github.com/hplgit/web4sciapps/blob/master/doc/src/web4sa/src-web4sa/apps/flask_apps/vib1/controller.py

from model import InputForm
from flask import Flask, render_template, request
from compute import compute

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
        result = compute(form.input_expression.data, 
                         form.inference_rule.data,
                         form.feed.data,
                         form.output_expression.data)
    else:
        result = None

    return render_template('view.html', form=form, result=result)

if __name__ == '__main__':
    app.run(debug=True)

