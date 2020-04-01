#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html

# convention: every function and class includes a [trace] print
# to help the developer understand functional dependencies and which state the program is in,
# a "trace" is printed to the terminal at the start of each function

import os
import json
import shutil
import logging  # https://docs.python.org/3/howto/logging.html

from flask import Flask, redirect, render_template, request, url_for, flash
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, validators, FieldList, FormField, IntegerField  # type: ignore
from jsonschema import validate  # type: ignore
from config import (
    Config,
)  # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

import common_lib as clib  # PDG common library
import json_schema  # PDG
import compute  # PDG
import validate_inference_rules_sympy as vir  # PDG

#global proc_timeout
proc_timeout = 30

app = Flask(__name__, static_folder="static")
app.config.from_object(
    Config
)  # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
app.config[
    "UPLOAD_FOLDER"
] = "/home/appuser/app/uploads"  # https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
app.config[
    "SEND_FILE_MAX_AGE_DEFAULT"
] = 0  # https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


if __name__ == "__main__":
    # called from flask

    # https://docs.python.org/3/howto/logging.html
    logging.basicConfig(  # filename='pdg.log',
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s|%(filename)-13s|%(levelname)-5s|%(lineno)-4d|%(funcName)-20s|%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    logger = logging.getLogger(__name__)


# https://stackoverflow.com/questions/41087790/how-to-override-gunicorns-logging-config-to-use-a-custom-formatter
# https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
if __name__ != "__main__":
    # called from gunicorn

    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    logger = app.logger

class EquationInputForm(Form):
    logger.info("[trace] class = EquationInputForm")
    #    r = FloatField(validators=[validators.InputRequired()])
    #    r = FloatField()
    latex = StringField("LaTeX", validators=[validators.InputRequired()])


class InferenceRuleForm(Form):
    logger.info("[trace] class = InferenceRuleForm")
    inf_rule_name = StringField(
        "inf rule name", validators=[validators.InputRequired()]
    )
    num_inputs = IntegerField(
        "number of inputs",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=5)],
    )
    num_feeds = IntegerField(
        "number of feeds",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=5)],
    )
    num_outputs = IntegerField(
        "number of outputs",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=5)],
    )
    latex = StringField("LaTeX", validators=[validators.InputRequired()])


class RevisedTextForm(Form):
    logger.info("[trace] class = RevisedTextForm")
    revised_text = StringField("revised text", validators=[validators.InputRequired()])


class infRuleInputsAndOutputs(Form):
    logger.info("[trace] class = infRuleInputsAndOutputs")
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
    inputs_and_outputs = FieldList(
        FormField(EquationInputForm, "late_x"), min_entries=1
    )


#    inputs_and_outputs = FieldList(EquationInputForm, min_entries=1)

# https://stackoverflow.com/questions/37837682/python-class-input-argument/37837766
class LatexIO(Form):
    logger.info("[trace] class = LatexIO")
    feed1 = StringField("feed LaTeX 1", validators=[validators.InputRequired()])
    feed2 = StringField("feed LaTeX 2", validators=[validators.InputRequired()])
    feed3 = StringField("feed LaTeX 3", validators=[validators.InputRequired()])
    input1 = StringField("input LaTeX 1", validators=[validators.InputRequired()])
    input2 = StringField("input LaTeX 2", validators=[validators.InputRequired()])
    input3 = StringField("input LaTeX 3", validators=[validators.InputRequired()])
    output1 = StringField("output LaTeX 1", validators=[validators.InputRequired()])
    output2 = StringField("output LaTeX 2", validators=[validators.InputRequired()])
    output3 = StringField("output LaTeX 3", validators=[validators.InputRequired()])


class NameOfDerivationInputForm(Form):
    logger.info("[trace] class = NameOfDerivationInputForm")
    name_of_derivation = StringField(validators=[validators.InputRequired()])


# goal is to prevent cached responses;
# see https://stackoverflow.com/questions/47376744/how-to-prevent-cached-response-flask-server-using-chrome
# The following doesn't work; instead use "F12 > Network > Disable cache"
# @app.after_request
# def add_header(r):
#    """
#    Add headers to both force latest IE rendering engine or Chrome Frame,
#    and also to cache the rendered page for 10 minutes.
#    """
#    logger.info('[trace] add_header')
#    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    r.headers["Pragma"] = "no-cache"
#    r.headers["Expires"] = "0"
#    r.headers['Cache-Control'] = 'public, max-age=0'
#    return r


