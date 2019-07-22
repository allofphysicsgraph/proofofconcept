if [ "$#" -ne 1 ]; then
    echo "Usage: $0 NAME_OF_DIRECTORY_IN_DOUBLE_QUOTES" >&2
    exit 1
fi

if [ -d "${1}" ]; then
    cd "${1}"
else
    echo "invalid directory"
    exit 1
fi

if [ -e graphviz.dot ]; then
    echo "now running neato in"
    pwd
    neato -Tpng -Nlabel="" graphviz.dot > out.png
else
    echo " missing graphviz.dot file"
    exit 1
fi

ls -hal graphviz.dot
ls -hal out.png