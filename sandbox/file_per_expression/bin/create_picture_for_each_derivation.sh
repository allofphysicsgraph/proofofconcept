# Ben Payne <ben.is.located@gmail.com>
# Physics Derivation Graph
# 20160129


# use: bash create_picture_for_each_derivation.sh

find ../derivations -depth 1 -type d | while read this_dir; do
    echo ${this_dir}
#     pwd
    python create_picture_per_derivation.py "${this_dir}"
    cd "${this_dir}"
    neato -Tpng -Nlabel="" graphviz.dot > out.png
    cd ../../bin
done