@app.errorhandler(404)
def page_not_found(e):
    """
    https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """
    logger.info("[trace] page_not_found")
    logger.debug(e)
    return redirect(url_for("index"))


@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    """
    index.html contains hyperlinks to pages like:
    * start new derivation
    * edit existing derivation
    * edit inference rule
    * view existing derivations

    file upload: see https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
    """
    logger.info("[trace] index")

    try:
        logger.debug("session id = %s", session_id)
    except NameError:
        logger.warning("session id does not appear to exist")
        session_id = compute.create_session_id()
        logger.debug("now the session id = %s", session_id)

    shutil.copy("data.json", "/home/appuser/app/static/")

    all_df = compute.convert_json_to_dataframes("data.json")
    df_pkl_file = compute.convert_df_to_pkl(all_df)
    sql_file = compute.convert_dataframes_to_sql(all_df)
    shutil.copy(sql_file, "/home/appuser/app/static/")

    rdf_file = compute.convert_data_to_rdf("data.json")
    shutil.copy(rdf_file, "/home/appuser/app/static/")

    neo4j_file = compute.convert_data_to_cypher("data.json")
    shutil.copy(neo4j_file, "/home/appuser/app/static/")

    logger.debug("index; request.method = %s", request.method)

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        # ImmutableMultiDict([('file', <FileStorage: 'prospector_output.json' ('application/json')>)])

        # check if the post request has the file part
        if "file" not in request.files:
            logger.debug("flash for file not in request files")
            flash("No file part")
            return redirect(request.url)
        file_obj = request.files["file"]

        logger.debug(request.files)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file_obj.filename == "":
            logger.debug("flash no selected file")
            flash("No selected file")
            return redirect(request.url)
        if file_obj and compute.allowed_file(file_obj.filename):
            filename = secure_filename(file_obj.filename)
            logger.debug("filename = %s", filename)
            path_to_uploaded_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file_obj.save(path_to_uploaded_file)

            if not compute.validate_json_file(path_to_uploaded_file):
                flash("uploaded file does not match PDG schema")
            else:  # file exists, has .json extension, is JSON, and complies with schema
                shutil.copy(path_to_uploaded_file, "/home/appuser/app/data.json")
            return redirect(url_for("index", filename=filename))

    logger.debug("reading from json")
    dat = clib.read_db("data.json")
    return render_template(
        "index.html",
        number_of_derivations=len(dat["derivations"].keys()),
        number_of_infrules=len(dat["inference rules"].keys()),
        number_of_expressions=len(dat["expressions"].keys()),
        number_of_symbols=len(dat["symbols"].keys()),
        number_of_operators=len(dat["operators"].keys()),
        database_json="data.json",
        database_df_pkl=df_pkl_file,
        database_sql=sql_file,
        database_neo4j=neo4j_file,
        database_rdf=rdf_file,
    )


@app.route("/start_new_derivation/", methods=["GET", "POST"])
def start_new_derivation():
    logger.info("[trace] start_new_derivation")
    web_form = NameOfDerivationInputForm(request.form)
    if request.method == "POST" and web_form.validate():
        name_of_derivation = str(web_form.name_of_derivation.data)
        logger.debug(
            "start_new_derivation: name of derivation = %s",
            name_of_derivation,
        )
        return redirect(
            url_for("new_step_select_inf_rule", name_of_derivation=name_of_derivation)
        )
    return render_template(
        "start_new_derivation.html", form=web_form, title="start new derivation"
    )


# @app.route('/edit_expression', methods=['GET', 'POST'])
# def edit_expression():
#    logger.info('[trace] edit_expression')
#    return render_template('edit_expression.html',
#                           expressions_dict=expressions_dict)


@app.route("/list_all_operators", methods=["GET", "POST"])
def list_all_operators():
    logger.info("[trace] list_all_operators")
    dat = clib.read_db("data.json")
    operator_popularity_dict = compute.popularity_of_operators("data.json")

    if request.method == "POST":
        logger.debug(
            "request.form = %s", request.form
        )
    return render_template(
        "list_all_operators.html",
        operators_dict=dat["operators"],
        operator_popularity_dict=operator_popularity_dict,
    )


