#!/bin/bash
# Ben Payne <ben.is.located@gmail.com
# run each Python script in bin
this_dir=`pwd`
for filename in `ls bin`
do
  if [ "$filename" == "interactive_user_prompt.py" ]
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

# better: 
# https://stackoverflow.com/questions/285289/exit-codes-in-python
# me@mini:~$ python -c ""; echo $?
# 0
# me@mini:~$ python -c "import sys; sys.exit(0)"; echo $?
# 0
# me@mini:~$ python -c "import sys; sys.exit(43)"; echo $?
# 43
