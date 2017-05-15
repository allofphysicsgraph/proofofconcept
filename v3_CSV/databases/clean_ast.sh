grep -P "ast|label" "$1"|
	sed -re 's/\[.*|ctx=|label=|\-\-|<_ast.|object at|ast\.|>//g'


