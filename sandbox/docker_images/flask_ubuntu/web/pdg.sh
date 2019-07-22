
latex lat.tex

dvipng lat.dvi -T tight

2to3 -w pydvi2svg/

python3 pydvi2svg/dvi2svg.py --paper-size=bbox:10 lat.dvi


