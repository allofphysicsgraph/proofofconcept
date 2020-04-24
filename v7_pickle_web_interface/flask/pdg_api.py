#!/usr/bin/env python3

# this trick only works for flask; not for gunicorn
from __main__ import app
import common_lib as clib
from flask import jsonify, request
path_to_db = "pdg.db"


@app.route("/api/v1/resources/derivations/all", methods=["GET"])
def api_all_derivations():
    """
    return the entire "derivations" dict
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["derivations"])


@app.route("/api/v1/resources/derivations/list", methods=["GET"])
def api_list_derivations():
    """
    list derivation names
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["derivations"].keys()))


@app.route("/api/v1/resources/derivations", methods=["GET"])
def api_read_derivation_by_name():
    """
    return a single derivation

    /api/v1/resources/derivations?name=curl%20curl%20identity

    https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "name" in request.args:
        name = str(request.args["name"])
    else:
        return "Error: No name field provided. Please specify a derivation name."
    if name in dat["derivations"].keys():
        return jsonify(dat["derivations"][name])
    else:
        return (
            "Error: derivation with name "
            + name
            + " not found in derivations; see derivations/list"
        )



@app.route("/api/v1/resources/expressions/all", methods=["GET"])
def api_all_expressions():
    """
    return the entire "expressions" dict
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["expressions"])

@app.route("/api/v1/resources/expressions/list", methods=["GET"])
def api_list_expressions():
    """
    list the expression global IDs
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["expressions"].keys()))


@app.route("/api/v1/resources/expressions", methods=["GET"])
def api_read_expression_by_id():
    """
    return a single expression

    /api/v1/resources/expressions?global_id=9999999953

    https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "global_id" in request.args:
        global_id = str(request.args["global_id"])
    else:
        return "Error: No global_id field provided. Please specify a global_id for the expression."
    if global_id in dat["expressions"].keys():
        return jsonify(dat["expressions"][global_id])
    else:
        return (
            "Error: expression with global_id "
            + global_id
            + " not found see expressions/list"
        )


@app.route("/api/v1/resources/infrules/all", methods=["GET"])
def api_all_infrules():
    """
    /api/v1/resources/infrules/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["inference rules"])


@app.route("/api/v1/resources/infrules/list", methods=["GET"])
def api_list_infrules():
    """
    /api/v1/resources/infrules/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["inference rules"].keys())


@app.route("/api/v1/resources/infrules", methods=["GET"])
def api_infrules_by_name():
    """
    /api/v1/resources/infrules?name=add%20zero%20to%20LHS
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "name" in request.args:
        name = str(request.args["name"])
    else:
        return "Error: no name field provided. Please specify a name for the inference rule."
    if name in dat["inference rules"].keys():
        return jsonify(dat["inference rules"][name])
    else:
        return "Error: expression with name " + name + " not found; see infrules/list"


@app.route("/api/v1/resources/local_to_global/all", methods=["GET"])
def api_all_local_to_global():
    """
    /api/v1/resources/local_to_global/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["expr local to global"])


@app.route("/api/v1/resources/local_to_global/list", methods=["GET"])
def api_list_local():
    """
    /api/v1/resources/local_to_global/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["expr local to global"].keys()))


@app.route("/api/v1/resources/local_to_global", methods=["GET"])
def api_local_to_global():
    """
    /api/v1/resources/local_to_global?local_id=8837284
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "local_id" in request.args:
        local_id = str(request.args["local_id"])
    else:
        return "Error: No local_id field provided. Please specify a local_id."
    if local_id in dat["expr local to global"].keys():
        return jsonify(dat["expr local to global"][local_id])
    else:
        return "Error: local_id " + local_id + " not found see local_to_global/list"


@app.route("/api/v1/resources/symbols/all", methods=["GET"])
def api_all_symbols():
    """
    /api/v1/resources/symbols/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["symbols"])


@app.route("/api/v1/resources/symbols/list", methods=["GET"])
def api_list_symbols():
    """
    /api/v1/resources/symbols/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["symbols"].keys()))


@app.route("/api/v1/resources/symbols", methods=["GET"])
def api_symbols_by_name():
    """
    /api/v1/resources/symbols?symbol_id=1223
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "symbol_id" in request.args:
        symbol_id = str(request.args["symbol_id"])
    else:
        return "Error: No symbol_id field provided. Please specify a symbol_id."
    if symbol_id in dat["symbols"].keys():
        return jsonify(dat["symbols"][symbol_id])
    else:
        return "Error: symbol_id " + symbol_id + " not found see symbols/list"


@app.route("/api/v1/resources/operators/all", methods=["GET"])
def api_all_operators():
    """
    /api/v1/resources/operators/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["symbols"])


@app.route("/api/v1/resources/operators/list", methods=["GET"])
def api_list_operators():
    """
    /api/v1/resources/operators/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["operators"].keys()))


@app.route("/api/v1/resources/operators", methods=["GET"])
def api_operators_by_name():
    """
    /api/v1/resources/operators?operator_id=equals
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "operator_id" in request.args:
        operator_id = str(request.args["operator_id"])
    else:
        return "Error: No operator_id field provided. Please specify a operator_id."
    if operator_id in dat["operators"].keys():
        return jsonify(dat["operators"][operator_id])
    else:
        return "Error: operator_id " + operator_id + " not found see symbols/list"

