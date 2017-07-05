#!/usr/local/bin/perl

# XML parser
# http://www.perlmonks.org/index.pl?node_id=62782

# usage: 
# rm *.svg; perl statement2svg.pl

# requires "dvisvgm" 
# "dvisvgm" is from http://dvisvgm.sourceforge.net/

# sub makeTex
# {
#   texstring =  "\\documentclass{article}\n"
#   texstring += "\\usepackage{amsmath}\n"
#   texstring += "\\usepackage{amssymb}\n"
#   texstring += "\\usepackage{amsfonts}\n"
#   texstring += "\\thispagestyle{empty}\n"
#   texstring += "\\begin{document}\n"
#   texstring += @_
#   texstring += "\n\\end{document}\n"
#   return $texstring
# }

print "Redraw existing equation pictures? ([y]/n): ";
$redrawEqPics = <>;
chomp($redrawEqPics);
if ($redrawEqPics ne "n") { # any response other than "n" is interpreted as "y"
  $redrawEqPics="y";
}
$EqPicsDrawnCount=0;

print "Redraw existing operator pictures? ([y]/n): ";
$redrawOpPics = <>;
chomp($redrawOpPics);
if ($redrawOpPics ne "n") { # any response other than "n" is interpreted as "y"
  $redrawOpPics="y";
}
$OpPicsDrawnCount=0;

# STEP 2
# read equations_database.txt and create svg for each
#open the xml file for reading:
file = open('equations_database.xml','r')
#convert to string:
data = file.read()
#close file because we dont need it anymore:
file.close()
#parse the xml you got from the file
dom = parseString(data)

statement_index

for eqIndx in range(len(dom.getElementsByTagName('statement'))):
    $uid=$line;
    $uid=~s/(^[0-9]+).*/\1/; # search line for a set of numbers and assign that to uid (unique identifier)
    #print "$uid\n";
    $latex=$line;
    $latex=~s/(^[0-9 ]+) \|\| (.*)/\$\2\$/; # search line for what comes after "||" and put that in $$
    #system("echo", "'\$", $latex, "\$'", "-o", $uid, "\b.svg");
    $filename=$uid . '.svg'; # output filename for this line is the UID
    #print "$filename\n";
    #system("./eq2png", "'\$", $latex, "\$'", "-o", $filename);

    #print "$latex\n";
    #print "$filename\n";

    if (($redrawEqPics eq "y") || (($redrawEqPics eq "n") && !(-e 'images_eq_svg/'.$filename))) { # if file does not exist, redraw
      #print "to print: $latex\n";
#      $texstring =  "\\documentclass{article}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{amsfonts}\n\\thispagestyle{empty}\n\\usepackage[active,tightpage]{preview}\n\\PreviewEnvironment{equation*}\n\\begin{document}\n".$latex."\n\\end{document}\n";
      $texstring =  "\\documentclass{article}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{amsfonts}\n\\thispagestyle{empty}\n\\begin{document}\n".$latex."\n\\end{document}\n";
#print "$texstring\n";
      system("/bin/rm tmp*");
      open (TEXFILE, '>>tmp.tex');
      print TEXFILE $texstring;
      close (TEXFILE);
      system("latex tmp"); # convert from .tex to .dvi
      #system("dvisvgm tmp.dvi -o ".$filename); # run dvisvgm to create svg version of the latex equation
      system("python pydvi2svg/dvi2svg.py --paper-size=bbox:10 tmp.dvi");
      system("mv tmp.svg images_eq_svg/".$filename);
      #system("dvips tmp.dvi");
      #system("ps2pdf tmp.ps");
      #system("pdfcrop tmp.pdf tmp.pdf");
      #system("pdf2svg tmp.pdf images_svg/".$filename);
      $EqPicsDrawnCount=$EqPicsDrawnCount+1;
      #exit
    }
  }
}
close(EQFILE);

