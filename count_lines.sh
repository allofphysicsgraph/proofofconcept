# delete temp files
find . -name "*.py~" -type f -delete

# for MAC OS X, this works:
find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sort | uniq -c | sort -k1,1
# for CentOS, try
#find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sed '/^\/.*/d' | sed '/.*$/d' | sort | uniq -c | sort -k1,1

count_py_files=`find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sort | uniq -c | grep " py$" | sed 's/\(.*\)py/\1/'`
count_c_files=`find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sort | uniq -c | grep " c$" | sed 's/\(.*\)c/\1/'`
count_csv_files=`find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sort | uniq -c | grep " csv$" | sed 's/\(.*\)csv/\1/'`
count_png_files=`find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sort | uniq -c | grep " png$" | sed 's/\(.*\)png/\1/'`
count_html_files=`find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sort | uniq -c | grep " html$" | sed 's/\(.*\)html/\1/'`
count_sh_file=`find . -type f | sed '/\.\/\./d' | awk -F'.' '{print $NF}' | sort | uniq -c | grep " sh$" | sed 's/\(.*\)sh/\1/'`

echo "{'date':`date +%s`, 'python file count':${count_py_files}, 'c file count':${count_c_files},'csv file count':${count_csv_files}, 'png file count':${count_png_files}, 'html file count':${count_html_files}, 'sh file count':${count_sh_file}}" >> record_of_file_counts.log

# count lines of code
py_line_count=`find . -name "*.py" -type f -exec grep . {} \; | sed -n '/^# /!p' | wc -l`
tex_line_count=`find . -name "*.tex" -type f -exec grep . {} \; | sed -n '/^% /!p' | wc -l`
html_line_count=`find . -name "*.html" -type f -exec grep . {} \; | wc -l`
sh_line_count=`find . -name "*.sh" -type f -exec grep . {} \; | wc -l`


echo "{'date':`date +%s`, 'python line count':${py_line_count}, 'tex line count':${tex_line_count}, 'html line count':${html_line_count}, 'sh line count':${sh_line_count}}" >> record_of_line_counts.log
