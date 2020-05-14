#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

# convention: every function and class includes a [trace] print
#
# Every function has type hinting; https://www.python.org/dev/peps/pep-0484/
# https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
#
# Every function has a doctest; https://docs.python.org/3/library/doctest.html
#
# formating should be PEP-8 compliant; https://www.python.org/dev/peps/pep-0008/

# import math
import json
from functools import wraps
import errno
import signal
import os
# move and copy files
import shutil  
# when content was created, use current timestamp
import datetime
# hash email addresses, file contents
import hashlib

# image dimensions in pixels
import cv2  # type: ignore
import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore
from subprocess import PIPE  # https://docs.python.org/3/library/subprocess.html
import subprocess  # https://stackoverflow.com/questions/39187886/what-is-the-difference-between-subprocess-popen-and-subprocess-run/39187984
import random
import logging
import collections
import sqlite3
import pickle
from jsonschema import validate  # type: ignore
import json_schema  # a PDG file
import validate_inference_rules_sympy as vir  # a PDG file
import common_lib as clib  # a PDG file
import logs_to_stats
from typing import Tuple, TextIO, List  # mypy
from typing_extensions import (
    TypedDict,
)  # https://mypy.readthedocs.io/en/stable/more_types.html

# https://www.python.org/dev/peps/pep-0589/
import pandas  # type: ignore


logger = logging.getLogger(__name__)

# global proc_timeout
proc_timeout = 30

STEP_DICT = TypedDict(
    "STEP_DICT",
    {
        "inf rule": str,
        "inputs": list,
        "feeds": list,
        "outputs": list,
        "linear index": int,
        "notes": str,
        "author": str,
        "creation date": str,
    },
)

# ******************************************
# debugging, error handling


def send_email(list_of_addresses: list, msg_body: str, subject: str) -> None:
    """
    >>>
    """
    return


# from https://gist.github.com/bhpayne/54fb2c8d864d02750c9168ae734fb21e
def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """
    https://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish
    >>>
    """

    def decorator(func):
        def _handle_timeout(signum, frame):
            send_email(["ben.is.located@gmail.com"], error_message, "TIMEOUT OCCURRED")
            logger.warning(error_message)
            raise Exception(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


# ******************************************
# check input files


def allowed_file(filename):
    """
    validate that the file name ends with the desired extention

    from https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
    >>> allowed_file('a_file')
    False
    >>> allowed_file('a_file.json')
    True
    """
    logger.info("[trace]")

    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"json"}


def validate_json_file(filename: str) -> None:
    """
    >>> validate_json_file('filename.json')
    """
    logger.info("[trace]")

    with open(filename) as json_file:
        try:
            candidate_dat = json.load(json_file)
        except json.decoder.JSONDecodeError as er:
            logger.error("ERROR in JSON schema compliance: %s", er)
            # return False
            raise Exception("uploaded file does not appear to be JSON; ignoring file")
    # now we know the file is actually JSON
    # next, does the JSON conform to PDG schema?

    try:
        validate(instance=candidate_dat, schema=json_schema.schema)
    except:  # jsonschema.exceptions.ValidationError as er:
        logger.error("ERROR in JSON schema compliance")
        raise Exception("JSON is not compliant with schema")
        # return False  # JSON is not compliant with schmea

    #    return True  # file is JSON and is compliant with schmea
    return


def create_session_id() -> str:
    """
    >>> create_session_id
    """
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
    rand_id = str(random.randint(100, 999))
    return now_str + "_" + rand_id


# *******************************************
# query database for properties
# read-only functions

# def validate_json_database(path_to_db: str) -> None:
#    """
#    >>> validate_json_database('data.pkl')
#    """
#    dat = clib.read_db(path_to_db)
#    validate(instance=dat,schema=json_schema.schema)
#    return
def update_symbol_in_step(
    sympy_symbol: str, symbol_id: str, deriv_id: str, step_id: str, path_to_db: str
) -> None:
    """
    In a webform a user associated a sympy symbol with a PDG symbol_id.
    This function updates the database to reflect that selection

    >>> update_symbol_in_step()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    for expr_global_id in list_expr_in_step(deriv_id, step_id, path_to_db):
        expr_latex = dat["expressions"][expr_global_id]["latex"]
        symbols_in_expr = list_symbols_used_in_expr_from_sympy(expr_latex)
        if sympy_symbol in symbols_in_expr:
            dat["expressions"][expr_global_id]["AST"].append(symbol_id)

    clib.write_db(path_to_db, dat)
    return


def find_symbols_in_step_that_lack_id(
    deriv_id: str, step_id: str, path_to_db: str
) -> list:
    """
    for a given step
    input: list of symbols detected by Sympy; each element is a string
    returns: list of Sympy symbols that don't seem to have a corresponding entry in the PDG AST list of symbol IDs

    >>> find_symbols_in_step_that_lack_id() 
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_sympy_symbols_lacking_PDG_id = []

    list_of_sympy_symbols_in_step = list_symbols_used_in_step_from_sympy(
        deriv_id, step_id, path_to_db
    )
    list_of_PDG_AST_symbol_ids_in_step = list_symbols_used_in_step_from_PDG_AST(
        deriv_id, step_id, path_to_db
    )

    for sympy_symbol in list_of_sympy_symbols_in_step:
        sympy_symbol_has_PDG_AST_id = False
        for symbol_id in list_of_PDG_AST_symbol_ids_in_step:
            symbol_latex = dat["symbols"][symbol_id]["latex"]
            if sympy_symbol in symbol_latex:
                sympy_symbol_has_PDG_AST_id = True
        if not sympy_symbol_has_PDG_AST_id:
            list_of_sympy_symbols_lacking_PDG_id.append(sympy_symbol)

    return list(set(list_of_sympy_symbols_lacking_PDG_id))


def guess_missing_PDG_AST_ids(
    list_of_symbols_in_step_lacking_id: list,
    deriv_id: str,
    step_id: str,
    path_to_db: str,
) -> dict:
    """
    this runs as a second pass after create_AST_png_per_expression_in_step()
    and fills in symbol_id based on what is present in other expressions within this step

    >>> guess_missing_PDG_AST_ids()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    logger.debug(
        "list of symbols from Sympy that lack PDG symbol ID: "
        + str(list_of_symbols_in_step_lacking_id)
    )

    list_of_PDG_symbol_ids_in_step = list_symbols_used_in_step_from_PDG_AST(
        deriv_id, step_id, path_to_db
    )
    logger.debug(
        "list of symbol_ids in this step: " + str(list_of_PDG_symbol_ids_in_step)
    )

    symbol_candidate_dict = {}
    for sympy_symbol_without_id in list_of_symbols_in_step_lacking_id:
        list_of_candidate_ids = []
        for PDG_symbol_id in list_of_PDG_symbol_ids_in_step:
            if sympy_symbol_without_id in dat["symbols"][PDG_symbol_id]["latex"]:
                list_of_candidate_ids.append(PDG_symbol_id)
        symbol_candidate_dict[sympy_symbol_without_id] = list_of_candidate_ids
        if len(list_of_candidate_ids) == 0:  # no matches in step, look elsewhere
            for symbol_id, symbol_dict in dat["symbols"].items():
                if sympy_symbol_without_id in dat["symbols"][symbol_id]["latex"]:
                    list_of_candidate_ids.append(symbol_id)
            symbol_candidate_dict[sympy_symbol_without_id] = list_of_candidate_ids

    logger.debug("symbol candidate dict: " + str(symbol_candidate_dict))
    return symbol_candidate_dict


def fill_in_missing_PDG_AST_ids(
    symbol_candidate_dict, deriv_id, step_id, path_to_db
) -> None:
    """
    if a symbol detected by Sympy has only one candidate ID, then update 

    >>> fill_in_missing_PDG_AST_ids()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    for sympy_symbol_without_id, list_of_candidate_ids in symbol_candidate_dict.items():
        if len(list_of_candidate_ids) == 1:
            logger.debug(
                "updating sympy's "
                + sympy_symbol_without_id
                + " using symbol ID "
                + list_of_candidate_ids[0]
            )
            for expr_global_id in list_expr_in_step(deriv_id, step_id, path_to_db):
                expr_latex = dat["expressions"][expr_global_id]["latex"]
                symbols_in_expr = list_symbols_used_in_expr_from_sympy(expr_latex)
                if sympy_symbol_without_id in symbols_in_expr:
                    dat["expressions"][expr_global_id]["AST"].append(
                        list_of_candidate_ids[0]
                    )
        else:
            logger.debug(
                "sympy symbol "
                + sympy_symbol_without_id
                + " has more than one ID: "
                + str(list_of_candidate_ids)
            )
    clib.write_db(path_to_db, dat)
    return


def rank_candidate_pdg_symbols_for_sympy_symbol(
    sympy_symbol: str, symbol_IDs_used_in_step_from_PDG_AST: list, path_to_db: str
) -> list:
    """
    input: symbol (detected by Sympy) as string
    returns: ranked list of PDG symbol IDs

    >>> rank_candidate_pdg_symbols_for_sympy_symbol()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_candidate_symbol_ids = []

    # most likely candidate is if symbol is already present in step
    for symbol_id in symbol_IDs_used_in_step_from_PDG_AST:
        if sympy_symbol in dat["symbols"][symbol_id]["latex"]:
            list_of_candidate_symbol_ids.append(symbol_id)

    for symbol_id, symbol_dict in dat["symbols"].items():
        if (
            sympy_symbol in dat["symbols"][symbol_id]["latex"]
            and symbol_id not in list_of_candidate_symbol_ids
        ):
            list_of_candidate_symbol_ids.append(symbol_id)
    return list_of_candidate_symbol_ids


def list_symbols_used_in_expr_from_sympy(expr_latex: str) -> list:
    """
    input: latex expression as string

    returns list of symbols detected by Sympy; each element is a string

    >>> list_symbols_used_in_expr_from_sympy('a = b')
    """
    logger.info("[trace]")
    list_of_symbols = []
    try:
        symp_lat = parse_latex(expr_latex)
    except sympy.SympifyError as err:
        logger.error(err)
        raise Exception("Sympy unable to parse latex (1): " + expr_latex)
    except sympy.parsing.latex.errors.LaTeXParsingError as err:
        logger.error(err)
        raise Exception("Sympy unable to parse latex (2): " + expr_latex)

    for symb in symp_lat.atoms(sympy.Symbol):
        list_of_symbols.append(str(symb))
    return list(set(list_of_symbols))


def list_symbols_used_in_expr_from_PDG_AST(ast_as_list: list, path_to_db: str) -> list:
    """
    >>> list_symbols_used_in_expr_from_PDG_AST()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    list_of_symbol_ids = []
    # logger.debug(str(ast_as_list))
    list_of_symbols_and_operators = list(flatten_list(ast_as_list))
    # logger.debug(str(list_of_symbols_and_operators))

    for this_symbol_id in list_of_symbols_and_operators:
        try:
            symbol_latex = dat["symbols"][this_symbol_id]["latex"]
        except:
            symbol_latex = ""
        if len(symbol_latex) > 0:
            list_of_symbol_ids.append(this_symbol_id)
    # logger.debug(str(list_of_symbol_ids))
    return list(set(list_of_symbol_ids))


def list_symbols_used_in_step_from_PDG_AST(
    deriv_id: str, step_id: str, path_to_db: str
) -> list:
    """
    for all expressions in a step, what variables and constants are present?

    >>> 
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_symbol_ids = []

    if step_id in dat["derivations"][deriv_id]["steps"].keys():
        step_dict = dat["derivations"][deriv_id]["steps"][step_id]
        for connection_type in ["inputs", "feeds", "outputs"]:
            for local_id in step_dict[connection_type]:
                expr_global_id = dat["expr local to global"][local_id]
                logger.debug(str(dat["expressions"][expr_global_id]["AST"]))
                symbols_per_expr = list_symbols_used_in_expr_from_PDG_AST(
                    dat["expressions"][expr_global_id]["AST"], path_to_db
                )
                logger.debug(str(symbols_per_expr))
                for symbol_id in symbols_per_expr:
                    list_of_symbol_ids.append(symbol_id)
    else:  # step_id not in steps
        list_of_symbol_ids = []
    list_of_symbol_ids = list(set(list_of_symbol_ids))
    return list_of_symbol_ids


def list_symbols_used_in_step_from_sympy(
    deriv_id: str, step_id: str, path_to_db: str
) -> list:
    """
    for all expressions in a step, what variables and constants are present?

    >>> 
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_symbols = []

    if step_id in dat["derivations"][deriv_id]["steps"].keys():
        step_dict = dat["derivations"][deriv_id]["steps"][step_id]
        for connection_type in ["inputs", "feeds", "outputs"]:
            for local_id in step_dict[connection_type]:
                expr_global_id = dat["expr local to global"][local_id]
                expr_latex = dat["expressions"][expr_global_id]["latex"]
                # logger.debug(expr_latex)
                symbols_per_expr = list_symbols_used_in_expr_from_sympy(expr_latex)
                for symb in symbols_per_expr:
                    list_of_symbols.append(str(symb))
    else:  # step_id not available
        list_of_symbols = []

    list_of_symbols = list(set(list_of_symbols))
    return list_of_symbols


def create_AST_png_for_latex(expr_latex: str, output_filename: str) -> str:
    """
    >>> 
    """
    logger.info("[trace]")

    try:
        symp_lat = parse_latex(expr_latex)
    except sympy.SympifyError as err:
        logger.error(err)
        raise Exception("Sympy unable to parse latex: " + expr_latex)
        sympy_lat = ""
    graphviz_of_AST_for_expr = sympy.printing.dot.dotprint(symp_lat)
    dot_filename = "tmp.dot"
    with open(dot_filename, "w") as fil:
        fil.write(graphviz_of_AST_for_expr)

    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
    process = subprocess.run(
        ["dot", "-Tpng", dot_filename, "-o" + output_filename],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )
    neato_stdout = process.stdout.decode("utf-8")
    if len(neato_stdout) > 0:
        logger.debug(neato_stdout)
    neato_stderr = process.stderr.decode("utf-8")
    if len(neato_stderr) > 0:
        logger.debug(neato_stderr)

    shutil.move(output_filename, "/home/appuser/app/static/" + output_filename)
    return output_filename