# STEP 3
# read operators_database.txt and create png for each
open (OPFILE, 'operators_database.txt');
while(<OPFILE>) # read each line from input 
{
  my($line) = $_; # assign input to new variable "line"
  chomp($line); # removes new line character from input 
  $findComment=$line;
  $findComment=~s/^%(.*)/%/; # replace commented lines with "%"
  if ( $findComment eq "%" ) { # this line is a comment, so skip it
    #print "$line\n";
  } else {
    ($operator, $numArgs, $numInputEquations, $numOutputEquations, $comment) = split('\|',$line);
    $operator =~ s/\s+//g;
#    print "operator is $operator.\n";
    $numArgs =~ s/\s+//g;
#    print "numArgs is $numArgs.\n";
    $numInputEquations =~ s/\s+//g;
#    print "numInputEq is $numInputEquations.\n";
    $numOutputEquations =~ s/\s+//g;
#    print "numOutputEq is $numOutputEquations.\n";
    $comment =~ s/^\s+//g;
#    print "comment is $comment.\n";

    $filename=$operator . '.svg'; # output filename for this line is the UID
    #print "$filename\n";
    #system("perl eq2png", "'\$", $latex, "\$'", "-o", $filename);

    if (($redrawOpPics eq "y") || (($redrawOpPics eq "n") && !(-e 'images_op_svg/'.$filename))) { # if file does not exist, redraw
      $texstring =  "\\documentclass{article}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{amsfonts}\n\\thispagestyle{empty}\n\\begin{document}\n".$operator."\n\\end{document}\n";
#print "$texstring\n";
      system("/bin/rm tmp*");
      open (TEXFILE, '>>tmp.tex');
      print TEXFILE $texstring;
      close (TEXFILE);
      system("latex tmp"); # convert from .tex to .dvi
      #system("dvisvgm tmp.dvi -o ".$filename); # run dvisvgm to create svg version of the latex equation
      system("python pydvi2svg/dvi2svg.py --paper-size=bbox:10 tmp.dvi");
      system("mv tmp.svg images_op_svg/".$filename);
      #system("dvips tmp.dvi");
      #system("ps2pdf tmp.ps");
      #system("pdfcrop tmp.pdf tmp.pdf");
      #system("pdf2svg tmp.pdf ".$filename);
      $OpPicsDrawnCount=$OpPicsDrawnCount+1;
    }
  }
}
close(OPFILE);


# STEP 4
# read connections_database.txt to create connections_result.gv
open (CONNECTFILE, 'connections_database.txt'); # read from this
open (MAKEGVFILE, '>connections_result.gv'); # write this
print MAKEGVFILE "#Command to produce output: \n";
print MAKEGVFILE "#neato -Tsvg thisfile > out.svg\n";
print MAKEGVFILE "#http://www.graphviz.org/Gallery/directed/traffic_lights.gv.txt\n";
print MAKEGVFILE "#http://www.graphviz.org/content/traffic_lights\n";
print MAKEGVFILE "digraph physicsEquations {\n";

while(<CONNECTFILE>) # read each line from input 
{
  my($line) = $_; # assign input to new variable "line"
  chomp($line); # removes new line character from input 
  $findComment=$line;
  $findComment=~s/^%(.*)/%/; # replace commented lines with "#"
  if ( $findComment eq "%" ) {
    # this line is a comment, so skip it
    #print "$line\n";
  } else {
    ($inputOneuid, $operator, $outputuid, $optionalInputuid) = split('\|',$line);
    $inputOneuid =~ s/\s+//g;
#     print "$inputOneuid\n";
    $operator =~ s/\s+//g;
#     print "operator is $operator\n";
    $outputuid =~ s/\s+//g;
#     print "$outputuid\n";
    $optionalInputuid =~ s/\s+//g;
#     print "$optionalInputuid\n\n";

    print MAKEGVFILE "$inputOneuid [shape=ellipse,color=red,image=\"images_eq_svg/$inputOneuid.svg\",labelloc=b,URL=\"http://google.com\"];\n";
    print MAKEGVFILE "$operator [shape=invtrapezium,color=red,image=\"images_op_svg/$operator.svg\",labelloc=b,URL=\"http://google.com\"];\n";
    print MAKEGVFILE "$outputuid [shape=ellipse,color=red,image=\"images_eq_svg/$outputuid.svg\",labelloc=b,imagescale=true]; \n";
    if ($optionalInputuid != 0) {
      #print "$optionalInputuid\n";
      print MAKEGVFILE "$optionalInputuid [shape=ellipse,color=red,image=\"images_eq_svg/$optionalInputuid.svg\",labelloc=b,imagescale=true]; \n";
      print MAKEGVFILE "$optionalInputuid -> $operator\n";
    }
    print MAKEGVFILE "$inputOneuid -> $operator\n";
    print MAKEGVFILE "$operator -> $outputuid\n";
  }
}
close(CONNECTFILE);

print MAKEGVFILE "overlap=false\n";
print MAKEGVFILE "label=\"Equation relations\\nExtracted from connections_database.txt and layed out by Graphviz\"\n";
print MAKEGVFILE "fontsize=12;\n";
print MAKEGVFILE "}\n";

close(MAKEGVFILE);

print "$EqPicsDrawnCount equation pictures drawn with pdf2svg\n";
print "$OpPicsDrawnCount operator pictures drawn with pdf2svg\n";

system("neato -Tsvg connections_result.gv > out.svg");