@app.route("/list_all_symbols", methods=["GET", "POST"])
def list_all_symbols():
    logger.info("[trace] list_all_symbols")
    dat = clib.read_db("data.json")
    symbol_popularity_dict = compute.popularity_of_symbols("data.json")

    if request.method == "POST":
        logger.debug(
            "list_all_symbolss; request.form = %s", request.form
        )
    return render_template(
        "list_all_symbols.html",
        symbols_dict=dat["symbols"],
        symbol_popularity_dict=symbol_popularity_dict,
    )


@app.route("/list_all_expressions", methods=["GET", "POST"])
def list_all_expressions():
    logger.info("[trace] list_all_expressions")
    dat = clib.read_db("data.json")
    expression_popularity_dict = compute.popularity_of_expressions("data.json")
    if request.method == "POST":
        logger.debug(
            "list_all_expressions; request.form = %s", request.form
        )
        if "edit_expr_latex" in request.form.keys():
            # request.form = ImmutableMultiDict([('edit_expr_latex', '4928923942'), ('revised_text', 'asdfingasinsf')])
            status_message = compute.edit_expr_latex(
                request.form["edit_expr_latex"],
                request.form["revised_text"],
                "data.json",
            )
            flash(status_message)
            logger.debug(
                "list_all_expressions; status = %s", status_message
            )
            return redirect(url_for("list_all_expressions"))
        elif "delete_expr" in request.form.keys():
            # request.form = ImmutableMultiDict([('delete_expr', '4928923942')])
            status_message = compute.delete_expr(
                request.form["delete_expr"], "data.json"
            )
            flash(status_message)
            logger.debug(
                "list_all_expressions; status = %s", status_message
            )
            return redirect(url_for("list_all_expressions"))
    list_of_expr = compute.get_sorted_list_of_expr("data.json")
    list_of_expr_not_appearing_in_any_derivations = compute.expr_not_in_derivations(
        "data.json"
    )
    return render_template(
        "list_all_expressions.html",
        expressions_dict=dat["expressions"],
        sorted_list_exprs=list_of_expr,
        list_of_expr_not_appearing_in_any_derivations=list_of_expr_not_appearing_in_any_derivations,
        edit_expr_latex_webform=RevisedTextForm(request.form),
        expression_popularity_dict=expression_popularity_dict,
    )


@app.route("/list_all_inference_rules", methods=["GET", "POST"])
def list_all_inference_rules():
    logger.info("[trace] list_all_inference_rules")
    dat = clib.read_db("data.json")
    infrule_popularity_dict = compute.popularity_of_infrules("data.json")
    if request.method == "POST":
        logger.debug(
            "list_all_inference_rules; request.form = %s",
            request.form,
        )
        if "inf_rule_name" in request.form.keys():
            # request.form = ImmutableMultiDict([('inf_rule_name', 'testola'), ('num_inputs', '1'), ('num_feeds', '0'), ('num_outputs', '0'), ('latex', 'adsfmiangasd')])
            status_message = compute.add_inf_rule(request.form.to_dict(), "data.json")
            flash(status_message)
            # https://stackoverflow.com/a/31945712/1164295
            return redirect(url_for("list_all_inference_rules"))
        elif "delete_inf_rule" in request.form.keys():
            # request.form = ImmutableMultiDict([('delete_inf_rule', 'asdf')])
            status_message = compute.delete_inf_rule(
                request.form["delete_inf_rule"], "data.json"
            )
            flash(status_message)
            logger.debug(
                "list_all_inference_rules; status = %s",
                status_message,
            )
            return redirect(url_for("list_all_inference_rules"))
        elif "rename_inf_rule_from" in request.form.keys():
            # request.form = ImmutableMultiDict([('rename_inf_rule_from', 'asdf'), ('revised_text', 'anotehr')])
            status_message = compute.rename_inf_rule(
                request.form["rename_inf_rule_from"],
                request.form["revised_text"],
                "data.json",
            )
            flash(status_message)
            logger.debug(
                "list_all_inference_rules; status = %s",
                status_message,
            )
            return redirect(url_for("list_all_inference_rules"))
        elif "edit_inf_rule_latex" in request.form.keys():
            # request.form = ImmutableMultiDict([('edit_inf_rule_latex', 'asdf'), ('revised_text', 'great works')])
            status_message = compute.edit_inf_rule_latex(
                request.form["edit_inf_rule_latex"],
                request.form["revised_text"],
                "data.json",
            )
            flash(status_message)
            logger.debug(
                "list_all_inference_rules; status = %s",
                status_message,
            )
            return redirect(url_for("list_all_inference_rules"))
        else:
            flash("unrecognized form result")
            logger.warning("ERROR: unrecognized form result")

    return render_template(
        "list_all_inference_rules.html",
        infrules_dict=dat["inference rules"],
        sorted_list_infrules=compute.get_sorted_list_of_inf_rules("data.json"),
        add_infrule_webform=InferenceRuleForm(request.form),
        rename_infrule_webform=RevisedTextForm(request.form),
        edit_infrule_latex_webform=RevisedTextForm(request.form),
        infrule_popularity_dict=infrule_popularity_dict,
    )