def create_AST_png_per_expression_in_step(
    deriv_id: str, step_id: str, path_to_db: str
) -> list:
    """
    for each expression in a step, create the AST PNG from Sympy

    >>> 
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_expression_AST_pictures = []

    step_dict = dat["derivations"][deriv_id]["steps"][step_id]
    for connection_type in ["inputs", "feeds", "outputs"]:
        for local_id in step_dict[connection_type]:
            expr_global_id = dat["expr local to global"][local_id]
            expr_latex = dat["expressions"][expr_global_id]["latex"]
            # logger.debug('latex = ' + expr_latex)
            output_filename = expr_global_id + "_ast.png"
            create_AST_png_for_latex(expr_latex, output_filename)

            symbols_from_sympy = list_symbols_used_in_expr_from_sympy(expr_latex)
            symbols_from_PDG_AST = list_symbols_used_in_expr_from_PDG_AST(
                dat["expressions"][expr_global_id]["AST"], path_to_db
            )

            list_of_sympy_symbols_lacking_PDG_id = find_symbols_in_step_that_lack_id(
                deriv_id, step_id, path_to_db
            )

            this_dict = {
                "ast png filename": output_filename,
                "expr global id": expr_global_id,
                "symbols from sympy": symbols_from_sympy,
                "symbols from PDG AST": symbols_from_PDG_AST,
                "sympy symbols without PDG AST ID": list_of_sympy_symbols_lacking_PDG_id,
            }
            # pic_and_id = (output_filename, expr_global_id)
            list_of_expression_AST_pictures.append(this_dict)

    logger.debug(str(list_of_expression_AST_pictures))
    return list_of_expression_AST_pictures


def linear_index_to_step_id(
    deriv_id: str, step_linear_index: str, path_to_db: str
) -> str:
    """
    >>> linear_index_to_step_id() 
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if deriv_id in dat["derivations"].keys():
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            if step_linear_index == str(step_dict["linear index"]):
                return step_id
    else:
        raise Exception(deriv_id + "not in dat")
    raise Exception(step_linear_index + "not found in derivation " + deriv_id)
    return "ERROR"


def get_list_of_sorted_linear_indices(deriv_id: str, path_to_db: str) -> list:
    """
    >>> 
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_linear_indices = []
    if deriv_id in dat["derivations"].keys():
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            list_of_linear_indices.append(step_dict["linear index"])
    else:
        raise Exception(deriv_id + "not in dat")

    list_of_linear_indices.sort()
    return list_of_linear_indices


def list_new_linear_indices(deriv_id: str, path_to_db: str) -> list:
    """
    https://github.com/allofphysicsgraph/proofofconcept/issues/116

    Given a list of indices in a derivation, what new linear indices can be inserted?

    >>> get_linear_indices()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_linear_indices = get_list_of_sorted_linear_indices(deriv_id, path_to_db)
    # logger.debug('list_of_linear_indices = %s', str(list_of_linear_indices))
    new_list = []  # potential linear indices available for insertion
    for indx, valu in enumerate(list_of_linear_indices[:-1]):
        # logger.debug('indx = ' + str(indx) + '; valu =' + str(valu))
        new_list.append(round((valu + list_of_linear_indices[indx + 1]) / 2, 3))
    new_list.append(list_of_linear_indices[-1] + 1)
    lowest_valu = round(list_of_linear_indices[0] / 2, 3)
    new_list.insert(0, lowest_valu)
    # logger.debug('new_list = %s', str(new_list))
    return new_list


