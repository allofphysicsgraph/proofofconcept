#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for
)

app = Flask(__name__, static_folder="static")
app.config.from_object(
    Config
)  # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
app.config["DEBUG"] = True

@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    """
    the index is a static page intended to be the landing page for new users
    >>> index()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    try:
        d3js_json_filename = compute.create_d3js_json("884319", path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        d3js_json_filename = ""
    dat = clib.read_db(path_to_db)

    logger.info("[trace page end " + trace_id + "]")
    return render_template("index.html", json_for_d3js=d3js_json_filename)

if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0")

# EOF
