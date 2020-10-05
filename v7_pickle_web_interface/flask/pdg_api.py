#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

"""
separate the API routes and functions into this file and thus make controller.py smaller
"""
# https://stackoverflow.com/a/16994175/1164295
from flask import current_app

import common_lib as clib
from flask import Blueprint, flash, g, redirect, render_template, jsonify, request, session, url_for
path_to_db = "pdg.db"

# https://flask.palletsprojects.com/en/1.1.x/tutorial/views/
bp = Blueprint('pdg_api', __name__, url_prefix='/api')



@bp.route("/v1/resources/derivations/all", methods=["GET"])
def api_all_derivations():
    """
    return the entire "derivations" dict
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(dat["derivations"])


@bp.route("/v1/resources/derivations/list", methods=["GET"])
def api_list_derivations():
    """
    list derivation names
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["derivations"].keys()))


@bp.route("/v1/resources/derivations", methods=["GET"])
def api_read_derivation_by_name():
    """
    return a single derivation

    /api/v1/resources/derivations?name=curl%20curl%20identity

    https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    >>>
    """
    current_app.logger.info("[trace]")
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


@bp.route("/v1/resources/expressions/all", methods=["GET"])
def api_all_expressions():
    """
    return the entire "expressions" dict
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(dat["expressions"])


@bp.route("/v1/resources/expressions/list", methods=["GET"])
def api_list_expressions():
    """
    list the expression global IDs
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["expressions"].keys()))


@bp.route("/v1/resources/expressions", methods=["GET"])
def api_read_expression_by_id():
    """
    return a single expression

    /api/v1/resources/expressions?global_id=9999999953

    https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    >>>
    """
    current_app.logger.info("[trace]")
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


@bp.route("/v1/resources/infrules/all", methods=["GET"])
def api_all_infrules():
    """
    /api/v1/resources/infrules/all
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(dat["inference rules"])


@bp.route("/v1/resources/infrules/list", methods=["GET"])
def api_list_infrules():
    """
    /api/v1/resources/infrules/list
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["inference rules"].keys()))


@bp.route("/v1/resources/infrules", methods=["GET"])
def api_infrules_by_name():
    """
    /api/v1/resources/infrules?name=add%20zero%20to%20LHS
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if "name" in request.args:
        name = str(request.args["name"])
    else:
        return "Error: no name field provided. Please specify a name for the inference rule."
    if name in dat["inference rules"].keys():
        return jsonify(dat["inference rules"][name])
    else:
        return "Error: expression with name " + name + " not found; see infrules/list"


@bp.route("/v1/resources/local_to_global/all", methods=["GET"])
def api_all_local_to_global():
    """
    /api/v1/resources/local_to_global/all
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(dat["expr local to global"])


@bp.route("/v1/resources/local_to_global/list", methods=["GET"])
def api_list_local():
    """
    /api/v1/resources/local_to_global/list
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["expr local to global"].keys()))


@bp.route("/v1/resources/local_to_global", methods=["GET"])
def api_local_to_global():
    """
    /api/v1/resources/local_to_global?local_id=8837284
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if "local_id" in request.args:
        local_id = str(request.args["local_id"])
    else:
        return "Error: No local_id field provided. Please specify a local_id."
    if local_id in dat["expr local to global"].keys():
        return jsonify(dat["expr local to global"][local_id])
    else:
        return "Error: local_id " + local_id + " not found see local_to_global/list"


@bp.route("/v1/resources/symbols/all", methods=["GET"])
def api_all_symbols():
    """
    /api/v1/resources/symbols/all
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(dat["symbols"])


@bp.route("/v1/resources/symbols/list", methods=["GET"])
def api_list_symbols():
    """
    /api/v1/resources/symbols/list
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["symbols"].keys()))


@bp.route("/v1/resources/symbols", methods=["GET"])
def api_symbols_by_name():
    """
    /api/v1/resources/symbols?symbol_id=1223
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if "symbol_id" in request.args:
        symbol_id = str(request.args["symbol_id"])
    else:
        return "Error: No symbol_id field provided. Please specify a symbol_id."
    if symbol_id in dat["symbols"].keys():
        return jsonify(dat["symbols"][symbol_id])
    else:
        return "Error: symbol_id " + symbol_id + " not found see symbols/list"


@bp.route("/v1/resources/operators/all", methods=["GET"])
def api_all_operators():
    """
    /api/v1/resources/operators/all
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(dat["symbols"])


@bp.route("/v1/resources/operators/list", methods=["GET"])
def api_list_operators():
    """
    /api/v1/resources/operators/list
    >>>
    """
    current_app.logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["operators"].keys()))


@bp.route("/v1/resources/operators", methods=["GET"])
def api_operators_by_name():
    """
    /api/v1/resources/operators?operator_id=equals
    >>>
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if "operator_id" in request.args:
        operator_id = str(request.args["operator_id"])
    else:
        return "Error: No operator_id field provided. Please specify a operator_id."
    if operator_id in dat["operators"].keys():
        return jsonify(dat["operators"][operator_id])
    else:
        return "Error: operator_id " + operator_id + " not found see symbols/list"


@bp.route("/v1/documentation", methods=["GET", "POST"])
def api_documentation():
    """
    a static page

    >>> api_documentation()
    """
    current_app.logger.info("[trace]")
    return render_template("api_documentation.html", title="API Documentation")
