#!/bin/bash
# Ben Payne <ben.is.located@gmail.com
# run each Python script in bin
this_dir=`pwd`
for filename in `ls bin`
do
  if [ "$filename" == "prompt_to_user.py" ]
  then
    echo skipping $filename because it requires user interaction
    continue
  fi
  echo starting $filename
  time reslt=$(python bin/${filename} 2>&1 1> /dev/null)
  if [ "$reslt" == "done" ]
  then
    echo $reslt with $filename
  else
    echo ERROR found with $filename
  fi
done