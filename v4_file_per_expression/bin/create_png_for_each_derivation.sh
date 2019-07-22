# Ben Payne <ben.is.located@gmail.com>
# Physics Derivation Graph
# 20160129


# use: bash create_picture_for_each_derivation.sh

find derivations -depth 1 -type d | while read this_dir; do
    echo ${this_dir}
    python bin/create_png_for_derivation__input_name_of_derivation.py "${this_dir}"
    echo 
done

find identities -depth 1 -type d | while read this_dir; do
    echo ${this_dir}
    python bin/create_png_for_derivation__input_name_of_derivation.py "${this_dir}"
    echo 
done