@app.route("/select_derivation_to_edit", methods=["GET", "POST"])
def select_derivation_to_edit():
    logger.info("[trace] select_derivation_to_edit")
    if request.method == "POST":
        logger.debug(
            "select_derivation_to_edit; request.form = %s",
            request.form,
        )
    return render_template(
        "select_derivation_to_edit.html",
        derivations_list=compute.get_sorted_list_of_derivations("data.json"),
    )


@app.route(
    "/select_derivation_step_to_edit/<name_of_derivation>/", methods=["GET", "POST"]
)
def select_derivation_step_to_edit(name_of_derivation: str):
    logger.info("[trace] select_derivation_step_to_edit")
    steps_dict = compute.get_derivation_steps(name_of_derivation, "data.json")
    if request.method == "POST":
        logger.debug(
            "select_derivation_step_to_edit; request.form = %s",
            request.form,
        )
    return render_template(
        "select_derivation_step_to_edit.html",
        name_of_derivation=name_of_derivation,
        steps_dict=steps_dict,
        list_of_step_ids=steps_dict.keys(),
    )


@app.route("/select_from_existing_derivations", methods=["GET", "POST"])
def select_from_existing_derivations():
    logger.info("[trace] select_from_existing_derivations")
    list_of_deriv = compute.get_sorted_list_of_derivations("data.json")
    if request.method == "POST":
        logger.debug(
            "select_from_existing_derivations; request.form = %s", request.form
        )

        # dropdown menu provides a derivation selected
        if "derivation_selected" in request.form.keys():
            name_of_derivation = request.form["derivation_selected"]
        else:  # no derivations exist
            return redirect(url_for("index"))

        if request.form["submit_button"] == "generate_pdf":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'generate_pdf')])
            pdf_filename = compute.generate_pdf_for_derivation(
                name_of_derivation, "data.json"
            )

            return redirect(url_for("static", filename=pdf_filename))
            # return redirect(url_for('review_derivation',
            #                  pdf_filename=pdf_filename,
            #                  name_of_derivation=name_of_derivation))

        elif request.form["submit_button"] == "display_graphviz":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'display_graphviz')])
            return redirect(
                url_for(
                    "review_derivation",
                    pdf_filename="NONE",
                    name_of_derivation=name_of_derivation,
                )
            )
        else:
            raise Exception("unrecongized button in", request.form)

    return render_template(
        "select_from_existing_derivations.html", list_of_derivations=list_of_deriv
    )


@app.route("/new_step_select_inf_rule/<name_of_derivation>/", methods=["GET", "POST"])
def new_step_select_inf_rule(name_of_derivation: str):
    logger.info("[trace] new_step_select_inf_rule")
    list_of_inf_rules = compute.get_sorted_list_of_inf_rules("data.json")

    if (
        request.method == "POST"
    ):  # and request.form.validate(): no validation because the form was defined on the web page
        logger.debug("new_step_select_inf_rule: %s", request.form)
        selected_inf_rule = request.form.get("inf_rul_select")
        logger.debug(
            "new_step_select_inf_rule; selected_inf_rule = %s",
            selected_inf_rule,
        )
        return redirect(
            url_for(
                "provide_expr_for_inf_rule",
                name_of_derivation=name_of_derivation,
                inf_rule=selected_inf_rule,
            )
        )

    return render_template(
        "new_step_select_inf_rule.html",
        title=name_of_derivation,
        inf_rule_list=list_of_inf_rules,
        name_of_derivation=name_of_derivation,
    )


