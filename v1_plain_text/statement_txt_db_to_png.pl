#!/usr/local/bin/perl

# usage: 
# rm *.png; perl statement2png.pl

# requires perl script "ep2png" to be in this directory
# "ep2png" is from http://www-users.math.umd.edu/~olsson/eq2png/

# STEP 1
# Create associated "eq2png-conf.xml"
open (XMLCONFIGFILE, '>eq2png-conf.xml');
print XMLCONFIGFILE "<eq2png_config>\n";
print XMLCONFIGFILE "  <packages>fullpage</packages>\n";
print XMLCONFIGFILE "  <dvips_scale>1000</dvips_scale>\n";
print XMLCONFIGFILE "  <ps_background_color>\"1,1,1\"</ps_background_color>\n";
print XMLCONFIGFILE "  <ps_foreground_color>\"0,0,0\"</ps_foreground_color>\n";
print XMLCONFIGFILE "</eq2png_config>\n";
close (XMLCONFIGFILE); 
# to verify this works, try
# ./eq2png '$\int$' -o integral.png

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
# read equations_database.txt and create png for each
open (EQFILE, 'equations_database.txt');
while(<EQFILE>) # read each line from input 
{
  my($line) = $_; # assign input to new variable "line"
  chomp($line); # removes new line character from input 
  $findComment=$line;
  $findComment=~s/^%(.*)/%/; # replace commented lines with "%"
  if ( $findComment eq "%" ) { # this line is a comment, so skip it
    #print "$line\n";
  } else {
    $uid=$line;
    $uid=~s/(^[0-9]+).*/\1/; # search line for a set of numbers and assign that to uid (unique identifier)
    #print "$uid\n";
    $latex=$line;
    $latex=~s/(^[0-9 ]+) \|\| (.*)/\$\2\$/; # search line for what comes after "||" and put that in $$
    #system("echo", "'\$", $latex, "\$'", "-o", $uid, "\b.png");
    $filename=$uid . '.png'; # output filename for this line is the UID
    #print "$filename\n";
    #system("./eq2png", "'\$", $latex, "\$'", "-o", $filename);

    #print "$latex\n";
    #print "$filename\n";

    if (($redrawEqPics eq "y") || (($redrawEqPics eq "n") && !(-e 'images_eq_png/'.$filename))) { # if file does not exist, redraw
      system("perl eq2png '".$latex."' -o images_eq_png/".$filename); # run eq2png to create png version of the latex equation
      $EqPicsDrawnCount=$EqPicsDrawnCount+1;
      #system("perl eq2png '$\int x^2 dx$' -o file.png"); # works
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
  $findComment=~s/^%(.*)/%/; # replace commented lines with "#"
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

    $filename=$operator . '.png'; # output filename for this line is the UID
    #print "$filename\n";
    #system("perl eq2png", "'\$", $latex, "\$'", "-o", $filename);

    if (($redrawOpPics eq "y") || (($redrawOpPics eq "n") && !(-e 'images_op_png/'.$filename))) { # if file does not exist, redraw
      system("perl eq2png '".$operator."' -o images_op_png/".$filename); # run eq2png to create png version of the latex equation
      #system("perl eq2png '$\int$' -o file.png"); # works
      $OpPicsDrawnCount=$OpPicsDrawnCount+1;
    }
  }
}
close(OPFILE);



# STEP 4
# read connections_database.txt to create connections_result.gv
open (CONNECTFILE, 'connections_database.txt'); # read from this
open (MAKEGVFILE, '>connections_result.gv'); # write this
print MAKEGVFILE "# Command to produce output: \n";
print MAKEGVFILE "#   neato -Tpng thisfile > out.png\n";
print MAKEGVFILE "# as an example, see\n";
print MAKEGVFILE "# http://www.graphviz.org/Gallery/directed/traffic_lights.gv.txt\n";
print MAKEGVFILE "# which produces\n";
print MAKEGVFILE "# http://www.graphviz.org/content/traffic_lights\n";
print MAKEGVFILE "digraph physicsEquationsGraph {\n";

while(<CONNECTFILE>) # read each line from input 
{
  my($line) = $_; # assign input to new variable "line"
  chomp($line); # removes new line character from input 
  $findComment=$line;
  $findComment=~s/^%(.*)/%/; # replace commented lines with "%"
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

    print MAKEGVFILE "$inputOneuid [shape=ellipse,color=red,image=\"images_eq_png/$inputOneuid.png\",labelloc=b,URL=\"http://google.com\"];\n";
    print MAKEGVFILE "$operator [shape=invtrapezium,color=red,image=\"images_op_png/$operator.png\",labelloc=b,URL=\"http://google.com\"];\n";
    print MAKEGVFILE "$outputuid [shape=ellipse,color=red,image=\"images_eq_png/$outputuid.png\",labelloc=b,imagescale=true]; \n";
    if ($optionalInputuid != 0) {
      #print "$optionalInputuid\n";
      print MAKEGVFILE "$optionalInputuid [shape=ellipse,color=red,image=\"images_eq_png/$optionalInputuid.png\",labelloc=b,imagescale=true]; \n";
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

print "$EqPicsDrawnCount equation pictures drawn with eq2png\n";
print "$OpPicsDrawnCount operator pictures drawn with eq2png\n";

system("neato -Tpng connections_result.gv > out.png");