def list_local_id_for_derivation(deriv_id: str, path_to_db: str) -> list:
    """
    list the expr_local_id used in a derivation

    >>> list_local_id_for_derivation('fun deriv', 'pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_local_id: List[str] = []
    if deriv_id not in dat["derivations"].keys():
        list_of_local_id = []
    else:
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            for connection_type in ["inputs", "feeds", "outputs"]:
                for local_id in step_dict[connection_type]:
                    list_of_local_id.append(local_id)
    list_of_local_id = list(set(list_of_local_id))
    # logger.debug('list_of_local_id = %s', str(list_of_local_id))
    list_of_local_id.sort()
    return list_of_local_id


def list_global_id_not_in_derivation(deriv_id: str, path_to_db: str) -> list:
    """
    >>> list_global_id_not_in_derivation('fun deriv', 'pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    # I could have called list_local_id_for_derivation but I wrote this function first
    global_ids_in_derivation: List[str] = []
    if deriv_id not in dat["derivations"].keys():
        global_ids_in_derivation = []
    else:  # derivation exists in dat
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            for connection_type in ["inputs", "feeds", "outputs"]:
                for local_id in step_dict[connection_type]:
                    global_ids_in_derivation.append(
                        dat["expr local to global"][local_id]
                    )
    global_ids_in_derivation = list(set(global_ids_in_derivation))
    # logger.debug('len(global_ids_in_derivation) = %s', str(len(global_ids_in_derivation)))
    all_global_ids = list(dat["expressions"].keys())
    list_of_global_id_not_in_derivation = list(
        set(all_global_ids) - set(global_ids_in_derivation)
    )
    # logger.debug('list_of_global_id_not_in_derivation = %s', str(list_of_global_id_not_in_derivation))
    list_of_global_id_not_in_derivation.sort()
    return list_of_global_id_not_in_derivation

def md5_of_file(fname):
    """
    get md5 hash of file content

    https://docs.python.org/3/library/hashlib.html
    https://www.geeksforgeeks.org/md5-hash-python/
    >>> md5_file()
    d41d8cd98f00b204e9800998ecf8427e
    """
    with open(fname, 'rb') as fil:
        file_content = fil.read()
    return hashlib.md5(file_content).hexdigest()

def md5_of_string(str_to_hash):
    """
    convert string to bytes, then get md5 hash
    >>> md5_of_string
    """
    return hashlib.md5( str_to_hash.encode('utf-8') ).hexdigest()

def create_files_of_db_content(path_to_db):
    """
    >>> create_files_of_db_content('pdg.db')
    """
    logger.info("[trace]")

    dat = clib.read_db(path_to_db)
    json_file_name = "data.json"
    with open(json_file_name, "w") as json_file_handle:
        json.dump(
            dat, json_file_handle, indent=4, separators=(",", ": ")
        )  # , sort_keys=True)
    shutil.copy(json_file_name, "/home/appuser/app/static/")

    all_df = convert_json_to_dataframes(path_to_db)

    df_pkl_file = convert_df_to_pkl(all_df)

    sql_file = convert_dataframes_to_sql(all_df)
    shutil.copy(sql_file, "/home/appuser/app/static/")

    rdf_file = convert_data_to_rdf(path_to_db)
    shutil.copy(rdf_file, "/home/appuser/app/static/")

    neo4j_file = convert_data_to_cypher(path_to_db)
    shutil.copy(neo4j_file, "/home/appuser/app/static/")

    return [json_file_name, all_df, df_pkl_file, sql_file, rdf_file, neo4j_file]


def convert_json_to_dataframes(path_to_db: str) -> dict:
    """
    this conversion is lossless

    >>> convert_json_to_dataframes('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    all_dfs = {}

    expressions_list_of_dicts = []
    for expression_id, expression_dict in dat["expressions"].items():
        this_expr = {}
        this_expr["expression id"] = expression_id
        this_expr["expression latex"] = expression_dict["latex"]
        this_expr["AST"] = "None"
        if "AST" in expression_dict.keys():
            this_expr["AST"] = expression_dict["AST"]
        expressions_list_of_dicts.append(this_expr)
    all_dfs["expressions"] = pandas.DataFrame(expressions_list_of_dicts)

    infrules_list_of_dicts = []
    for infrule_name, infrule_dict in dat["inference rules"].items():
        this_infrule = {}
        this_infrule["inference rule"] = infrule_name
        this_infrule["number of feeds"] = infrule_dict["number of feeds"]
        this_infrule["number of inputs"] = infrule_dict["number of inputs"]
        this_infrule["number of outputs"] = infrule_dict["number of outputs"]
        this_infrule["latex"] = infrule_dict["latex"]
        infrules_list_of_dicts.append(this_infrule)
    all_dfs["infrules"] = pandas.DataFrame(infrules_list_of_dicts)

    derivations_list_of_dicts = []
    for deriv_id in dat["derivations"].keys():
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            for connection_type in ["inputs", "feeds", "outputs"]:
                for expr_local_id in step_dict[connection_type]:
                    this_derivation_step_expr = {}
                    this_derivation_step_expr["derivation name"] = dat["derivations"][
                        deriv_id
                    ]["name"]
                    this_derivation_step_expr["step id"] = step_id
                    this_derivation_step_expr["inference rule"] = step_dict["inf rule"]
                    this_derivation_step_expr["linear index"] = step_dict[
                        "linear index"
                    ]
                    this_derivation_step_expr["connection type"] = connection_type
                    this_derivation_step_expr["expression local id"] = expr_local_id
                    derivations_list_of_dicts.append(this_derivation_step_expr)
    all_dfs["derivations"] = pandas.DataFrame(derivations_list_of_dicts)

    local_to_global_list_of_dicts = []
    for local_id, global_id in dat["expr local to global"].items():
        this_lookup = {}
        this_lookup["expr local id"] = local_id
        this_lookup["expr global id"] = global_id
        local_to_global_list_of_dicts.append(this_lookup)
    all_dfs["expr local global"] = pandas.DataFrame(local_to_global_list_of_dicts)

    symbols_list_of_dicts = []
    for symbol_id, symbol_dict in dat["symbols"].items():
        if "values" in symbol_dict.keys():
            for value_dict in symbol_dict["values"]:
                this_symb = {}
                this_symb["symbol id"] = symbol_id
                this_symb["latex"] = symbol_dict["latex"]
                this_symb["category"] = symbol_dict["category"]
                this_symb["scope"] = ";".join(
                    symbol_dict["scope"]
                )  # TODO: an entry in a table should not be a list (tidy data)
                if "references" in symbol_dict.keys():
                    this_symb["references"] = " ".join(
                        symbol_dict["references"]
                    )  # TODO: an entry in a table should not be a list (tidy data)
                if "name" in symbol_dict.keys():
                    this_symb["name"] = symbol_dict["name"]
                if "measure" in symbol_dict.keys():
                    this_symb["measure"] = symbol_dict["measure"]
                this_symb["value"] = value_dict["value"]
                this_symb["units"] = value_dict["units"]
                symbols_list_of_dicts.append(this_symb)
        else:  # no 'values' in symbol_dict.keys()
            this_symb = {}
            this_symb["symbol id"] = symbol_id
            this_symb["latex"] = symbol_dict["latex"]
            if "category" in symbol_dict.keys():
                this_symb["category"] = symbol_dict["category"]
            this_symb["scope"] = ";".join(
                symbol_dict["scope"]
            )  # TODO: an entry in a table should not be a list (tidy data)
            if "references" in symbol_dict.keys():
                this_symb["references"] = " ".join(
                    symbol_dict["references"]
                )  # TODO: an entry in a table should not be a list (tidy data)
            if "name" in symbol_dict.keys():
                this_symb["name"] = symbol_dict["name"]
            if "measure" in symbol_dict.keys():
                this_symb["measure"] = symbol_dict["measure"]
            symbols_list_of_dicts.append(this_symb)
    all_dfs["symbols"] = pandas.DataFrame(symbols_list_of_dicts)

    measures_list_of_dicts = []
    for measure_name, measure_dict in dat["measures"].items():
        if "references" in measure_dict.keys():
            for ref in measure_dict["references"]:
                this_measure = {}
                this_measure["measure"] = measure_name
                this_measure["reference"] = ref
                measures_list_of_dicts.append(this_measure)
        else:
            this_measure = {}
            this_measure["measure"] = measure_name
            measures_list_of_dicts.append(this_measure)
    all_dfs["measures"] = pandas.DataFrame(measures_list_of_dicts)

    units_list_of_dicts = []
    for unit_name, unit_dict in dat["units"].items():
        for this_ref in unit_dict["references"]:
            this_unit = {}
            this_unit["unit"] = unit_name
            this_unit["measure"] = unit_dict["measure"]
            this_unit["reference"] = this_ref
            units_list_of_dicts.append(this_unit)
    all_dfs["units"] = pandas.DataFrame(units_list_of_dicts)

    operators_list_of_dicts = []
    for operator_name, operator_dict in dat["operators"].items():
        for this_scope in operator_dict["scope"]:
            this_op = {}
            this_op["operator"] = operator_name
            this_op["operator latex"] = operator_dict["latex"]
            this_op["argument count"] = operator_dict["argument count"]
            this_op["scope"] = this_scope
            operators_list_of_dicts.append(this_op)
    all_dfs["operators"] = pandas.DataFrame(operators_list_of_dicts)

    return all_dfs


def convert_df_to_pkl(all_df) -> str:
    """
    this conversion is lossless

    >>> convert_df_to_pkl(all_df)
    """
    logger.info("[trace]")
    df_pkl = "data.pkl"
    with open(df_pkl, "wb") as fil:
        pickle.dump(all_df, fil)
    return df_pkl


def convert_dataframes_to_sql(all_dfs) -> str:
    """
    this conversion is lossless

    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html

    >>> convert_dataframes_to_sql(all_dfs, 'pdg.db')
    """
    logger.info("[trace]")
    sql_file = "physics_derivation_graph.sqlite3"
    try:
        cnx = sqlite3.connect(sql_file)
    except sqlite3.Error:
        logger.debug(sqlite3.Error)
        raise Exception("unable to connect to SQL file " + sql_file)

    for df_name, df in all_dfs.items():
        # logger.debug(df_name)
        # logger.debug(df.dtypes)
        # logger.debug(df.head())
        df = df.astype(str)
        df.to_sql(name=df_name, con=cnx, if_exists="replace")

    return sql_file


def convert_data_to_rdf(path_to_db: str) -> str:
    """
    this conversion is lossy

    https://github.com/allofphysicsgraph/proofofconcept/issues/14

    https://www.w3.org/RDF/
    https://en.wikipedia.org/wiki/Web_Ontology_Language
    >>> convert_data_to_rdf('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    rdf_str = ""
    # https://www.w3.org/TR/1999/REC-rdf-syntax-19990222/#basic
    rdf_str += '<?xml version="1.0"?>'
    rdf_str += "<rdf:RDF"
    rdf_str += '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"'
    rdf_str += '  xmlns:s="http://description.org/schema/">'
    for expression_id, expression_dict in dat["expressions"].items():
        rdf_str += expression_id + " has_latex '" + expression_dict["latex"] + "'\n"
    for infrule_name, infrule_dict in dat["inference rules"].items():
        rdf_str += (
            # https://stackoverflow.com/questions/22520932/python-remove-all-non-alphabet-chars-from-string
            "".join(filter(str.isalnum, infrule_name))
            + " has_input_count "
            + str(infrule_dict["number of inputs"])
            + "\n"
        )
        rdf_str += (
            "".join(filter(str.isalnum, infrule_name))
            + " has_feed_count "
            + str(infrule_dict["number of feeds"])
            + "\n"
        )
        rdf_str += (
            "".join(filter(str.isalnum, infrule_name))
            + " has_output_count "
            + str(infrule_dict["number of outputs"])
            + "\n"
        )
        rdf_str += (
            "".join(filter(str.isalnum, infrule_name))
            + " has_latex '"
            + infrule_dict["latex"]
            + "'\n"
        )
    for deriv_id in dat["derivations"].keys():
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            rdf_str += deriv_id + " has_step " + step_id + "\n"
            rdf_str += (
                step_id
                + " has_infrule "
                + "".join(filter(str.isalnum, step_dict["inf rule"]))
                + "\n"
            )
            rdf_str += (
                step_id + " has_linear_index " + str(step_dict["linear index"]) + "\n"
            )
            for expr_local_id in step_dict["inputs"]:
                rdf_str += step_id + " has_input_expr " + expr_local_id + "\n"
            for expr_local_id in step_dict["feeds"]:
                rdf_str += step_id + " has_feed_expr " + expr_local_id + "\n"
            for expr_local_id in step_dict["outputs"]:
                rdf_str += step_id + " has_output_expr " + expr_local_id + "\n"
    for local_id, global_id in dat["expr local to global"].items():
        rdf_str += local_id + " local_is_global " + global_id + "\n"
    rdf_str += "</rdf:RDF>"

    rdf_file = "data.rdf"
    with open(rdf_file, "w") as fil:
        fil.write(rdf_str)
    return rdf_file


def convert_data_to_cypher(path_to_db: str) -> str:
    """
    this conversion is lossy

    https://hub.docker.com/_/neo4j

    $ docker run --publish=7474:7474 --publish=7687:7687 --publish=7473:7473 \
                 --volume=$HOME/neo4j/data:/data \
                 --volume=$HOME/neo4j/logs:/logs \
                 --volume=$HOME/neo4j/conf:/conf \
                 --volume=$HOME/neo4j/tmp:/tmp \
                 --env NEO4J_AUTH=none neo4j:4.0

    https://neo4j.com/docs/cypher-manual/current/clauses/create/#create-create-single-node

    >>> convert_data_to_cypher('pdg.db')
    """
    logger.info("[trace]")

    dat = clib.read_db(path_to_db)

    cypher_str = ""

    for expression_id, expression_dict in dat["expressions"].items():
        cypher_str += "CREATE (id" + expression_id + ":expression {\n"
        cypher_str += (
            "       latex: '"
            + expression_dict["latex"].replace("\\", "\\\\").replace("'", "\\'")
            + "'})\n"
        )
    for infrule_name, infrule_dict in dat["inference rules"].items():
        # https://stackoverflow.com/questions/22520932/python-remove-all-non-alphabet-chars-from-string
        cypher_str += (
            "CREATE (" + "".join(filter(str.isalnum, infrule_name)) + ":infrule {\n"
        )
        cypher_str += (
            "       num_inputs: " + str(infrule_dict["number of inputs"]) + ",\n"
        )
        cypher_str += (
            "       num_feeds: " + str(infrule_dict["number of feeds"]) + ",\n"
        )
        cypher_str += (
            "       num_outputs: " + str(infrule_dict["number of outputs"]) + ",\n"
        )
        cypher_str += "       latex: '" + infrule_dict["latex"] + "'})\n"
    for deriv_id in dat["derivations"].keys():
        cypher_str += (
            "// derivation: " + dat["derivations"][deriv_id]["name"] + "\n"
        )  # https://neo4j.com/docs/cypher-manual/current/syntax/comments/
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            cypher_str += "CREATE (id" + step_id + ":step {\n"
            cypher_str += (
                "       infrule: '"
                + "".join(filter(str.isalnum, step_dict["inf rule"]))
                + "',\n"
            )
            cypher_str += (
                "       linear_index: " + str(step_dict["linear index"]) + "})\n"
            )
            for expr_local_id in step_dict["inputs"]:
                cypher_str += (
                    "CREATE (id" + step_id + ")<-[:expr]-(id" + expr_local_id + ")\n"
                )
            for expr_local_id in step_dict["feeds"]:
                cypher_str += (
                    "CREATE (id" + step_id + ")<-[:expr]-(id" + expr_local_id + ")\n"
                )
            for expr_local_id in step_dict["outputs"]:
                cypher_str += (
                    "CREATE (id" + step_id + ")-[:expr]->(id" + expr_local_id + ")\n"
                )
    for local_id, global_id in dat["expr local to global"].items():
        cypher_str += (
            "CREATE (id" + local_id + ")-[:local_is_global]->(id" + global_id + ")\n"
        )
    # for symbol_id, symbol_dict in dat['symbols'].items():
    #    cypher_str += "CREATE ()"
    # for operator_name, operator_dict in dat['operators'].items():
    #    cypher_str += "CREATE ()"
    cypher_file = "neo4j.txt"
    with open(cypher_file, "w") as fil:
        fil.write(cypher_str)
    return cypher_file


def flatten_list(list_of_lists: list):
    """
    https://stackoverflow.com/a/5286571/1164295

    >>> l = ['aab', 'aimign', ['agian', 'agag', ['gagag', 'gasg']]]
    >>> list(flatten_list(l))
    ['aab', 'aimign', 'agian', 'agag', 'gagag', 'gasg']
    """
    for x in list_of_lists:
        if hasattr(x, "__iter__") and not isinstance(x, str):
            for y in flatten_list(x):
                yield y
        else:
            yield x


def generate_expr_dict_with_symbol_list(path_to_db: str) -> dict:
    """
    >>> generate_expr_dict_with_symbol_list()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    expr_dict_with_symbol_list = dat["expressions"]
    for expr_global_id, expr_dict in dat["expressions"].items():
        list_of_symbols = list(flatten_list(expr_dict["AST"]))

        list_of_tuples = []
        for this_symbol in list_of_symbols:
            try:
                symbol_latex = dat["symbols"][this_symbol]["latex"]
            except:
                symbol_latex = ""
            list_of_tuples.append((this_symbol, symbol_latex))
        expr_dict_with_symbol_list[expr_global_id]["list of symbols"] = list_of_tuples

    # logger.debug(str(expr_dict_with_symbol_list))
    return expr_dict_with_symbol_list


def get_sorted_list_of_symbols_not_in_use(path_to_db: str) -> list:
    """
    >>>
    """
    symbol_popularity_dict = popularity_of_symbols_in_expressions(path_to_db)
    list_of_symbols_not_in_use = []
    for symbol, list_of_deriv_used_in in symbol_popularity_dict.items():
        if len(list_of_deriv_used_in) == 0:
            list_of_symbols_not_in_use.append(symbol)
    list_of_symbols_not_in_use.sort()
    return list_of_symbols_not_in_use


def get_sorted_list_of_operators_not_in_use(path_to_db: str) -> list:
    """
    >>>
    """
    operator_popularity_dict = popularity_of_operators(path_to_db)
    list_of_operators_not_in_use = []
    for operator, list_of_deriv_used_in in operator_popularity_dict.items():
        if len(list_of_deriv_used_in) == 0:
            list_of_operators_not_in_use.append(operator)
    list_of_operators_not_in_use.sort()
    return list_of_operators_not_in_use


def get_sorted_list_of_expr(path_to_db: str) -> list:
    """
    return: list of global IDs

    >>> get_sorted_list_of_expr('data.pkl')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_expr = list(dat["expressions"].keys())
    list_expr.sort()
    return list_expr


def get_sorted_list_of_expr_not_in_use(path_to_db: str) -> list:
    """
    return: list of global IDs

    >>> get_sorted_list_of_expr('data.pkl')
    """
    logger.info("[trace]")

    expr_popularity_dict = popularity_of_expressions(path_to_db)
    list_of_expr_not_in_use = []
    for expr_global_id, list_of_deriv_used_in in expr_popularity_dict.items():
        if len(list_of_deriv_used_in) == 0:
            list_of_expr_not_in_use.append(expr_global_id)
    list_of_expr_not_in_use.sort()
    return list_of_expr_not_in_use


def get_sorted_list_of_inf_rules_not_in_use(path_to_db: str) -> list:
    """
    >>> get_sorted_list_of_inf_rules('data.pkl')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    infrule_popularity_dict = popularity_of_infrules(path_to_db)
    list_of_infrules_not_in_use = []
    for infrule, list_of_deriv_used_in in infrule_popularity_dict.items():
        if len(list_of_deriv_used_in) == 0:
            list_of_infrules_not_in_use.append(infrule)
    # list_of_infrules_not_in_use = [x.lower() for x in list_of_infrules_not_in_use]
    list_of_infrules_not_in_use.sort()
    return list_of_infrules_not_in_use


def get_sorted_list_of_inf_rules(path_to_db: str) -> list:
    """
    >>> get_sorted_list_of_inf_rules('data.pkl')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_infrule = list(dat["inference rules"].keys())
    # list_infrule = [x.lower() for x in list_infrule]
    list_infrule.sort()
    return list_infrule


def get_sorted_list_of_derivations(path_to_db: str) -> list:
    """
    >>> get_list_of_derivations('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_tups = []
    for deriv_id in dat["derivations"].keys():
        list_of_tups.append((deriv_id, dat["derivations"][deriv_id]["name"].lower()))

    list_deriv = []
    # https://stackoverflow.com/a/10695161/1164295
    for this_tup in sorted(list_of_tups, key=lambda x: x[1]):
        list_deriv.append(this_tup[0])

    return list_deriv


def create_symbol_id(path_to_db: str) -> str:
    """
    >>> create_symbol_id()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    symbol_ids_in_use = list(dat["symbols"].keys())
    found_valid_id = False
    loop_count = 0
    while not found_valid_id:
        loop_count += 1
        proposed_symbol_id = str(random.randint(1000, 9999))  # 4 digits

        if proposed_symbol_id not in symbol_ids_in_use:
            found_valid_id = True
        if loop_count > 100000:
            logger.error("too many; this seems unlikely")
            raise Exception("this seems unlikely")
    return proposed_symbol_id


def create_deriv_id(path_to_db: str) -> str:
    """
    >>> create_deriv_id()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    deriv_ids_in_use = list(dat["derivations"].keys())

    found_valid_id = False
    loop_count = 0
    while not found_valid_id:
        loop_count += 1
        proposed_deriv_id = str(random.randint(100000, 999999))  # 6 digits

        if proposed_deriv_id not in deriv_ids_in_use:
            found_valid_id = True
        if loop_count > 10000000:
            logger.error("too many; this seems unlikely")
            raise Exception("this seems unlikely")
    return proposed_deriv_id


def create_expr_global_id(path_to_db: str) -> str:
    """
    search DB to find whether proposed expr ID already exists

    >>> create_expr_id(False, 'pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    global_expr_ids_in_use = list(dat["expressions"].keys())

    found_valid_id = False
    loop_count = 0
    while not found_valid_id:
        loop_count += 1
        proposed_global_expr_id = str(
            random.randint(1000000000, 9999999999)
        )  # 10 digits

        if proposed_global_expr_id not in global_expr_ids_in_use:
            found_valid_id = True
        if loop_count > 10000000000:
            logger.error("too many; this seems unlikely")
            raise Exception("this seems unlikely")
    return proposed_global_expr_id


def create_step_id(path_to_db: str) -> str:
    """
    aka step ID

    search DB to find whether proposed local ID already exists
    >>> create_step_id(False, 'pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    step_ids_in_use = []
    for deriv_id in dat["derivations"].keys():
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            step_ids_in_use.append(step_id)  # formerly 'inf rule local ID'

    found_valid_id = False
    loop_count = 0
    while not found_valid_id:
        loop_count += 1
        proposed_step_id = str(random.randint(1000000, 9999999))  # 7 digits
        if proposed_step_id not in step_ids_in_use:
            found_valid_id = True
        if loop_count > 10000000000:
            logger.error("too many reached; this seems unlikely")
            raise Exception("this seems unlikely")
    return proposed_step_id


def create_expr_local_id(path_to_db: str) -> str:
    """
    search DB to find whether proposed local ID already exists
    >>> create_expr_local_id(False, 'pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    local_ids_in_use = list(dat["expr local to global"].keys())

    found_valid_id = False
    loop_count = 0
    while not found_valid_id:
        loop_count += 1
        proposed_local_id = str(random.randint(1000000, 9999999))  # 7 digits
        if proposed_local_id not in local_ids_in_use:
            found_valid_id = True
        if loop_count > 10000000000:
            logger.error("unlikely")
            raise Exception("this seems unlikely")
    return proposed_local_id


# *******************************************
# stats


def file_tail(full_path_to_file: str, number_of_lines_of_log_tail: int) -> list:
    """
    >>> 
    """
    logger.info("[trace]")
    lines = []
    tail_of_log_as_list = []
    with open(full_path_to_file, "r") as f:
        lines = f.readlines()
    tail_of_log_as_list = lines[-1 * number_of_lines_of_log_tail :]
    return tail_of_log_as_list


def generate_auth_summary() -> list:
    """
    >>> generate_auth_summary()
    """
    logger.info("[trace]")

    df = logs_to_stats.auth_log_to_df(
        "/home/appuser/app/logs/auth.log", "/home/appuser/app/static/iso3166.csv"
    )

    logger.debug("generated df from auth log")

    creation_date = datetime.datetime.now().strftime("%Y-%m-%d")

    list_of_picture_names = []

    pic_name = "unique_usernames_" + creation_date + ".png"
    if not os.path.exists("/home/appuser/app/static/" + pic_name):
        logs_to_stats.plot_username_distribution(
            df, "/home/appuser/app/static/", pic_name
        )
    list_of_picture_names.append(pic_name)

    pic_name = "unique_IP_address_per_day_" + creation_date + ".png"
    if not os.path.exists("/home/appuser/app/static/" + pic_name):
        logs_to_stats.plot_ip_vs_time(df, "/home/appuser/app/static/", pic_name)
    list_of_picture_names.append(pic_name)

    pic_name = "unique_user_names_per_day_" + creation_date + ".png"
    if not os.path.exists("/home/appuser/app/static/" + pic_name):
        logs_to_stats.plot_username_vs_time(df, "/home/appuser/app/static/", pic_name)
    list_of_picture_names.append(pic_name)

    pic_name = (
        "unique_IP_address_per_country_above_threshold_per_day_"
        + creation_date
        + ".png"
    )
    if not os.path.exists("/home/appuser/app/static/" + pic_name):
        logs_to_stats.plot_country_per_day_vs_time(
            df, "/home/appuser/app/static/", pic_name
        )
    list_of_picture_names.append(pic_name)

    return list_of_picture_names


# ********************************************
# popularity


def flatten_dict(d: dict, sep: str = "_") -> dict:
    """
    convert the AST structure
    'AST': {'equals': [ {'nabla': ['2911']},{'function': ['1452']}]}}
    to
    {'equals_0_nabla_0': '2911', 'equals_1_function_0': '1452'}

    from https://medium.com/better-programming/how-to-flatten-a-dictionary-with-nested-lists-and-dictionaries-in-python-524fd236365

    >>> flatten_dict({},'_')
    """
    obj = collections.OrderedDict()

    def recurse(t, parent_key=""):
        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t

    recurse(d)
    return dict(obj)


def extract_operators_from_expression_dict(expr_id: str, path_to_db: str) -> list:
    """
    >>>
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    expr_dict = dat["expressions"]
    if "AST" in expr_dict[expr_id].keys():
        flt_dict = flatten_dict(expr_dict[expr_id]["AST"])
    else:
        flt_dict = {}
    list_of_str = list(flt_dict.keys())
    list_of_operators = []
    for this_str in list_of_str:  # 'equals_0_addition_0'
        list_of_operator_candidates = this_str.split("_")
        for operator_candidate in list_of_operator_candidates:
            try:
                int(operator_candidate)
            except ValueError:
                list_of_operators.append(operator_candidate)
    return list(set(list_of_operators))


def extract_symbols_from_expression_dict(expr_id: str, path_to_db: str) -> list:
    """
    >>> extract_symbols_from_expression_dict('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    logger.debug("expr_id = %s", expr_id)
    expr_dict = dat["expressions"]
    if "AST" in expr_dict[expr_id].keys():
        flt_dict = flatten_dict(expr_dict[expr_id]["AST"])
        return list(flt_dict.values())
    else:
        return []
    # logger.debug('flt_dict=',flt_dict)


def extract_expressions_from_derivation_dict(deriv_id: str, path_to_db: str) -> list:
    """
    >>>
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    flt_dict = flatten_dict(dat["derivations"][deriv_id])
    logger.debug("flat dict = %s", flt_dict)
    list_of_expr_ids = []
    for flattened_key, val in flt_dict.items():
        if (
            ("_inputs_" in flattened_key)
            or ("_outputs_" in flattened_key)
            or ("_feeds_" in flattened_key)
        ):
            list_of_expr_ids.append(val)
    logger.debug(
        "list_of_expr_ids= %s", list_of_expr_ids,
    )
    return list_of_expr_ids


def popularity_of_derivations(path_to_db: str) -> dict:
    """
    output:
    derivations_popularity_dict['name of deriv']['number of steps'] = 4
    derivations_popularity_dict['name of deriv']['shares expressions with'] = ['fun deriv', 'another deriv']

    >>> popularity_of_derivations('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    derivations_popularity_dict = {}
    expressions_per_derivation = {}
    for deriv_id in dat["derivations"].keys():
        derivations_popularity_dict[deriv_id] = {
            "number of steps": len(list(dat["derivations"][deriv_id]["steps"].keys())),
            "shares expressions with": [],
        }
        # which expressions are shared?
        # first, build a list of expr_global_id per derivation
        # logger.debug('build a list of expr_global_id per derivation')
        expressions_per_derivation[deriv_id] = []
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            for connection_type in ["inputs", "feeds", "outputs"]:
                for expr_local_id in step_dict[connection_type]:
                    expressions_per_derivation[deriv_id].append(
                        dat["expr local to global"][expr_local_id]
                    )
        # logger.debug('remove duplicates')
        # remove duplicates
        expressions_per_derivation[deriv_id] = list(
            set(expressions_per_derivation[deriv_id])
        )
    # logger.debug('find intersections')
    # find intersections

    for deriv_id1, list1_of_expr_global_id in expressions_per_derivation.items():
        for deriv_id2, list2_of_expr_global_id in expressions_per_derivation.items():
            if deriv_id1 != deriv_id2:
                for expr_global_id1 in list1_of_expr_global_id:
                    if expr_global_id1 in list2_of_expr_global_id:
                        tup = (deriv_id2, expr_global_id1)
                        # logger.debug(str(tup))
                        derivations_popularity_dict[deriv_id1][
                            "shares expressions with"
                        ].append(tup)

    return derivations_popularity_dict


def popularity_of_operators(path_to_db: str) -> dict:
    """
    >>> popularity_of_operators('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    operator_popularity_dict = {}

    operators_per_expr = {}
    for expr_id, expr_dict in dat["expressions"].items():
        if "AST" in expr_dict.keys():
            flt_dict = flatten_dict(expr_dict["AST"])
        else:
            flt_dict = {}
        list_of_str = list(flt_dict.keys())
        list_of_operators = []
        for this_str in list_of_str:  # 'equals_0_addition_0'
            list_of_operator_candidates = this_str.split("_")
            for operator_candidate in list_of_operator_candidates:
                try:
                    int(operator_candidate)
                except ValueError:
                    list_of_operators.append(operator_candidate)
        operators_per_expr[expr_id] = list(set(list_of_operators))

    for operator, operator_dict in dat["operators"].items():
        operator_popularity_dict[operator] = []
        for expr_id, list_of_ops in operators_per_expr.items():
            if operator in list_of_ops:
                operator_popularity_dict[operator].append(expr_id)
    return operator_popularity_dict


def popularity_of_symbols_in_expressions(path_to_db: str) -> dict:
    """
    >>> popularity_of_symbols_in_expressions('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    symbol_popularity_dict = {}
    # TODO: this is a join that is really slow!
    for symbol_id, symbol_dict in dat["symbols"].items():
        list_of_uses = []
        for expr_global_id, expr_dict in dat["expressions"].items():
            if "AST" in expr_dict.keys():
                flt_dict = flatten_dict(expr_dict["AST"])
                list_of_symbols_for_this_expr = list(flt_dict.values())
            else:
                list_of_symbols_for_this_expr = []
            if symbol_id in list_of_symbols_for_this_expr:
                list_of_uses.append(expr_global_id)
        symbol_popularity_dict[symbol_id] = list_of_uses

    return symbol_popularity_dict


def popularity_of_symbols_in_derivations(path_to_db: str) -> dict:
    """
    >>> popularity_of_symbols_in_derivations('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    symbol_popularity_dict_in_deriv = {}

    # symbol per expression
    symbol_popularity_dict_in_expr = popularity_of_symbols_in_expressions(path_to_db)
    # logger.debug(str(symbol_popularity_dict_in_expr))

    # expression per derivation
    expression_popularity_dict = popularity_of_expressions(path_to_db)
    # logger.debug(str(expression_popularity_dict))

    for symbol_id, list_of_expr in symbol_popularity_dict_in_expr.items():
        # logger.debug(symbol_id)
        this_symbol_is_in_derivations = []
        for expr_global_id in list_of_expr:
            # logger.debug(expr_global_id)
            for deriv_id in expression_popularity_dict[expr_global_id]:
                this_symbol_is_in_derivations.append(deriv_id)
        # logger.debug(this_symbol_is_in_derivations)
        # logger.debug(symbol_id)
        symbol_popularity_dict_in_deriv[symbol_id] = list(
            set(this_symbol_is_in_derivations)
        )

    return symbol_popularity_dict_in_deriv


def popularity_of_expressions(path_to_db: str) -> dict:
    """
    >>> popularity_of_expressions('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    expression_popularity_dict = {}

    deriv_uses_expr_global_id = {}
    for deriv_id in dat["derivations"].keys():
        list_of_all_expr_global_IDs_for_this_deriv = []
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            for connection_type in ["inputs", "feeds", "outputs"]:
                for expr_local_id in step_dict[connection_type]:
                    list_of_all_expr_global_IDs_for_this_deriv.append(
                        dat["expr local to global"][expr_local_id]
                    )
        # logger.debug(deriv_id + ":" + str(list_of_all_expr_global_IDs_for_this_deriv))

        deriv_uses_expr_global_id[deriv_id] = list(
            set(list_of_all_expr_global_IDs_for_this_deriv)
        )

    for expr_global_id, expr_dict in dat["expressions"].items():
        expression_popularity_dict[expr_global_id] = []
        for deriv_id, list_of_expr in deriv_uses_expr_global_id.items():
            if expr_global_id in list_of_expr:
                expression_popularity_dict[expr_global_id].append(deriv_id)
        expression_popularity_dict[expr_global_id] = list(
            set(expression_popularity_dict[expr_global_id])
        )

    # logger.debug("expression_popularity_dict = %s", expression_popularity_dict)
    return expression_popularity_dict


def popularity_of_infrules(path_to_db: str) -> dict:
    """
    >>> popularity_of_infrules('pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    infrule_popularity_dict = {}
    for infrule_name, infrule_dict in dat["inference rules"].items():
        list_of_uses = []
        for deriv_id in dat["derivations"].keys():
            list_of_infrules = []
            for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
                list_of_infrules.append(step_dict["inf rule"])

            list_of_infrule_for_this_deriv = list(set(list_of_infrules))

            # logger.debug('popularity_of_infrules; list =',list_of_infrule_for_this_deriv)
            # logger.debug('popularity_of_infrules; infrule_name =',infrule_name)
            if infrule_name in list_of_infrule_for_this_deriv:
                list_of_uses.append(deriv_id)
        infrule_popularity_dict[infrule_name] = list_of_uses
    return infrule_popularity_dict


# ********************************************
# local filesystem


def remove_file_debris(
    list_of_paths_to_files: list, list_of_file_names: list, list_of_file_ext: list
) -> None:
    """
    >>> remove_file_debris(['/path/to/file/'],['filename_without_extension'], ['ext1', 'ext2'])
    """
    logger.info("[trace]")

    for path_to_file in list_of_paths_to_files:
        #        logger.debug('path_to_file =',path_to_file)
        for file_name in list_of_file_names:
            #            logger.debug('file_name =',file_name)
            for file_ext in list_of_file_ext:
                #                logger.debug('file_ext =',file_ext)

                if os.path.isfile(path_to_file + file_name + "." + file_ext):
                    os.remove(path_to_file + file_name + "." + file_ext)
    #    logger.debug('done')
    return


# *******************************************
# create files on filesystem


def generate_all_expr_and_infrule_pngs(
    overwrite_existing: bool, path_to_db: str
) -> None:
    """
    >>> generate_all_expr_and_infrule_pngs()
    """
    logger.info("[trace]")

    dat = clib.read_db(path_to_db)
    destination_folder = "/home/appuser/app/static/"

    for expr_global_id, expr_dict in dat["expressions"].items():
        png_name = expr_global_id
        if overwrite_existing:
            if os.path.isfile(destination_folder + png_name):
                os.remove(destination_folder + png_name + ".png")
        else:  # do not overwrite existing PNG
            if not os.path.isfile(destination_folder + png_name + ".png"):
                logger.debug("PNG does not exist, creating %s", png_name)
                create_png_from_latex(
                    dat["expressions"][expr_global_id]["latex"], png_name
                )

    for infrule_name, infrule_dict in dat["inference rules"].items():
        png_name = "".join(filter(str.isalnum, infrule_name))
        if overwrite_existing:
            if os.path.isfile(destination_folder + png_name):
                os.remove(destination_folder + png_name + ".png")
        else:  # do not overwrite existing PNG
            if not os.path.isfile(destination_folder + png_name + ".png"):
                logger.debug("PNG does not exist, creating %s", png_name)
                create_png_from_latex(infrule_name, png_name)
    return


def create_tex_file_for_expr(tmp_file: str, input_latex_str: str) -> None:
    """
    >>> create_tex_file_for_expr('filename_without_extension', 'a \dot b \\nabla')
    """
    logger.info("[trace]")

    remove_file_debris(["./"], [tmp_file], ["tex"])

    with open(tmp_file + ".tex", "w") as lat_file:
        lat_file.write("\\documentclass[12pt]{article}\n")
        lat_file.write("\\thispagestyle{empty}\n")
        # https://tex.stackexchange.com/questions/73016/how-do-i-install-an-individual-package-on-a-linux-system
        # if "usepackage{braket}" is on and the package isn't available, the process pauses while waiting for user input
        # the web interface isn't aware of this pause, so the page hangs
        # lat_file.write("\\usepackage{braket}\n")
        lat_file.write(
            "\\usepackage{amsmath}\n"
        )  # https://tex.stackexchange.com/questions/32100/what-does-each-ams-package-do
        # lat_file.write("\\newcommand{\\when}[1]{{\\rm \\ when\\ }#1}\n")
        # lat_file.write("\\newcommand{\\bra}[1]{\\langle #1 |}\n")
        # lat_file.write("\\newcommand{\\ket}[1]{| #1\\rangle}\n")
        # lat_file.write("\\newcommand{\\op}[1]{\\hat{#1}}\n")
        # lat_file.write("\\newcommand{\\braket}[2]{\\langle #1 | #2 \\rangle}\n")
        # lat_file.write(
        #    "\\newcommand{\\rowCovariantColumnContravariant}[3]{#1_{#2}^{\\ \\ #3}} % left-bottom, right-upper\n"
        # )
        # lat_file.write(
        #    "\\newcommand{\\rowContravariantColumnCovariant}[3]{#1^{#2}_{\\ \\ #3}} % left-upper, right-bottom\n"
        # )

        lat_file.write("\\begin{document}\n")
        lat_file.write("\\huge{\n")
        lat_file.write("$" + input_latex_str + "$\n")
        lat_file.write("}\n")
        lat_file.write("\\end{document}\n")
    # logger.debug("wrote tex file")
    return


def generate_d3js_json_map_of_derivations(path_to_db: str) -> str:
    """
    >>> generate_d3js_json_map_of_derivations()
    """
    logger.info("[trace]")
    derivation_popularity_dict = popularity_of_derivations(path_to_db)
    # logger.debug("derivation_popularity_dict = %s", str(derivation_popularity_dict))

    dat = clib.read_db(path_to_db)

    #    json_filename = "all_derivations.json"
    #    with open(json_filename, "w") as fil:
    json_str = ""

    json_str += "{ \n"
    json_str += '  "nodes": [\n'

    if True:
        list_of_nodes = []
        list_of_edges = []

        for deriv_id, deriv_dict in derivation_popularity_dict.items():
            # https://stackoverflow.com/questions/22520932/python-remove-all-non-alphabet-chars-from-string
            this_deriv = deriv_id
            if not os.path.isfile(
                "/home/appuser/app/static/" + this_deriv + "_name" + ".png"
            ):
                create_png_from_latex(
                    "\\text{"
                    + dat["derivations"][deriv_id]["name"].replace("^", "")
                    + "}",
                    this_deriv + "_name",
                )
            image = cv2.imread(
                "/home/appuser/app/static/" + this_deriv + "_name" + ".png"
            )
            list_of_nodes.append(
                '    {"id": "'
                + this_deriv
                + '", "group": 0, "img": "/static/'
                + this_deriv
                + "_name"
                + '.png", '
                + '"width": '
                + str(image.shape[1])
                + ", "
                + '"height": '
                + str(image.shape[0])
                + ', "linear index": 0},\n'
            )

        for deriv_id, deriv_dict in derivation_popularity_dict.items():
            this_deriv = deriv_id
            for tup in deriv_dict["shares expressions with"]:
                other_deriv_name = tup[0]
                expr_global_id = tup[1]
                if not os.path.isfile(
                    "/home/appuser/app/static/" + expr_global_id + ".png"
                ):
                    expr_latex = dat["expressions"][expr_global_id]["latex"]
                    create_png_from_latex(expr_latex, expr_global_id)
                image = cv2.imread(
                    "/home/appuser/app/static/" + expr_global_id + ".png"
                )
                list_of_nodes.append(
                    '    {"id": "'
                    + expr_global_id
                    + '", "group": 1, "img": "/static/'
                    + expr_global_id
                    + '.png", '
                    + '"width": '
                    + str(image.shape[1])
                    + ", "
                    + '"height": '
                    + str(image.shape[0])
                    + ', "linear index": 0},\n'
                )

                list_of_edges.append(
                    '    {"source": "'
                    + this_deriv
                    + '", "target": "'
                    + expr_global_id
                    + '", "value": 1},\n'
                )
                list_of_edges.append(
                    '    {"source": "'
                    + other_deriv_name
                    + '", "target": "'
                    + expr_global_id
                    + '", "value": 1},\n'
                )

    list_of_nodes = list(set(list_of_nodes))
    all_nodes = "".join(list_of_nodes)
    all_nodes = (
        all_nodes[:-2] + "\n"
    )  # remove the trailing comma to be compliant with JSON
    json_str += all_nodes

    json_str += "  ],\n"
    json_str += '  "links": [\n'

    list_of_edges = list(set(list_of_edges))
    all_edges = "".join(list_of_edges)
    all_edges = all_edges[:-2] + "\n"
    json_str += all_edges

    json_str += "  ]\n"
    json_str += "}"

    json_filename = "all_derivations.json"
    with open(json_filename, "w") as fil:
        fil.write(json_str)

    shutil.move(json_filename, "/home/appuser/app/static/" + json_filename)
    return json_filename


def generate_graphviz_map_of_derivations(path_to_db: str) -> str:
    """
    for a clear description of the graphviz language, see
    https://www.graphviz.org/doc/info/lang.html

    potentially relevant: https://graphviz.gitlab.io/_pages/Gallery/undirected/fdpclust.html

    >>> generate_map_of_derivations()
    """
    logger.info("[trace]")
    derivation_popularity_dict = popularity_of_derivations(path_to_db)
    # logger.debug("derivation_popularity_dict = %s", str(derivation_popularity_dict))

    dat = clib.read_db(path_to_db)

    dot_filename = "/home/appuser/app/static/graphviz.dot"
    with open(dot_filename, "w") as fil:
        fil.write("graph physicsDerivation { \n")
        # the following can cause graphviz to crash; see
        # https://github.com/allofphysicsgraph/proofofconcept/issues/2
        # fil.write("overlap = false;\n")
        fil.write(
            "overlap = prism;\n"
        )  # https://www.graphviz.org/doc/info/attrs.html#d:overlap
        fil.write(
            "pack = true;\n"
        )  # https://www.graphviz.org/doc/info/attrs.html#d:pack
        fil.write('label="all derivations\nhttps://derivationmap.net";\n')
        fil.write("fontsize=12;\n")

        for deriv_id, deriv_dict in derivation_popularity_dict.items():
            # https://stackoverflow.com/questions/22520932/python-remove-all-non-alphabet-chars-from-string
            this_deriv = deriv_id
            if not os.path.isfile("/home/appuser/app/static/" + this_deriv + ".png"):
                create_png_from_latex(
                    "\\text{"
                    + dat["derivations"][deriv_id]["name"].replace("^", "")
                    + "}",
                    this_deriv,
                )
            fil.write(
                '"'
                + this_deriv
                + '" [shape=invtrapezium, color=blue, label="",image="/home/appuser/app/static/'
                + this_deriv
                + ".png"
                + '",labelloc=b];\n'
            )

        list_of_edges = []
        list_of_nodes = []

        for deriv_id, deriv_dict in derivation_popularity_dict.items():
            this_deriv = deriv_id
            for tup in deriv_dict["shares expressions with"]:
                other_deriv_name = tup[0]
                expr_global_id = tup[1]
                if not os.path.isfile(
                    "/home/appuser/app/static/" + expr_global_id + ".png"
                ):
                    expr_latex = dat["expressions"][expr_global_id]["latex"]
                    create_png_from_latex(expr_latex, expr_global_id)

                list_of_nodes.append(
                    expr_global_id
                    + ' [shape=ellipse, color=black,label="",image="/home/appuser/app/static/'
                    + expr_global_id
                    + ".png"
                    + '",labelloc=b];\n'
                )
                list_of_edges.append(
                    '"' + this_deriv + '" -- ' + expr_global_id + ";\n"
                )
                list_of_edges.append(
                    '"' + other_deriv_name + '" -- ' + expr_global_id + ";\n"
                )

        for this_node in set(list_of_nodes):
            fil.write(this_node)
        for this_edge in set(list_of_edges):
            fil.write(this_edge)

        fil.write("}\n")
    output_filename = "all_derivation.png"
    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
    #    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = subprocess.run(
        ["neato", "-Tpng", dot_filename, "-o" + output_filename],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )
    neato_stdout = process.stdout.decode("utf-8")
    if len(neato_stdout) > 0:
        logger.debug(neato_stdout)
    neato_stderr = process.stderr.decode("utf-8")
    if len(neato_stderr) > 0:
        logger.debug(neato_stderr)

    shutil.move(output_filename, "/home/appuser/app/static/" + output_filename)
    return output_filename


def write_step_to_graphviz_file(
    deriv_id: str, step_id: str, fil: TextIO, path_to_db: str
) -> None:
    """
    >>> fil = open('a_file','r')
    >>> write_step_to_graphviz_file("deriv name", "492482", fil, False, 'pdg.db')
    """
    logger.info("[trace]")

    dat = clib.read_db(path_to_db)

    step_dict = dat["derivations"][deriv_id]["steps"][step_id]
    logger.debug("step_dict = %s", step_dict)
    #  step_dict = {'inf rule': 'begin derivation', 'inputs': [], 'feeds': [], 'outputs': ['526874110']}
    #    for global_id, latex_and_ast_dict in dat["expressions"].items():
    #        logger.debug(
    #            "expr_dict has %s %s",
    #            global_id,
    #            latex_and_ast_dict["latex"],
    #        )

    png_name = "".join(filter(str.isalnum, step_dict["inf rule"]))
    if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
        create_png_from_latex("\\text{" + step_dict["inf rule"] + "}", png_name)
    fil.write(
        step_id
        + ' [shape=invtrapezium, color=blue, label="",image="/home/appuser/app/static/'
        + png_name
        + ".png"
        + '",labelloc=b];\n'
    )

    for expr_local_id in step_dict["inputs"]:
        expr_global_id = dat["expr local to global"][expr_local_id]
        png_name = expr_global_id
        if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
            create_png_from_latex(dat["expressions"][expr_global_id]["latex"], png_name)
        fil.write(expr_local_id + " -> " + step_id + ";\n")
        fil.write(
            expr_local_id
            + ' [shape=ellipse, color=black,label="",image="/home/appuser/app/static/'
            + png_name
            + ".png"
            + '",labelloc=b];\n'
        )

    for expr_local_id in step_dict["outputs"]:
        expr_global_id = dat["expr local to global"][expr_local_id]
        png_name = expr_global_id
        if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
            create_png_from_latex(dat["expressions"][expr_global_id]["latex"], png_name)
        fil.write(step_id + " -> " + expr_local_id + ";\n")
        fil.write(
            expr_local_id
            + ' [shape=ellipse, color=black,label="",image="/home/appuser/app/static/'
            + png_name
            + ".png"
            + '",labelloc=b];\n'
        )

    for expr_local_id in step_dict["feeds"]:
        expr_global_id = dat["expr local to global"][expr_local_id]
        png_name = expr_global_id
        if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
            create_png_from_latex(dat["expressions"][expr_global_id]["latex"], png_name)
        fil.write(expr_local_id + " -> " + step_id + ";\n")
        fil.write(
            expr_local_id
            + ' [shape=box, color=red,label="",image="/home/appuser/app/static/'
            + png_name
            + ".png"
            + '",labelloc=b];\n'
        )

    return  # True, "no invalid latex"


def generate_tex_for_derivation(deriv_id: str, path_to_db: str) -> str:
    """
    In this iteration of the PDG (v7), I allow for inference rule names
    to have spaces. In previous versions, the inference rule names were
    camel case. When I implemented this function, I learned why the
    inference rule names had been camel case: Latex doesn't like
    newcommand names to have underscore in them; see https://tex.stackexchange.com/questions/306110/new-command-with-an-underscore
    Therefore, I remove all spaces from the inference rule name

    >>> generate_tex_for_derivation()
    """

    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    path_to_tex = "/home/appuser/app/static/"  # must end with /
    tex_filename = deriv_id

    remove_file_debris([path_to_tex, "./"], [tex_filename], ["tex", "log", "pdf"])

    with open(tex_filename + ".tex", "w") as lat_file:
        lat_file.write(
            "% this tex file was generated by the Physics Derivation Graph \n"
        )
        lat_file.write("\\documentclass[12pt]{article}\n")  # article or report
        #        lat_file.write('\\thispagestyle{empty}\n')
        lat_file.write(
            "\\usepackage{amsmath,amssymb,amsfonts}\n"
        )  # https://tex.stackexchange.com/questions/32100/what-does-each-ams-package-do
        lat_file.write(
            "\\usepackage[dvipdfmx,colorlinks=true,pdfkeywords={physics derivation graph}]{hyperref}\n"
        )
        # lat_file.write("\\newcommand{\\when}[1]{{\\rm \\ when\\ }#1}\n")
        # lat_file.write("\\newcommand{\\bra}[1]{\\langle #1 |}\n")
        # lat_file.write("\\newcommand{\\ket}[1]{| #1\\rangle}\n")
        # lat_file.write("\\newcommand{\\op}[1]{\\hat{#1}}\n")
        # lat_file.write("\\newcommand{\\braket}[2]{\\langle #1 | #2 \\rangle}\n")
        # lat_file.write(
        #    "\\newcommand{\\rowCovariantColumnContravariant}[3]{#1_{#2}^{\\ \\ #3}} % left-bottom, right-upper\n"
        # )
        # lat_file.write(
        #    "\\newcommand{\\rowContravariantColumnCovariant}[3]{#1^{#2}_{\\ \\ #3}} % left-upper, right-bottom\n"
        # )

        # first, write the inference rules as newcommand at top of .tex file
        lat_file.write("% inference rules as newcommand for use in the body\n")
        for infrule_name, infrule_dict in dat["inference rules"].items():
            number_of_args = (
                infrule_dict["number of feeds"]
                + infrule_dict["number of inputs"]
                + infrule_dict["number of outputs"]
            )
            # https://en.wikibooks.org/wiki/LaTeX/Macros#New_commands
            lat_file.write(
                "\\newcommand\\"
                + "".join(
                    filter(str.isalpha, infrule_name)
                )  # digits cannot be used to name macros
                + "["
                + str(  # https://tex.stackexchange.com/questions/306110/new-command-with-an-underscore
                    number_of_args
                )
                + "]{"
                + infrule_dict["latex"]
                + "}\n"
            )

        # extract the list of linear index from the derivation
        list_of_linear_index = []
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            list_of_linear_index.append(step_dict["linear index"])

        list_of_linear_index.sort()
        lat_file.write("\\title{" + dat["derivations"][deriv_id]["name"] + "}\n")
        lat_file.write("\\date{\\today}\n")
        # TODO: include author (based on signed in account)
        lat_file.write("\\setlength{\\topmargin}{-.5in}\n")
        lat_file.write("\\setlength{\\textheight}{9in}\n")
        lat_file.write("\\setlength{\\oddsidemargin}{0in}\n")
        lat_file.write("\\setlength{\\textwidth}{6.5in}\n")

        lat_file.write("\\begin{document}\n")
        lat_file.write("\\maketitle\n")

        lat_file.write("\\begin{abstract}\n")
        lat_file.write(
            "Generated by the \\href{http://derivationmap.net/}{Physics Derivation Graph}\n"
        )
        lat_file.write("\\end{abstract}\n")

        for linear_indx in list_of_linear_index:
            for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
                if step_dict["linear index"] == linear_indx:
                    # using the newcommand, populate the expression IDs
                    if step_dict["inf rule"] not in dat["inference rules"].keys():
                        logger.error(
                            "inference rule in step is not in dat['inference rules']: ",
                            step_dict["inf rule"],
                        )
                        raise Exception(
                            "inference rule in step is not in dat['inference rules']: ",
                            step_dict["inf rule"],
                        )
                    lat_file.write("% step ID = " + step_id + "\n")
                    lat_file.write(
                        # digits cannot be used to name macros
                        "\\"
                        + "".join(filter(str.isalpha, step_dict["inf rule"]))
                    )
                    for expr_local_id in step_dict["feeds"]:
                        expr_global_id = dat["expr local to global"][expr_local_id]
                        lat_file.write(
                            "{" + dat["expressions"][expr_global_id]["latex"] + "}"
                        )
                    for expr_local_id in step_dict["inputs"]:
                        expr_global_id = dat["expr local to global"][expr_local_id]
                        lat_file.write("{" + expr_local_id + "}")
                    for expr_local_id in step_dict["outputs"]:
                        expr_global_id = dat["expr local to global"][expr_local_id]
                        lat_file.write("{" + expr_local_id + "}")
                    lat_file.write("\n")
                    # write output expressions
                    for expr_local_id in step_dict["outputs"]:
                        expr_global_id = dat["expr local to global"][expr_local_id]
                        lat_file.write("\\begin{equation}\n")
                        lat_file.write(
                            dat["expressions"][expr_global_id]["latex"] + "\n"
                        )
                        lat_file.write("\\label{eq:" + expr_local_id + "}\n")
                        lat_file.write("\\end{equation}\n")
        lat_file.write("\\end{document}\n")
        lat_file.write("% EOF\n")

    shutil.copy(tex_filename + ".tex", path_to_tex + tex_filename + ".tex")
    return tex_filename + ".tex"


def generate_pdf_for_derivation(deriv_id: str, path_to_db: str) -> str:
    """
    >>> generate_pdf_for_derivation()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    path_to_pdf = "/home/appuser/app/static/"  # must end with /
    pdf_filename = deriv_id

    remove_file_debris([path_to_pdf], [pdf_filename], ["log", "pdf"])

    tex_filename_with_extension = generate_tex_for_derivation(deriv_id, path_to_db)

    # first of two latex runs
    process = subprocess.run(
        ["latex", "-halt-on-error", tex_filename_with_extension],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )
    # https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
    latex_stdout = process.stdout.decode("utf-8")
    latex_stderr = process.stderr.decode("utf-8")

    logger.debug("latex std out: %s", latex_stdout)
    logger.debug("latex std err: %s", latex_stderr)

    if "Text line contains an invalid character" in latex_stdout:
        logger.error("no PDF generated - tex contains invalid character")
        raise Exception("no PDF generated - tex contains invalid character")
    if "No pages of output." in latex_stdout:
        logger.error("no PDF generated - reason unknown")
        raise Exception("no PDF generated - reason unknown")

    # run latex a second time to enable references to work
    process = subprocess.run(
        ["latex", "-halt-on-error", tex_filename_with_extension],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )

    # https://tex.stackexchange.com/questions/73783/dvipdfm-or-dvipdfmx-or-dvipdft
    # TODO: how does dvipdfmx know the name of the .tex input? In the process below only the output filename is specified (!)
    process = subprocess.run(
        ["dvipdfmx", pdf_filename + ".dvi"],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )

    dvipdf_stdout = process.stdout.decode("utf-8")
    dvipdf_stderr = process.stderr.decode("utf-8")

    logger.debug("dvipdf std out: %s", dvipdf_stdout)
    logger.debug("dvipdf std err: %s", dvipdf_stderr)

    shutil.move(pdf_filename + ".pdf", path_to_pdf + pdf_filename + ".pdf")

    # return True, pdf_filename + ".pdf"
    return pdf_filename + ".pdf"


def list_expr_in_step(deriv_id: str, step_id: str, path_to_db: str) -> list:
    """
    >>> list_expr_in_step()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_global_expr = []
    for connection_type in ["feeds", "inputs", "outputs"]:
        for local_id in dat["derivations"][deriv_id]["steps"][step_id][connection_type]:
            expr_global_id = dat["expr local to global"][local_id]
            list_of_global_expr.append(expr_global_id)
    return list_of_global_expr


def list_expr_in_derivation(deriv_id: str, path_to_db: str) -> list:
    """
    returns a list of global expression IDs for a given derivation

    >>> list_expr_in_derivation('my deriv', 'pdg.db')
    """
    logger.info("[trace]")

    dat = clib.read_db(path_to_db)
    list_of_local_expr = []
    for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
        for connection_type in ["feeds", "inputs", "outputs"]:
            for local_expr in step_dict[connection_type]:
                list_of_local_expr.append(local_expr)
    list_of_local_expr = list(set(list_of_local_expr))
    list_of_global_expr = []
    for local_expr in list_of_local_expr:
        list_of_global_expr.append(dat["expr local to global"][local_expr])
    logger.debug("number of expr = %s", len(list_of_global_expr))
    # logger.debug(str(list_of_global_expr))
    return list_of_global_expr


def update_linear_index(
    deriv_id: str, step_id: str, valu: str, path_to_db: str
) -> None:
    """
    # https://github.com/allofphysicsgraph/proofofconcept/issues/116
    >>> modify_linear_index()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if "." not in valu:
        valu = str(int(valu))
    else:
        valu = str(float(valu))
    if deriv_id in dat["derivations"].keys():
        if step_id in dat["derivations"][deriv_id]["steps"].keys():
            dat["derivations"][deriv_id]["steps"][step_id]["linear index"] = valu
        else:
            logger.error("missing " + step_id + " in " + deriv_id)
            raise Exception("missing " + step_id + " in " + deriv_id)
    else:
        logger.error("missing " + deriv_id)
        raise Exception("missing " + deriv_id)
    clib.write_db(path_to_db, dat)
    return


def edges_in_derivation(deriv_id: str, path_to_db: str) -> list:
    """
    >>> edges_in_derivation
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    list_of_edges = []
    for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
        inf_rule = "".join(filter(str.isalnum, step_dict["inf rule"]))
        for local_expr in step_dict["inputs"]:
            list_of_edges.append((dat["expr local to global"][local_expr], step_id))
        for local_expr in step_dict["feeds"]:
            list_of_edges.append((dat["expr local to global"][local_expr], step_id))
        for local_expr in step_dict["outputs"]:
            list_of_edges.append((step_id, dat["expr local to global"][local_expr]))
    list_of_edges = list(set(list_of_edges))
    # logger.debug('number of edges = %s', len(list_of_edges))
    return list_of_edges


def create_d3js_json(deriv_id: str, path_to_db: str) -> str:
    """
    Produce a JSON file that contains something like
{
  "nodes": [
    {"id": "Myriel", "group": 1, "img": "/static/test.png", "width": 138, "height": 39, "linear index": 1},
    {"id": "Napoleon", "group": 1, "img": "/static/test.png", "width": 138, "height": 39, "linear index": 2}
  ],
  "links": [
    {"source": "Napoleon", "target": "Myriel", "value": 1},
    {"source": "Mlle.Baptistine", "target": "Myriel", "value": 8}
  ]
}

    for inspiration based on the last time I implemented this, see
    v3_CSV/bin/create_json_per_derivation_from_connectionsDB.py

    >>> create_d3js_json('my deriv', 'pdg.db')
    """
    logger.info("[trace]")

    d3js_json_filename = deriv_id + ".json"

    dat = clib.read_db(path_to_db)

    json_str = "{\n"
    json_str += '  "nodes": [\n'
    list_of_nodes = []
    for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
        png_name = "".join(filter(str.isalnum, step_dict["inf rule"]))
        if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
            create_png_from_latex(step_dict["inf rule"], png_name)
        image = cv2.imread("/home/appuser/app/static/" + png_name + ".png")
        # construct the node JSON content
        list_of_nodes.append(
            '    {"id": "'
            + step_id
            + '", "group": '
            + str(step_dict["linear index"])
            + ", "
            + '"img": "/static/'
            + png_name
            + '.png", '
            + '"width": '
            + str(image.shape[1])
            + ", "
            + '"height": '
            + str(image.shape[0])
            + ", "
            + '"linear index": '
            + str(step_dict["linear index"])
            + "},\n"
        )

    list_of_expr = list_expr_in_derivation(deriv_id, path_to_db)
    for global_expr_id in list_of_expr:
        png_name = global_expr_id
        if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
            create_png_from_latex(dat["expressions"][global_expr_id]["latex"], png_name)
        image = cv2.imread("/home/appuser/app/static/" + png_name + ".png")
        # construct the node JSON content
        list_of_nodes.append(
            '    {"id": "'
            + global_expr_id
            + '", "group": 0, '
            + '"img": "/static/'
            + png_name
            + '.png", '
            + '"width": '
            + str(image.shape[1])
            + ", "
            + '"height": '
            + str(image.shape[0])
            + ", "
            + '"linear index": 0},\n'
        )

    list_of_nodes = list(set(list_of_nodes))
    all_nodes = "".join(list_of_nodes)
    all_nodes = (
        all_nodes[:-2] + "\n"
    )  # remove the trailing comma to be compliant with JSON
    json_str += all_nodes

    json_str += "  ],\n"
    json_str += '  "links": [\n'

    list_of_edges = edges_in_derivation(deriv_id, path_to_db)
    list_of_edge_str = []
    for edge_tuple in list_of_edges:
        list_of_edge_str.append(
            '    {"source": "'
            + edge_tuple[0]
            + '", "target": "'
            + edge_tuple[1]
            + '", "value": 1},\n'
        )
    list_of_edge_str = list(set(list_of_edge_str))
    # logger.debug('number of edges = %s', len(list_of_edge_str))
    all_edges = "".join(list_of_edge_str)
    all_edges = all_edges[:-2] + "\n"
    # logger.debug('all edges = %s', all_edges)
    json_str += all_edges
    json_str += "  ]\n"
    json_str += "}\n"
    with open("/home/appuser/app/static/" + d3js_json_filename, "w") as fil:
        fil.write(json_str)

    return d3js_json_filename


def create_derivation_png(deriv_id: str, path_to_db: str) -> str:
    """
    for a clear description of the graphviz language, see
    https://www.graphviz.org/doc/info/lang.html

    >>> create_derivation_png()
    """
    logger.info("[trace]")

    dat = clib.read_db(path_to_db)

    dot_filename = "/home/appuser/app/static/graphviz.dot"
    with open(dot_filename, "w") as fil:
        fil.write("digraph physicsDerivation { \n")
        fil.write("overlap = false;\n")
        fil.write(
            'label="derivation: '
            + dat["derivations"][deriv_id]["name"]
            + '\nhttps://derivationmap.net";\n'
        )
        fil.write("fontsize=12;\n")

        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            write_step_to_graphviz_file(deriv_id, step_id, fil, path_to_db)

        fil.write("}\n")
    output_filename = deriv_id + ".png"
    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
    #    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = subprocess.run(
        ["neato", "-Tpng", dot_filename, "-o" + output_filename],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )

    neato_stdout = process.stdout.decode("utf-8")
    if len(neato_stdout) > 0:
        logger.debug(neato_stdout)
    neato_stderr = process.stderr.decode("utf-8")
    if len(neato_stderr) > 0:
        logger.debug(neato_stderr)

    shutil.move(output_filename, "/home/appuser/app/static/" + output_filename)
    # return True, "no invalid latex", output_filename
    return output_filename


def create_step_graphviz_png(deriv_id: str, step_id: str, path_to_db: str) -> str:
    """
    for a clear description of the graphviz language, see
    https://www.graphviz.org/doc/info/lang.html

    >>> step_dict = {'inf rule':'add X to both sides',
                     'inf rule local ID':'2948592',
                     'inputs':[{'expr local ID':'9428', 'expr ID':'4928923942'}],
                     'feeds':[{'feed local ID':'319', 'feed latex':'k'],
                     'outputs':[{'expr local ID':'3921', 'expr ID':'9499959299'}]}
    >>> create_step_graphviz_png(step_dict, 'my derivation', False)

    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    dot_filename = "/home/appuser/app/static/graphviz.dot"
    remove_file_debris(["/home/appuser/app/static/"], ["graphviz"], ["dot"])

    with open(dot_filename, "w") as fil:
        fil.write("digraph physicsDerivation { \n")
        fil.write("overlap = false;\n")
        fil.write(
            'label="step '
            + step_id
            + " in "
            + dat["derivations"][deriv_id]["name"]
            + '\nhttps://derivationmap.net";\n'
        )
        fil.write("fontsize=12;\n")

        write_step_to_graphviz_file(deriv_id, step_id, fil, path_to_db)
        fil.write("}\n")

    #    with open(dot_filename,'r') as fil:
    #       logger.debug(fil.read())

    output_filename = step_id + ".png"
    logger.debug("output_filename = %s", output_filename)
    remove_file_debris(["./"], ["graphviz"], ["png"])

    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
    #    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = subprocess.run(
        ["neato", "-Tpng", dot_filename, "-o" + output_filename],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )
    neato_stdout = process.stdout.decode("utf-8")
    if len(neato_stdout) > 0:
        logger.debug(neato_stdout)
    neato_stderr = process.stderr.decode("utf-8")
    if len(neato_stderr) > 0:
        logger.debug(neato_stderr)

    shutil.move(output_filename, "/home/appuser/app/static/" + output_filename)
    # return True, "no invalid latex", output_filename
    return output_filename


def generate_graphviz_of_step_with_numeric_IDs(
    deriv_id: str, step_id: str, path_to_db: str
) -> str:
    """
    https://github.com/allofphysicsgraph/proofofconcept/issues/108
    >>> generate_graphviz_of_step_with_numeric_IDs()
    """
    logger.info("[trace]")
    dot_filename = "/home/appuser/app/static/graphviz.dot"
    dat = clib.read_db(path_to_db)
    if deriv_id in dat["derivations"].keys():
        if step_id in dat["derivations"][deriv_id]["steps"].keys():
            step_dict = dat["derivations"][deriv_id]["steps"][step_id]
        else:
            logger.error(
                "step_id " + step_id + " not in " + dat["derivations"][deriv_id]["name"]
            )
            raise Exception(
                "step_id " + step_id + " not in " + dat["derivations"][deriv_id]["name"]
            )
    else:
        logger.error(deriv_id + " not in database")
        raise Exception(deriv_id + " not in database")

    remove_file_debris(["/home/appuser/app/static/"], ["graphviz"], ["dot"])
    with open(dot_filename, "w") as fil:
        fil.write("digraph physicsDerivation { \n")
        fil.write("overlap = false;\n")
        fil.write(
            'label="step '
            + step_id
            + " in "
            + dat["derivations"][deriv_id]["name"]
            + '\nhttps://derivationmap.net";\n'
        )
        fil.write("fontsize=12;\n")

        # the following code is similar to write_step_to_graphviz_file()
        infrule_png_name = "".join(filter(str.isalnum, step_dict["inf rule"]))
        if not os.path.isfile("/home/appuser/app/static/" + infrule_png_name + ".png"):
            create_png_from_latex(
                "\\text{" + step_dict["inf rule"] + "}", infrule_png_name
            )
        fil.write(
            infrule_png_name
            + ' [shape=invtrapezium, color=blue, label="",image="/home/appuser/app/static/'
            + infrule_png_name
            + ".png"
            + '",labelloc=b];\n'
        )

        stepid_png_name = "step_id_" + step_id
        if not os.path.isfile("/home/appuser/app/static/" + stepid_png_name + ".png"):
            create_png_from_latex(
                "\\text{" + step_dict["inf rule"] + "}", stepid_png_name
            )
        fil.write(
            step_id
            + ' [shape=invtrapezium, color=blue, label="",image="/home/appuser/app/static/'
            + stepid_png_name
            + ".png"
            + '",labelloc=b];\n'
        )
        fil.write(infrule_png_name + " -> " + step_id + ";\n")

        for expr_local_id in step_dict["inputs"]:
            # TODO:
            # latex -> global_id -> local_id -> step_id

            expr_global_id = dat["expr local to global"][expr_local_id]
            latex_png_name = expr_global_id
            if not os.path.isfile(
                "/home/appuser/app/static/" + latex_png_name + ".png"
            ):
                create_png_from_latex(
                    dat["expressions"][expr_global_id]["latex"], latex_png_name
                )
            fil.write(expr_local_id + " -> " + step_id + ";\n")
            fil.write(
                expr_local_id
                + ' [shape=ellipse, color=black,label="",image="/home/appuser/app/static/'
                + latex_png_name
                + ".png"
                + '",labelloc=b];\n'
            )

        for expr_local_id in step_dict["outputs"]:
            # TODO:
            # step_id -> local_id -> global_id -> latex

            expr_global_id = dat["expr local to global"][expr_local_id]
            png_name = expr_global_id
            if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
                create_png_from_latex(
                    dat["expressions"][expr_global_id]["latex"], png_name
                )
            fil.write(step_id + " -> " + expr_local_id + ";\n")
            fil.write(
                expr_local_id
                + ' [shape=ellipse, color=black,label="",image="/home/appuser/app/static/'
                + png_name
                + ".png"
                + '",labelloc=b];\n'
            )

        for expr_local_id in step_dict["feeds"]:
            expr_global_id = dat["expr local to global"][expr_local_id]
            png_name = expr_global_id
            if not os.path.isfile("/home/appuser/app/static/" + png_name + ".png"):
                create_png_from_latex(
                    dat["expressions"][expr_global_id]["latex"], png_name
                )
            fil.write(expr_local_id + " -> " + step_id + ";\n")
            fil.write(
                expr_local_id
                + ' [shape=box, color=red,label="",image="/home/appuser/app/static/'
                + png_name
                + ".png"
                + '",labelloc=b];\n'
            )

    output_filename = step_id + "_with_numeric_IDs.png"
    logger.debug("output_filename = %s", output_filename)
    remove_file_debris(["./"], ["graphviz"], ["png"])

    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
    #    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = subprocess.run(
        ["neato", "-Tpng", dot_filename, "-o" + output_filename],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )
    neato_stdout = process.stdout.decode("utf-8")
    if len(neato_stdout) > 0:
        logger.debug(neato_stdout)
    neato_stderr = process.stderr.decode("utf-8")
    if len(neato_stderr) > 0:
        logger.debug(neato_stderr)

    shutil.move(output_filename, "/home/appuser/app/static/" + output_filename)
    # return True, "no invalid latex", output_filename
    return output_filename


def create_png_from_latex(input_latex_str: str, png_name: str) -> None:
    """
    this function relies on latex  being available on the command line
    this function relies on dvipng being available on the command line
    this function assumes generated PNG should be placed in /home/appuser/app/static/
    >>> create_png_from_latex('a \dot b \\nabla', False)
    """
    logger.info("[trace]")

    destination_folder = "/home/appuser/app/static/"

    #    logger.debug("png_name = %s", png_name)
    #    logger.debug("input latex str = %s", input_latex_str)

    # TODO: I'd like to have the latex build process take place in an isolated directory
    # instead of the /home/appuser/app/ location used now
    tmp_file = "lat"
    remove_file_debris(["./tmp"], [tmp_file], ["tex", "dvi", "aux", "log"])

    # logger.debug('create_png_from_latex: finished debris removal, starting create tex file')

    logger.debug("latex = " + str(input_latex_str))
    create_tex_file_for_expr(tmp_file, input_latex_str)

    # logger.debug('create_png_from_latex: running latex against file')

    # logger.debug(str(os.listdir()))

    process = subprocess.run(
        ["latex", "-halt-on-error", tmp_file + ".tex"],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )
    # https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
    latex_stdout = process.stdout.decode("utf-8")
    latex_stderr = process.stderr.decode("utf-8")

    #    logger.debug(str(os.listdir()))

    logger.debug("latex std out:" + str(latex_stdout))
    logger.debug("latex std err:" + str(latex_stderr))

    if "Text line contains an invalid character" in latex_stdout:
        logging.error("tex input contains invalid charcter")
        shutil.copy(destination_folder + "error.png", destination_folder + png_name)
        raise Exception("no png generated due to invalid character in tex input.")
    #    remove_file_debris(["./"], [tmp_file], ["png"])

    process = subprocess.run(
        ["dvipng", tmp_file + ".dvi", "-T", "tight", "-o", tmp_file + ".png"],
        stdout=PIPE,
        stderr=PIPE,
        timeout=proc_timeout,
    )
    # https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
    png_stdout = process.stdout.decode("utf-8")
    png_stderr = process.stderr.decode("utf-8")

    if len(png_stdout) > 0:
        if "This is dvipng" not in png_stdout:
            logger.debug("png std out %s", png_stdout)
    if len(png_stderr) > 0:
        logger.debug("png std err %s", png_stderr)

    # logger.debug(str(os.listdir()))

    if "No such file or directory" in png_stderr:
        logging.error("PNG creation failed for %s", png_name)
        shutil.copy(destination_folder + "error.png", destination_folder + png_name)
        # return False, "no PNG created. Check usepackage in latex"
        raise Exception(
            "no PNG created for " + png_name + ". Check 'usepackage' in latex"
        )

    shutil.move(tmp_file + ".png", destination_folder + png_name + ".png")

    logger.debug(destination_folder + png_name + ".png")

    #    if os.path.isfile(destination_folder + png_name):
    # os.remove('/home/appuser/app/static/'+name_of_png)
    #        logger.debug("[ERROR] create_png_from_latex: png already exists!")

    # return True, "success"
    return


# *********************************************************
# data structure transformations


def modify_latex_in_step(
    expr_local_id_of_latex_to_modify: str, revised_latex: str, path_to_db: str
) -> None:
    """
    >>> modify_latex_in_step('959242', 'a = b', 'pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    expr_global_id = create_expr_global_id(path_to_db)

    entry = {}
    entry["latex"] = revised_latex
    entry["creation date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    entry["author"] = "Ben"
    entry["notes"] = dat["expressions"][
        dat["expr local to global"][expr_local_id_of_latex_to_modify]
    ]["notes"]
    entry["name"] = dat["expressions"][
        dat["expr local to global"][expr_local_id_of_latex_to_modify]
    ]["name"]
    entry["AST"] = []

    dat["expressions"][expr_global_id] = entry
    dat["expr local to global"][expr_local_id_of_latex_to_modify] = expr_global_id

    clib.write_db(path_to_db, dat)
    return


def delete_step_from_derivation(
    deriv_id: str, step_to_delete: str, path_to_db: str
) -> None:
    """
    >>> delete_step_from_derivation
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if deriv_id in dat["derivations"].keys():
        if step_to_delete in dat["derivations"][deriv_id]["steps"].keys():
            del dat["derivations"][deriv_id]["steps"][step_to_delete]
            clib.write_db(path_to_db, dat)
        else:
            raise Exception(step_to_delete + " not in derivations dat")
    else:
        raise Exception(deriv_id + " not in derivations dat")
    return


def delete_derivation(deriv_id: str, path_to_db: str) -> str:
    """
    >>> delete_derivation('my cool deriv', 'pdg.db')

    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    # TODO: if expr is only used in this derivation, does the user want dangling expressions removed?
    if deriv_id in dat["derivations"].keys():
        del dat["derivations"][deriv_id]
    else:
        raise Exception("name of derivation not in dat")
    clib.write_db(path_to_db, dat)
    return "successfully deleted " + deriv_id


def add_symbol(
    category: str,
    latex: str,
    name: str,
    dimension: str,
    reference: str,
    value: str,
    units: str,
    scope: str,
    path_to_db: str,
) -> None:
    """
    >>> add_symbol()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)

    symbol_dict = {}
    symbol_dict["category"] = category
    symbol_dict["latex"] = latex
    symbol_dict["name"] = name
    symbol_dict["measure"] = dimension
    symbol_dict["scope"] = scope
    symbol_dict["references"] = [reference]
    if category == "constant" and len(value) > 0:
        symbol_dict["value"] = value
        symbol_dict["units"] = units
    symbol_dict["author"] = "Ben"
    symbol_dict["creation date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    symbol_id = create_symbol_id(path_to_db)
    logger.debug("new symbol ID:" + symbol_id)
    dat["symbols"][symbol_id] = symbol_dict

    logger.debug(str(symbol_dict))
    clib.write_db(path_to_db, dat)

    return


def add_inf_rule(inf_rule_dict_from_form: dict, path_to_db: str) -> str:
    """
    >>> request.form = ImmutableMultiDict([('inf_rule_name', 'testola'), ('num_inputs', '1'), ('num_feeds', '0'), ('num_outputs', '0'), ('latex', 'adsfmiangasd')])
    >>> add_inf_rule(request.form.to_dict(), 'pdg.db')
    """
    logger.info("[trace]")

    # create a data structure similar to
    #   'begin derivation':         {'number of feeds':0, 'number of inputs':0, 'number of outputs': 1, 'latex': 'more'}
    arg_dict = {}
    status_msg = ""
    try:
        arg_dict["number of feeds"] = int(inf_rule_dict_from_form["num_feeds"])
    except ValueError as err:
        return "number of feeds does not seem to be an integer"
    try:
        arg_dict["number of inputs"] = int(inf_rule_dict_from_form["num_inputs"])
    except ValueError as err:
        return "number of inputs does not seem to be an integer"
    try:
        arg_dict["number of outputs"] = int(inf_rule_dict_from_form["num_outputs"])
    except ValueError as err:
        return "number of outputs does not seem to be an integer"
    arg_dict["latex"] = inf_rule_dict_from_form["latex"]
    arg_dict["notes"] = inf_rule_dict_from_form["notes"]
    arg_dict["author"] = "Ben"
    arg_dict["creation date"] = datetime.datetime.now().strftime("%Y-%m-%d")

    logger.debug("add_inf_rule; arg_dict = %s", arg_dict)

    dat = clib.read_db(path_to_db)
    if inf_rule_dict_from_form["inf_rule_name"] in dat["inference rules"].keys():
        status_msg = "inference rule already exists"
        logger.error(status_msg)
        raise Exception(status_msg)
    else:
        dat["inference rules"][inf_rule_dict_from_form["inf_rule_name"]] = arg_dict
        clib.write_db(path_to_db, dat)
        status_msg = "success"
    return status_msg


def delete_inf_rule(name_of_inf_rule: str, path_to_db: str) -> str:
    """
    >>> delete_inf_rule('multbothsidesbyx','pdg.db')
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    infrule_popularity_dict = popularity_of_infrules(path_to_db)
    # logger.debug('name_of_inf_rule',name_of_inf_rule)
    # logger.debug(infrule_popularity_dict)

    if len(infrule_popularity_dict[name_of_inf_rule]) > 0:
        status_message = (
            name_of_inf_rule
            + " cannot be deleted because it is used in "
            + str(infrule_popularity_dict[name_of_inf_rule])
        )
        return status_message
    if name_of_inf_rule in dat["inference rules"].keys():
        del dat["inference rules"][name_of_inf_rule]
        status_msg = name_of_inf_rule + " deleted"
        clib.write_db(path_to_db, dat)

    else:
        status_msg = name_of_inf_rule + " does not exist in database"
    return status_msg


def add_symbol_to_expr(expr_global_id: str, symbol_id: str, path_to_db: str) -> None:
    """
    >>> 
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    if expr_global_id in dat["expressions"].keys():
        if symbol_id in dat["symbols"].keys():
            dat["expressions"][expr_global_id]["AST"].append(symbol_id)
            clib.write_db(path_to_db, dat)
        else:
            raise Exception(symbol_id + " is not in symbols")
    else:
        raise Exception(expr_global_id + " is not in expressions list")
    return


def edit_expr_note(expr_global_id: str, new_note: str, path_to_db: str) -> str:
    """
    >>>
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if expr_global_id in dat["expressions"].keys():
        dat["expressions"][expr_global_id]["notes"] = new_note
        status_msg = "updated note"
        clib.write_db(path_to_db, dat)
    else:
        status_msg = expr_global_id + " is not in expressions"
        logger.error(status_msg)
    return status_msg


def edit_expr_name(expr_global_id: str, new_name: str, path_to_db: str) -> str:
    """
    >>>
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if expr_global_id in dat["expressions"].keys():
        dat["expressions"][expr_global_id]["name"] = new_name
        status_msg = "updated name to " + new_name
        clib.write_db(path_to_db, dat)
    else:
        status_msg = expr_global_id + " is not in expressions"
        logger.error(status_msg)
    return status_msg


def edit_step_note(deriv_id: str, step_id: str, new_note: str, path_to_db: str) -> str:
    """
    >>> edit_step_note()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if deriv_id in dat["derivations"].keys():
        if step_id in dat["derivations"][deriv_id]["steps"].keys():
            dat["derivations"][deriv_id]["steps"][step_id]["notes"] = new_note
            status_msg = "updated note"
            clib.write_db(path_to_db, dat)
        else:
            status_msg = step_id + " is not in derivation " + deriv_id
            logger.error(step_id + " is not in derivation " + deriv_id)
    else:
        status_msg = deriv_id + " is not in dat"
        logger.error(deriv_id + " is not in dat")
    return status_msg


def edit_derivation_note(deriv_id: str, new_note: str, path_to_db: str) -> str:
    """
    >>> edit_derivation_note()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if deriv_id in dat["derivations"].keys():
        dat["derivations"][deriv_id]["notes"] = new_note
        status_msg = "updated note"
        clib.write_db(path_to_db, dat)
    else:
        status_msg = deriv_id + " does not appear in derivations; no change made"
        logger.error(status_msg)
    return status_msg


def rename_derivation(deriv_id: str, new_name: str, path_to_db: str) -> str:
    """
    >>> rename_derivation()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if deriv_id in dat["derivations"].keys():
        dat["derivations"][deriv_id]["name"] = new_name
        status_msg = "renamed to " + new_name
        clib.write_db(path_to_db, dat)
    else:
        status_msg = deriv_id + " does not appear in derivations; no change made"
    return status_msg


def rename_inf_rule(
    old_name_of_inf_rule: str, new_name_of_inf_rule: str, path_to_db: str
) -> str:
    """
    >>> rename_inf_rule()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if old_name_of_inf_rule in dat["inference rules"].keys():
        dat["inference rules"][new_name_of_inf_rule] = dat["inference rules"][
            old_name_of_inf_rule
        ]
        del dat["inference rules"][old_name_of_inf_rule]

        # rename inf_rule in dat['derivations']
        for deriv_id in dat["derivations"].keys():
            for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
                if step_dict["inf rule"] == old_name_of_inf_rule:
                    dat["derivations"][deriv_id]["steps"][step_id][
                        "inf rule"
                    ] = new_name_of_inf_rule

        status_msg = (
            old_name_of_inf_rule
            + " renamed to "
            + new_name_of_inf_rule
            + "\n and references in derivations were updated"
        )
    else:
        status_msg = (
            old_name_of_inf_rule + " does not exist in database; no action taken"
        )
    clib.write_db(path_to_db, dat)
    return status_msg


def edit_operator_latex(operator: str, revised_latex: str, path_to_db: str) -> str:
    """
    >>> edit_operator_latex()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if operator in dat["operators"].keys():
        dat["operators"][operator]["latex"] = revised_latex
        status_msg = operator + "updated"
    else:
        status_msg = operator + " does not exist in database"
    clib.write_db(path_to_db, dat)
    return status_msg


def edit_symbol_latex(symbol: str, revised_latex: str, path_to_db: str) -> str:
    """
    >>> edit_symbol_latex()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if symbol in dat["symbols"].keys():
        dat["symbols"][symbol]["latex"] = revised_latex
        status_msg = symbol + " updated"
    else:
        status_msg = symbol + " does not exist in database"
    clib.write_db(path_to_db, dat)
    return status_msg


def edit_inf_rule_latex(inf_rule_name: str, revised_latex: str, path_to_db: str) -> str:
    """
    >>> edit_inf_rule_latex()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if inf_rule_name in dat["inference rules"].keys():
        dat["inference rules"][inf_rule_name]["latex"] = revised_latex
        status_msg = inf_rule_name + " updated"
    else:
        status_msg = inf_rule_name + " does not exist in database"
    clib.write_db(path_to_db, dat)
    return status_msg


def edit_expr_latex(expr_id: str, revised_latex: str, path_to_db: str) -> str:
    """
    http://asciiflow.com/
    suppose there is a step that has the following

                                   +--------------------+    +------------+
                       +---------> | old global expr ID |--->+ old latex  |
                       |           +--------------------+    +------------+
               +-------+-------+
        +----->+ expr local ID |
        |      +---------------+
    +---+-----+
    | step ID |
    +---+-----+
        |      +---------------+
        +----->+ inf rule name |
               +---------------+

    after the change, we have

               +---------------+
        +----->+ expr local ID |
        |      +-------+-------+
    +---+-----+        |            +--------------------+  +-----------+
    | step ID |        +----------->+ new global expr ID |  | new latex |
    +---+-----+                     +--------------------+  +-----------+
        |      +---------------+
        +----->+ inf rule name |
               +---------------+


    >>> edit_expr_latex()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    if expr_id in dat["expressions"].keys():
        dat["expressions"][expr_id]["latex"] = revised_latex
        status_msg = expr_id + " updated"
    else:
        status_msg = expr_id + " not in database"
    clib.write_db(path_to_db, dat)
    return status_msg


def delete_symbol(symbol_to_delete: str, path_to_db: str) -> str:
    """
    >>> delete_symbol()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    symbol_popularity_dict = popularity_of_symbols_in_expressions(path_to_db)
    if len(symbol_popularity_dict[symbol_to_delete]) > 0:
        status_msg = (
            symbol_to_delete
            + " cannot be deleted because it is in use in "
            + str(symbol_popularity_dict[symbol_to_delete])
        )
    else:
        del dat["symbols"][symbol_to_delete]
        status_message = "successfully deleted " + symbol_to_delete
    clib.write_db(path_to_db, dat)
    return status_msg


def delete_operator(operator_to_delete: str, path_to_db: str) -> str:
    """
    >>> delete_operator()
    """
    logger.info("[trace]")
    dat = clib.read_db(path_to_db)
    status_msg = ""
    operator_popularity_dict = popularity_of_operators(path_to_db)
    if len(operator_popularity_dict[operator_to_delete]) > 0:
        status_msg = (
            operator_to_delete
            + " cannot be deleted because it is in use in "
            + str(operator_popularity_dict[operator_to_delete])
        )
    else:
        del dat["symbols"][operator_to_delete]
        status_message = "successfully deleted " + operator_to_delete
    clib.write_db(path_to_db, dat)
    return status_msg


def delete_expr(expr_global_id: str, path_to_db: str) -> str:
    """
    >>> delete_expr()
    """
    logger.info("[trace]")
    status_message = ""
    dat = clib.read_db(path_to_db)
    expression_popularity_dict = popularity_of_expressions(path_to_db)
    if len(expression_popularity_dict[expr_global_id]) > 0:
        status_message = (
            expr_global_id
            + " cannot be deleted because it is in use in "
            + str(expression_popularity_dict[expr_global_id])
        )
    else:  # expr is not in use
        del dat["expressions"][expr_global_id]
        status_message = "successfully deleted " + expr_global_id
    logger.debug("delete_expr; dat[expr].keys = %s", dat["expressions"].keys())
    clib.write_db(path_to_db, dat)
    return status_message


def initialize_derivation(
    name_of_derivation: str, current_username: str, notes: str, path_to_db: str
) -> str:
    """
    >>> initialize_derivation()
    """
    logger.info("[trace] " + current_username)
    dat = clib.read_db(path_to_db)
    deriv_id = create_deriv_id(path_to_db)
    dat["derivations"][deriv_id] = {
        "name": name_of_derivation,
        "author": current_username,
        "notes": notes,
        "creation date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "steps": {},
    }
    clib.write_db(path_to_db, dat)

    return deriv_id


def create_step(
    latex_for_step_dict: dict,
    inf_rule: str,
    deriv_id: str,
    user_name: str,
    path_to_db: str,
) -> str:
    """
    https://strftime.org/

    >>> latex_for_step_dict = ImmutableMultiDict([('input1', ''), ('input1_radio', 'global'), ('input1_global_id', '5530148480'), ('feed1', 'asgasgag'), ('output1', ''), ('output1_radio', 'global'), ('output1_global_id', '9999999951'), ('submit_button', 'Submit')])

# prior to the radio buttons, this was the style:
#    >>> latex_for_step_dict = ImmutableMultiDict([('output1', 'a = b')])
#    >>> create_step(latex_for_step_dict, 'begin derivation', 'deriv name', False, 'pdg.db')
#    9492849
    """
    logger.info("[trace]")

    dat = clib.read_db(path_to_db)

    if deriv_id not in dat["derivations"].keys():
        logger.debug(deriv_id + "was not in derivations; it has been added.")
        dat["derivations"][deriv_id] = {}

    # because the form is an immutable dict, we need to convert to dict before deleting keys
    # https://tedboy.github.io/flask/generated/generated/werkzeug.ImmutableMultiDict.html
    latex_for_step_dict = latex_for_step_dict.to_dict(flat=True)
    logger.debug("latex_for_step_dict = %s", latex_for_step_dict)

    step_dict = {
        "inf rule": inf_rule,
        "inputs": [],
        "feeds": [],
        "outputs": [],
        "linear index": -1,
        "notes": latex_for_step_dict["step_note"],
        "author": user_name,
        "creation date": datetime.datetime.now().strftime("%Y-%m-%d"),
    }  # type: STEP_DICT
    # if we observe 'linear index'==-1 outside this function, it indicates a problem

    logger.debug("initialized step_dict to %s", str(step_dict))

    # start with feeds since those are the easiest
    for key, text in latex_for_step_dict.items():
        if "static_feed" in key:  # novel latex
            # logger.debug("in feed for " + text)
            expr_global_id = create_expr_global_id(path_to_db)
            dat["expressions"][expr_global_id] = {
                "latex": latex_for_step_dict[key],
                "AST": [],
                "name": "",
                "notes": "",
                "author": "Ben",
                "creation date": datetime.datetime.now().strftime("%Y-%m-%d"),
            }
            expr_local_id = create_expr_local_id(path_to_db)
            dat["expr local to global"][expr_local_id] = expr_global_id
            step_dict["feeds"].append(expr_local_id)
        elif "dynamic_feed" in key:  # reference to existing expression ID
            step_dict["feeds"].append(latex_for_step_dict[key])

    logger.debug("entered feed to dat")

    for connection_type in ["input", "output"]:
        for expr_index in ["1", "2", "3"]:
            for key, text in latex_for_step_dict.items():
                # logger.debug("key = " + key)
                if "_radio" in key and connection_type in key and expr_index in key:
                    logger.debug(connection_type + " " + expr_index + "; radio")
                    if text == "latex":
                        # logger.debug('latex')
                        expr_global_id = create_expr_global_id(path_to_db)
                        if latex_for_step_dict[connection_type + expr_index] == "":
                            logger.error("empty Latex is not accepted")
                            raise Exception("empty Latex is not accepted")
                        dat["expressions"][expr_global_id] = {
                            "latex": latex_for_step_dict[connection_type + expr_index],
                            "AST": [],
                            "name": latex_for_step_dict[
                                connection_type + expr_index + "_name"
                            ],
                            "notes": latex_for_step_dict[
                                connection_type + expr_index + "_note"
                            ],
                            "author": "Ben",
                            "creation date": datetime.datetime.now().strftime(
                                "%Y-%m-%d"
                            ),
                        }
                        expr_local_id = create_expr_local_id(path_to_db)
                        dat["expr local to global"][expr_local_id] = expr_global_id
                        step_key = connection_type + "s"
                        step_dict[step_key].append(expr_local_id)
                    elif text == "local":
                        # logger.debug('local')
                        # logger.debug('step dict = ' + str(latex_for_step_dict.keys()))
                        # logger.debug('new' + latex_for_step_dict[connection_type  + expr_index + '_local_id'])
                        expr_local_id = latex_for_step_dict[
                            connection_type + expr_index + "_local_id"
                        ]
                        step_key = connection_type + "s"
                        step_dict[step_key].append(expr_local_id)
                    elif text == "global":
                        # logger.debug('global')
                        # logger.debug(connection_type + expr_index + '_global_id')
                        # logger.debug('keys = ' + str(latex_for_step_dict.keys()))
                        expr_global_id = latex_for_step_dict[
                            connection_type + expr_index + "_global_id"
                        ]
                        # logger.debug('got global id: ' + expr_global_id)
                        expr_local_id = create_expr_local_id(path_to_db)
                        # logger.debug('local id: ' + expr_local_id)
                        dat["expr local to global"][expr_local_id] = expr_global_id
                        # logger.debug('added to dat' + str(dat["expr local to global"][expr_local_id]))
                        step_key = connection_type + "s"
                        step_dict[step_key].append(expr_local_id)
                        # logger.debug('end of global')
                    else:
                        logger.error("unknown radio option: ", key, text)
                        raise Exception("unknown radio option: ", key, text)
                    # logger.debug('end of loop')
    logger.debug("step_dict = " + str(step_dict))

    #    inputs_and_outputs_to_delete = []
    #    for which_eq, latex_expr_str in latex_for_step_dict.items():
    #        if (
    #            "use_ID_for" in which_eq
    #        ):  # 'use_ID_for_in1' or 'use_ID_for_in2' or 'use_ID_for_out1', etc
    #            # the following leverages the dict from the web form
    #            # request.form = ImmutableMultiDict([('input1', '1492842000'), ('use_ID_for_in1', 'on'), ('submit_button', 'Submit')])
    #            logger.debug("create_step; use_ID_for is in %s", which_eq)
    #            if "for_in" in which_eq:
    #                this_input = "input" + which_eq[-1]
    #                expr_local_id = latex_for_step_dict[this_input]
    #                step_dict["inputs"].append(expr_local_id)
    #                inputs_and_outputs_to_delete.append(this_input)
    #            elif "for_out" in which_eq:
    #                this_output = "output" + which_eq[-1]
    #                expr_local_id = latex_for_step_dict[this_input]
    #                step_dict["inputs"].append(expr_local_id)
    #                inputs_and_outputs_to_delete.append(this_output)
    #            else:
    #                raise Exception(
    #                    "[ERROR] compute; create_step; unrecognized key in use_ID ",
    #                    latex_for_step_dict,
    #                )
    #
    #    # remove all the "use_ID_for" keys
    #    list_of_keys = list(latex_for_step_dict.keys())
    #    for this_key in list_of_keys:
    #        if "use_ID_for" in this_key:
    #            del latex_for_step_dict[this_key]
    #
    #    # remove the inputs and outputs that were associated with 'use_ID_for'
    #    for input_and_output in inputs_and_outputs_to_delete:
    #        del latex_for_step_dict[input_and_output]
    #
    #    for which_eq, latex_expr_str in latex_for_step_dict.items():
    #        logger.debug(
    #            "create_step; which_eq = %s and latex_expr_str = %s",
    #            which_eq,
    #            latex_expr_str,
    #        )
    #        if "input" in which_eq:
    #            expr_global_id = create_expr_global_id(path_to_db)
    #            dat["expressions"][expr_global_id] = {
    #                "latex": latex_expr_str
    #            }  # , 'AST': latex_as_AST}
    #            expr_local_id = create_expr_local_id(path_to_db)
    #            dat["expr local to global"][expr_local_id] = expr_global_id
    #            step_dict["inputs"].append(expr_local_id)
    #        elif "output" in which_eq:
    #            expr_global_id = create_expr_global_id(path_to_db)
    #            dat["expressions"][expr_global_id] = {
    #                "latex": latex_expr_str
    #            }  # , 'AST': latex_as_AST}
    #            expr_local_id = create_expr_local_id(path_to_db)
    #            dat["expr local to global"][expr_local_id] = expr_global_id
    #            step_dict["outputs"].append(expr_local_id)
    #        elif "feed" in which_eq:
    #            expr_global_id = create_expr_global_id(path_to_db)
    #            dat["expressions"][expr_global_id] = {
    #                "latex": latex_expr_str
    #            }  # , 'AST': latex_as_AST}
    #            expr_local_id = create_expr_local_id(path_to_db)
    #            dat["expr local to global"][expr_local_id] = expr_global_id
    #            step_dict["feeds"].append(expr_local_id)
    #        elif "submit_button" in which_eq:
    #            pass
    #        else:
    #            raise Exception(
    #                "[ERROR] compute; create_step; unrecognized key in step dict",
    #                latex_for_step_dict,
    #            )

    list_of_linear_index = [0]

    if deriv_id in dat["derivations"].keys():
        for step_id, tmp_step_dict in dat["derivations"][deriv_id]["steps"].items():
            list_of_linear_index.append(tmp_step_dict["linear index"])
        highest_linear_index = max(list_of_linear_index)
        step_dict["linear index"] = highest_linear_index + 1
    else:  # new derivation
        logger.debug("create_step; new derivation so initializing linear index")
        step_dict["linear index"] = 1

    if step_dict["linear index"] == -1:
        logger.error("problem with linear index")
        raise Exception("problem with linear index!")
    logger.debug("create_step; step_dict = %s", step_dict)

    # add step_dict to dat, write dat to file
    inf_rule_local_ID = create_step_id(path_to_db)
    if deriv_id not in dat["derivations"].keys():
        logger.debug("create_step: starting new derivation")
        dat["derivations"][deriv_id]["steps"] = {inf_rule_local_ID: step_dict}
    else:  # derivation exists
        if inf_rule_local_ID in dat["derivations"][deriv_id]["steps"].keys():
            logger.error("collision of inf_rule_local_id already in dat")
            raise Exception(
                "collision of inf_rule_local_id already in dat", inf_rule_local_ID
            )
        dat["derivations"][deriv_id]["steps"][inf_rule_local_ID] = step_dict

    clib.write_db(path_to_db, dat)

    return inf_rule_local_ID


# the following was moved into controller.py so that when a single step fails the notice is provided to the user
# def determine_derivation_validity(deriv_id: str, path_to_db: str) -> dict:
#    """
#    >>> determine_derivation_validity()
#    """
#    logger.info("[trace]")
#    dat = clib.read_db(path_to_db)
#    step_validity_dict = {}
#
#    if deriv_id not in dat["derivations"].keys():
#        logger.error("dat does not contain " + deriv_id)
#        raise Exception("dat does not contain " + deriv_id)
#
#    for step_id, step_dict in dat["derivations"][deriv_id]['steps'].items():
#        step_validity_dict[step_id] = vir.validate_step(
#            deriv_id, step_id, path_to_db
#        )
#    return step_validity_dict


# def determine_step_validity(
#    step_id: str, deriv_id: str, path_to_db: str
# ) -> str:
#    """
#    >>> determine_step_validity()
#    """
#    logger.info("[trace]")
#    dat = clib.read_db(path_to_db)
#    step_validity_dict = {}
#
#    if deriv_id not in dat["derivations"].keys():
#        logger.error("dat does not contain " + deriv_id)
#        raise Exception("dat does not contain " + deriv_id)
#
#    if step_id not in dat["derivations"][deriv_id]['steps'].keys():
#        logger.error("dat does not contain " + step_id + " in " + deriv_id)
#        raise Exception("dat does not contain " + step_id + " in " + deriv_id)
#
#    return vir.validate_step(deriv_id, step_id, path_to_db)


# EOF