@app.route(
    "/provide_expr_for_inf_rule/<name_of_derivation>/<inf_rule>",
    methods=["GET", "POST"],
)
def provide_expr_for_inf_rule(name_of_derivation: str, inf_rule: str):
    """
    https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms

    >>> provide_expr_for_inf_rule()
    """

    logger.info("[trace] provide_expr_for_inf_rule")
    # num_feeds, num_inputs, num_outputs = compute.input_output_count_for_infrule(inf_rule, 'data.json')
    # logger.debug('provide_expr_for_inf_rule;',num_feeds,'feeds,',num_inputs,'inputs, and',num_outputs,'outputs')

    dat = clib.read_db("data.json")

    if (
        request.method == "POST"
    ):  # and request.form.validate(): no validation because the form was defined on the web page
        latex_for_step_dict = request.form

        logger.debug("request.form = %s", request.form)
        # request.form = ImmutableMultiDict([('input1', 'a = b'), ('submit_button', 'Submit')])

        # request.form = ImmutableMultiDict([('input1', 'asfd'), ('use_ID_for_in1', 'on'), ('submit_button', 'Submit')])

        # request.form = ImmutableMultiDict([('input1', '1492842000'), ('use_ID_for_in1', 'on'), ('feed1', 'a'), ('feed2', 'b'), ('feed3', 'c'), ('output1', 'asdf = asf'), ('submit_button', 'Submit')])

        logger.debug(
            "provide_expr_for_inf_rule: latex_for_step_dict = %s",
            latex_for_step_dict,
        )
        local_step_id = compute.create_step(
            latex_for_step_dict, inf_rule, name_of_derivation, "data.json"
        )
        logger.debug(
            "provide_expr_for_inf_rule; local_step_id = %s",
            local_step_id,
        )

        step_validity_msg = vir.validate_step(
            name_of_derivation, local_step_id, "data.json"
        )

        return redirect(
            url_for(
                "step_review",
                step_validity_msg=step_validity_msg,
                name_of_derivation=name_of_derivation,
                local_step_id=local_step_id,
            )
        )

    # the following is needed to handle the case where the derivation is new and no steps exist yet
    if name_of_derivation in dat["derivations"].keys():
        step_dict = dat["derivations"][name_of_derivation]
        step_validity_dict = (
            compute.determine_step_validity(name_of_derivation, "data.json"),
        )

    else:
        step_dict = {}
        step_validity_dict = {}

    return render_template(
        "provide_expr_for_inf_rule.html",
        name_of_derivation=name_of_derivation,
        inf_rule_dict=dat["inference rules"][inf_rule],
        step_dict=step_dict,
        step_validity_dict=step_validity_dict,
        expr_dict=dat["expressions"],
        expr_local_to_gobal=dat["expr local to global"],
        webform=LatexIO(request.form),
    )


@app.route(
    "/step_review/<name_of_derivation>/<local_step_id>/<step_validity_msg>",
    methods=["GET", "POST"],
)
def step_review(name_of_derivation: str, local_step_id: str, step_validity_msg: str):
    """
    https://teamtreehouse.com/community/getting-data-from-wtforms-formfield

    >>> step_review
    """
    logger.info("[trace] step_review")

    (
        valid_latex_bool,
        invalid_latex,
        step_graphviz_png,
    ) = compute.create_step_graphviz_png(name_of_derivation, local_step_id, "data.json")
    if not valid_latex_bool:
        logger.debug(
            "step_review; invalid latex detected %s", invalid_latex
        )
        # TODO: now what?

    dat = clib.read_db("data.json")

    if request.method == "POST":
        reslt = request.form
        logger.debug("step_review: reslt = %s", reslt)
        if request.form["submit_button"] == "accept this step; add another step":
            return redirect(
                url_for(
                    "new_step_select_inf_rule", name_of_derivation=name_of_derivation
                )
            )
        if request.form["submit_button"] == "accept this step; review derivation":
            return redirect(
                url_for(
                    "review_derivation",
                    pdf_filename="NONE",
                    name_of_derivation=name_of_derivation,
                )
            )
        elif request.form["submit_button"] == "modify this step":
            return redirect(
                url_for(
                    "modify_step",
                    name_of_derivation=name_of_derivation,
                    step_id=local_step_id,
                )
            )
        else:
            raise Exception('unrecognized button in "step_review":', request.form)

    return render_template(
        "step_review.html",
        step_validity_msg=step_validity_msg,
        name_of_graphviz_png=step_graphviz_png,
        name_of_derivation=name_of_derivation,
        step_dict=dat["derivations"][name_of_derivation],
        expr_dict=dat["expressions"],
        step_validity_dict=compute.determine_step_validity(
            name_of_derivation, "data.json"
        ),
        expr_local_to_gobal=dat["expr local to global"],
    )


