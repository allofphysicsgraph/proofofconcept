# check that omega=2*pi*f
# divided by 2*pi (the "feed" for inference rule: dividebothsidesby)
# results in omega/(2*pi)=f

import sympy
omega = sympy.Symbol('omega') # from outputs
f = sympy.Symbol('f') # from inputs
pi = sympy.pi

# from databases/statements_database.xml
#outputs statement index 3147472131
#outputs lhs: omega/(2*pi)
out_lhs0=omega/(2*pi)
#outputs rhs: f
out_rhs0=f
#inputs statement index 3131211131
#inputs lhs: omega
in_lhs0=omega
#inputs rhs: 2*pi*f
in_rhs0=2*pi*f

# from databases/feed_database.xml
#feed tunid 2940021 is 2*pi
feed0=2*pi

try:
  rule_obeyed = ((out_lhs0 == (in_lhs0/feed0)) and (out_rhs0 == in_rhs0/feed0))
except:
  rule_obeyed = 5 # used to indicate problem
      
if(rule_obeyed==True):
  print(True)
elif(rule_obeyed==False):
  print(False)
else:
  print(5)

