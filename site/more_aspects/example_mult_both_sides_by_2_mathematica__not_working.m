(* 
Read input from plain text file, evaluate validity

Usage: 
perl mash.pl result_to_test_read_from_file.m

Mathematica package for Einstein summation notation
http://www.springerlink.com/content/m5427406037u8043/
See also
http://www.math.washington.edu/~lee/Ricci/Ricci.m
*)
(* input = ReadList["input.dat_multLHSbyUnity"] *)
input = ReadList["input.dat"]
numberOfLines=input[[1]];
actioninput = input[[2]];
initialLHS = input[[3]];
initialRHS = input[[4]];
resultLHS = input[[5]];
resultRHS = input[[6]];
If[numberOfLines >= 7, extraArg1 = input[[7]];]
If[numberOfLines >= 8, extraArg2 = input[[8]];]
If[numberOfLines >= 9, extraArg3 = input[[9]];]

(* initialize check to true *)
check = True;
Switch[actioninput, multBothSidesByX, 
 appliedActionLHS = extraArg1 initialLHS;
 appliedActionRHS = extraArg1 initialRHS;,
 multLHSbyUnity, 
 appliedActionLHS = extraArg1 initialLHS;
 appliedActionRHS = initialRHS;
 check = extraArg1 == 1;,
 multRHSbyUnity, 
 appliedActionLHS = initialLHS;
 appliedActionRHS = extraArg1 initialRHS;
 check = extraArg1 == 1;,
 addZerotoLHS,
 appliedActionLHS = initialLHS + extraArg1;
 appliedActionRHS = initialRHS;
 check = extraArg1 == 0;,
 addZerotoRHS,
 appliedActionLHS = initialLHS;
 appliedActionRHS = initialRHS + extraArg1;
 check = extraArg1 == 0;,
 addXtoBothSides,
 appliedActionLHS = initialLHS + extraArg1;
 appliedActionRHS = initialRHS + extraArg1;,
 selectRealParts,
 appliedActionLHS = Re[initialLHS];
 appliedActionRHS = Re[initialRHS];,
 selectImagParts,
 appliedActionLHS = Im[initialLHS];
 appliedActionRHS = Im[initialRHS];,
 swapLHSwithRHS,
 appliedActionLHS = initialRHS;
 appliedActionRHS = initialLHS;,
 subXforY,
 appliedActionLHS = initialLHS/. extraArg2 -> extraArg1;
 appliedActionRHS = initialRHS/. extraArg2 -> extraArg1;
]

verdict = "Result: intended operation is carryed out correctly: ";
Print[(appliedActionLHS == resultLHS) && (appliedActionRHS == resultRHS) && check];


