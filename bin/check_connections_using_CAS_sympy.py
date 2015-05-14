#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# 
# depends on lib_physics_graph
# use: python bin/check_connections_using_CAS_sympy.py
# input: 
# output: 

import subprocess
import os.path
import sys
lib_path = os.path.abspath('lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

from xml.dom.minidom import parseString

import sympy # https://github.com/sympy/sympy/releases

def convert_xml_to_cas_array(type_str,xml_ary,symbols_array,check_this_connection):
  lhs_array=[]
  rhs_array=[]
  for stat in xml_ary[0].getElementsByTagName('statement_punid'):
    statement_punid=physgraf.remove_tags(stat.toxml(encoding="ascii"),'statement_punid')
    # now that we know the statement index, retrieve the CAS statements from statementsDB

    [statement_lhs,statement_rhs]=physgraf.convert_statement_punid_to_cas_sympy(statement_punid,statementsDB)
    symbol_punid_array=physgraf.convert_tpunid_to_symbol_punid_array(statement_punid,statementsDB,'statement')
    for indx in range(len(symbol_punid_array)):
      cas_sympy=physgraf.convert_symbol_punid_to_cas_sympy(symbol_punid_array[indx],symbolsDB)
      symbols_array.append(cas_sympy+" # from "+type_str)

    if ((statement_lhs != "empty") and (statement_rhs != "empty")):
      print(type_str+" statement index "+statement_punid)
      print(type_str+" lhs: " + statement_lhs)
      lhs_array.append(statement_lhs)
      print(type_str+" rhs: " + statement_rhs)
      rhs_array.append(statement_rhs)
    else:
      print(type_str+" statement index "+statement_punid+" is missing CAS expansion")
      check_this_connection=False
  return check_this_connection,lhs_array,rhs_array,symbols_array

def write_sympy_to_file(filename,symbols_array,out_lhs_array,out_rhs_array,\
        in_lhs_array,in_rhs_array,feed_array,inf_rule_sympy,this_inference_rule):
  CAS_file=open('tmp_sympy.py','w')
  CAS_file.write("# this file was written by check_connections_using_CAS_sympy.py\n")
  CAS_file.write("import sympy\n")
  for symbl_indx in range(len(symbols_array)):
    CAS_file.write(symbols_array[symbl_indx]+"\n")
  if (len(out_lhs_array)>0):
    CAS_file.write("out_lhs0="+out_lhs_array[0]+"\n")
    CAS_file.write("out_rhs0="+out_rhs_array[0]+"\n")
  if (len(out_lhs_array)>1):
    CAS_file.write("out_lhs1="+out_lhs_array[1]+"\n")
    CAS_file.write("out_rhs1="+out_rhs_array[1]+"\n")    
  if (len(in_lhs_array)>0):
    CAS_file.write("in_lhs0="+in_lhs_array[0]+"\n")
    CAS_file.write("in_rhs0="+in_rhs_array[0]+"\n")
  if (len(in_lhs_array)>1):
    CAS_file.write("in_lhs1="+in_lhs_array[1]+"\n")
    CAS_file.write("in_rhs1="+in_rhs_array[1]+"\n")    
  if (len(feed_array)>0):
    CAS_file.write("feed0="+feed_array[0]+"\n")
  if (len(feed_array)>1):
    CAS_file.write("feed1="+feed_array[1]+"\n")
  CAS_file.write("# "+this_inference_rule+" \n")
  CAS_file.write(inf_rule_sympy+"\n")
  CAS_file.write("if(rule_obeyed==True):\n")
  CAS_file.write("  print(True)\n")
  CAS_file.write("elif(rule_obeyed==False):\n")
  CAS_file.write("  print(False)\n")
  CAS_file.write("else:\n")
  CAS_file.write("  print(5)\n")
  CAS_file.write("# eof \n")    
  CAS_file.close()

def convert_feed_to_cas_array(inputs_xml,symbols_array,check_this_connection):
  feed_array=[]
  for feeed in inputs_xml[0].getElementsByTagName('feed_tunid'):
    feed_tunid=physgraf.remove_tags(feeed.toxml(encoding="ascii"),'feed_tunid')
    feed_sympy=physgraf.convert_feed_tunid_to_feed_sympy(feed_tunid,feedsDB)
#     for this_feed in feedsDB.getElementsByTagName('feed'):
#       this_feed_tunid=physgraf.convert_tag_to_content(this_feed,'feed_tunid',0)
#       if(this_feed_tunid==feed_tunid):
#         feed_cas=physgraf.convert_tag_to_content(this_feed,'feed_sympy',0)
    if (feed_sympy != "empty"):
      print("feed tunid "+feed_tunid+" is "+ feed_sympy)
      feed_array.append(feed_sympy)
      symbol_punid_array=physgraf.convert_tpunid_to_symbol_punid_array(feed_tunid,feedsDB,'feed')
      for indx in range(len(symbol_punid_array)):
        cas_sympy=physgraf.convert_symbol_punid_to_cas_sympy(symbol_punid_array[indx],symbolsDB)
        symbols_array.append(cas_sympy+" # from feed")
    else:
      print("feed label "+feed_tunid+" is missing CAS expansion")
      check_this_connection=False
  print(feed_array)
  return check_this_connection,feed_array,symbols_array

inference_rulesDB=physgraf.parse_XML_file(db_path+'/inference_rules_database.xml')
connectionsDB=physgraf.parse_XML_file(db_path+'/connections_database.xml')
statementsDB=physgraf.parse_XML_file(db_path+'/expressions_database.xml')
feedsDB=physgraf.parse_XML_file(db_path+'/feed_database.xml')
symbolsDB=physgraf.parse_XML_file(db_path+'/symbols_database.xml')

counter_array=[]
counter_array.append(0) # number_of_rules_not_checkable=0
counter_array.append(0) # number_of_checkable_rules_not_checked=0
counter_array.append(0) # number_of_tested_true_connections=0
counter_array.append(0) # number_of_tested_false_connections=0
counter_array.append(0) # number_of_connection_setups_with_error=0

for this_connection in connectionsDB.getElementsByTagName('connection'):
  check_this_connection=True
  #this_connection=physgraf.remove_tags(this_connection.toxml(encoding="ascii"),'connection')
  #print(this_connection)
  this_inference_rule=physgraf.convert_tag_to_content(this_connection,'infrule_name',0)
  if (this_inference_rule=="declareInitialEq" or \
      this_inference_rule=="AssumeNdimensions" or \
      this_inference_rule=="ReplaceCurlWithLeviCevitaSummationContravariant" or \
      this_inference_rule=="ReplaceSummationNotationWithVectorNotation" or \
      this_inference_rule=="replaceScalarWithVector" or \
      this_inference_rule=="normalizationCondition" or \
      this_inference_rule=="declareFinalEq" or \
      this_inference_rule=="declareAssumption" or \
      this_inference_rule=="declareGuessSolution" or \
      this_inference_rule=="boundaryCondition" ):
    print("skipping "+this_inference_rule+" since it's not checkable")
    counter_array[0]=counter_array[0]+1  
    continue # skip this loop; no CAS check needed
  if (this_inference_rule=="functionIsEven" or \
      this_inference_rule=="functionIsOdd" or \
      this_inference_rule=="conjugateFunctionX" or \
      this_inference_rule=="conjugateBothSides" or \
      this_inference_rule=="conjugateTransposeBothSides" or \
      this_inference_rule=="distributeConjugateTransposeToFactors" or \
      this_inference_rule=="distributeConjugateToFactors" or \
      this_inference_rule=="expandMagnitudeToConjugate" or \
      this_inference_rule=="expandIntegrand" or \
      this_inference_rule=="takeCurlofBothSides" or \
      this_inference_rule=="applyGradientToScalarFunction" or \
      this_inference_rule=="applyDivergence" or \
      this_inference_rule=="indefIntOver" or \
      this_inference_rule=="indefIntegration" or \
      this_inference_rule=="indefIntLHSOver" or \
      this_inference_rule=="indefIntRHSOver" or \
      this_inference_rule=="IntOverFromTo" or \
      this_inference_rule=="EvaluateDefiniteIntegral" or \
      this_inference_rule=="differentiateWRT" or \
      this_inference_rule=="partialDiffWRT" or \
      this_inference_rule=="Xcrossbothsidesby" or \
      this_inference_rule=="bothsidescrossX" or \
      this_inference_rule=="Xdotbothsides" or \
      this_inference_rule=="bothsidesdotX" or \
      this_inference_rule=="solveForX" or \
      this_inference_rule=="factorOutX" or \
      this_inference_rule=="factorOutXfromLHS" or \
      this_inference_rule=="factorOutXfromRHS" or \
      this_inference_rule=="applyOperatorToKet" or \
      this_inference_rule=="applyOperatorToBra" or \
      this_inference_rule=="simplify" or \
      this_inference_rule=="selectRealParts" or \
      this_inference_rule=="selectImagParts" or \
      this_inference_rule=="expandLHS" or \
      this_inference_rule=="expandRHS" or \
      this_inference_rule=="sumExponents" or \
      this_inference_rule=="sumExponentsLHS" or \
      this_inference_rule=="sumExponentsRHS" or \
      this_inference_rule=="subRHSofEqXintoEqY" or \
      this_inference_rule=="subLHSofEqXintoEqY" or \
      this_inference_rule=="EqXisTrueUnderconditionEqY" or \
      this_inference_rule=="declareIdentity" ): 
    counter_array[1]=counter_array[1]+1  
    print("skipping "+this_inference_rule+" since no CAS implemented yet")
    continue # skip this loop; CAS not implemented yet
  print("\ninference rule: "+this_inference_rule)
  
  for inf_rule in inference_rulesDB.getElementsByTagName('inference_rule'):
    inf_rule_name=physgraf.convert_tag_to_content(inf_rule,'infrule_name',0)
    if (inf_rule_name==this_inference_rule):
      inf_rule_sympy=physgraf.convert_tag_to_content(inf_rule,'cas_sympy',0)
      print(inf_rule_sympy)

  symbols_array=[]  

  this_infrule_tunid=physgraf.convert_tag_to_content(this_connection,'infrule_tunid',0)
  outputs_xml=this_connection.getElementsByTagName('output')
  inputs_xml=this_connection.getElementsByTagName('input')
  if len(outputs_xml)>0:
    check_this_connection=True
    [check_this_connection,out_lhs_array,out_rhs_array,symbols_array]=\
        convert_xml_to_cas_array("outputs",outputs_xml,symbols_array,check_this_connection)
  else:
    out_lhs_array=[]
    out_rhs_array=[]

  if len(inputs_xml)>0:
    [check_this_connection,in_lhs_array,in_rhs_array,symbols_array]=\
        convert_xml_to_cas_array("inputs",inputs_xml,symbols_array,check_this_connection)

    [check_this_connection,feed_array,symbols_array]=\
        convert_feed_to_cas_array(inputs_xml,symbols_array,check_this_connection)
  else:
    in_lhs_array=[]
    in_rhs_array=[]
    # there may be a future bug here related to feed

  # if the input, output, and feed CAS exists, then proceed
  if (check_this_connection):
    write_sympy_to_file('tmp_sympy.py',symbols_array,out_lhs_array,out_rhs_array,\
        in_lhs_array,in_rhs_array,feed_array,inf_rule_sympy,this_inference_rule)
    # at this point a valid function exists in a python file; need to run it and get result
    outpt = subprocess.check_output("python tmp_sympy.py", shell=True)
    outpt = outpt.rstrip()
#     print("outpt = "+outpt)
    if(outpt=="True"):
      print("output is True")
      counter_array[2]=counter_array[2]+1
    elif(outpt=="False"):
      print("WARNING: output is NOT True")
      counter_array[3]=counter_array[3]+1
#       exit()
    elif(outpt=="5"):
      print("ERROR: problem found with setup in tmp_sympy!")
      counter_array[4]=counter_array[4]+1
      exit()
    else:
      print("ERROR: you shouldn't get here! Problem in check_connections_using_CAS_sympy")
      exit()
    os.system("rm tmp_sympy.py")
    
  print("number_of_rules_not_checkable="+str(counter_array[0]))
  print("number_of_checkable_rules_not_checked="+str(counter_array[1]))  
  print("number_of_tested_true_connections="+str(counter_array[2]))
  print("number_of_tested_false_connections="+str(counter_array[3]))
  print("number_of_connection_setups_with_error="+str(counter_array[4]))

sys.exit("done")
