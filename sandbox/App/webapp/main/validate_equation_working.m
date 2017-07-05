(* this sample mathematica script evaluates
initial: A==B
action:  multiply both sides by 2
result:  2 A == 2 B
*)
labelInitialLHS = A;
labelInitialRHS = B;
labelResultLHS = 2 A;
labelResultRHS = 2 B;
action[y_] := Module[{x=y}, 2 x]
appliedActionLHS = action[labelInitialLHS];
appliedActionRHS = action[labelInitialRHS];
verdict= "Result: operation is ";
Print[verdict,appliedActionLHS == labelResultLHS && appliedActionRHS == labelResultRHS]
