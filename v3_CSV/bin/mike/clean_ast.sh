grep -P "ast|label" "$1"|
	
	sed -re 's/\[.*|ctx=|label=|\-\-|<_ast.|object at|ast\.|>//g'
	
#	tr -d "\n" | 
#	tr ',' '\n'|
#	
#	sed -re 's/\s{2,}/ /g' | 
 #	sed -re 's/Assign/,/g'	