@app.route(
    "/review_derivation/<name_of_derivation>/<pdf_filename>/", methods=["GET", "POST"]
)
def review_derivation(name_of_derivation: str, pdf_filename: str):
    """
    >>> review_derivation
    """
    logger.info("[trace] review_derivation")
    if request.method == "POST":
        if request.form["submit_button"] == "add another step":
            return redirect(
                url_for(
                    "new_step_select_inf_rule", name_of_derivation=name_of_derivation
                )
            )
        elif request.form["submit_button"] == "edit existing step":
            return redirect(
                url_for(
                    "select_derivation_step_to_edit",
                    name_of_derivation=name_of_derivation,
                )
            )
        elif request.form["submit_button"] == "return to main menu":
            return redirect(url_for("index"))
        elif request.form["submit_button"] == "generate pdf":
            pdf_filename = compute.generate_pdf_for_derivation(
                name_of_derivation, "data.json"
            )
            return redirect(url_for("static", filename=pdf_filename))
        elif request.form["submit_button"] == "delete derivation":
            msg = compute.delete_derivation(name_of_derivation, "data.json")
            flash(msg)
            return redirect(url_for("index"))
        else:
            raise Exception(
                "[ERROR] compute; review_derivation; unrecognized button:", request.form
            )

    valid_latex_bool, invalid_latex, derivation_png = compute.create_derivation_png(
        name_of_derivation, "data.json"
    )

    dat = clib.read_db("data.json")

    return render_template(
        "review_derivation.html",
        pdf_filename=pdf_filename,
        name_of_derivation=name_of_derivation,
        name_of_graphviz_png=derivation_png,
        step_dict=dat["derivations"][name_of_derivation],
        step_validity_dict=compute.determine_step_validity(
            name_of_derivation, "data.json"
        ),
        expr_dict=dat["expressions"],
        expr_local_to_gobal=dat["expr local to global"],
    )


@app.route("/modify_step/<name_of_derivation>/<step_id>/", methods=["GET", "POST"])
def modify_step(name_of_derivation: str, step_id: str):
    """
    >>>
    """
    logger.info("[trace] modify_step")

    (
        valid_latex_bool,
        invalid_latex,
        step_graphviz_png,
    ) = compute.create_step_graphviz_png(name_of_derivation, step_id, "data.json")
    if not valid_latex_bool:
        logger.debug("invalid latex %s", invalid_latex)
        # TODO: now what?

    # steps_dict = compute.get_derivation_steps(name_of_derivation, 'data.json')
    # this_step = steps_dict[step_id]
    dat = clib.read_db("data.json")
    if request.method == "POST":
        logger.debug("modify_step; request form = %s", request.form)
        if request.form["submit_button"] == "change inference rule":
            return redirect(
                url_for(
                    "new_step_select_inf_rule", name_of_derivation=name_of_derivation
                )
            )
        elif "expr_local_id_of_latex_to_modify" in request.form.keys():
            # request form = ImmutableMultiDict([('edit_expr_latex', '2244'), ('revised_text', 'a = b')])
            compute.modify_latex_in_step(
                request.form["expr_local_id_of_latex_to_modify"],
                request.form["revised_text"],
                "data.json",
            )
            return redirect(
                url_for(
                    "step_review",
                    name_of_derivation=name_of_derivation,
                    local_step_id=step_id,
                    step_validity_msg=vir.validate_step(
                        name_of_derivation, step_id, "data.json"
                    ),
                )
            )

        else:
            raise Exception(
                "[ERROR] compute; review_derivation; unrecognized button:", request.form
            )

    return render_template(
        "modify_step.html",
        name_of_derivation=name_of_derivation,
        name_of_graphviz_png=step_graphviz_png,
        step_dict=dat["derivations"][name_of_derivation][step_id],
        local_to_global=dat["expr local to global"],
        expr_dict=dat["expressions"],
        edit_expr_latex_webform=RevisedTextForm(request.form),
        expr_local_to_gobal=dat["expr local to global"],
    )


@app.route("/create_new_inf_rule/", methods=["GET", "POST"])
def create_new_inf_rule():
    """
    >>>
    """
    logger.info("[trace] create_new_inf_rule")
    if request.method == "POST":
        logger.debug(
            "create_new_inf_rule; request.form = %s", request.form
        )
    return render_template("create_new_inf_rule.html")


if __name__ == "__main__":
    session_id = compute.create_session_id()

    app.run(debug=True, host="0.0.0.0")

# EOF
