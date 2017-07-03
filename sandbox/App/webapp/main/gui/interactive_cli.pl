#!/usr/bin/perl
use strict;
use diagnostics;
use warnings;

# http://learn.perl.org/

# Perl Data Structures Cookbook
# http://perldoc.perl.org/perldsc.html

my($rand_size) = 100000;
my($EqFilename)="equations_database.txt";
my($OpFilename)="operators_database.txt";
my($CnFilename)="connections_database.txt";

my($createNewEqDB)="";

my($initial_equation_indx)=0;
my($chosen_operator_indx)=0;
my($resulting_equation_indx)=0;
my($optional_equation_indx)=0;
my($opName)="";

my @operators_database;
my @operator_descriptions;
my @operator_abbreviations;
my @operator_num_input_equations;
my @operator_num_output_equations;

my($findComment)="";
my($operator)="";
# my($numInputEquations)=0;
# my($numOutputEquations)=0;

my($resultingEq)="";
my($initialEq)="";

system("/bin/rm *.png connections_database.txt *.gv");

print "Start new equations database? ([y]/n): ";
$createNewEqDB = <>;
chomp($createNewEqDB);
if ($createNewEqDB ne "n") { # any response other than "n" is interpreted as "y"
  $createNewEqDB="y";
}

if (($createNewEqDB eq "y") || (($createNewEqDB eq "n") && !(-e $EqFilename))) {
  print "creating new Equation DB\n";
  if (unlink($EqFilename) == 0) {
      print "Equations file deleted successfully.\n";
  } else {
      print "Equations file was not deleted.\n";
  }
}

$initial_equation_indx = specify_initial_equation($rand_size);

@operators_database = readOpFile();

for(my $i = 0; $i <= $#operators_database; $i++){
   # $#array_2d gives the highest index from the array
   #print "$operators_database[$i][4] ";
#    for(my $j = 0; $j <= $#operators_database ; $j++){
#       print "$operators_database[$i][$j] ";
#    }
   #print "\n";
   push @operator_abbreviations, $operators_database[$i][0];
   push @operator_num_input_equations, $operators_database[$i][2];
   push @operator_num_output_equations, $operators_database[$i][3];
   push @operator_descriptions, $operators_database[$i][4];
}
# for(my $i=0; $i <= $#operator_abbreviations; $i++){
#   print "$operator_abbreviations[$i]\n";
# }
# for(my $i=0; $i <= $#operator_abbreviations; $i++){
#   print "$operator_descriptions[$i]\n";
# }
# exit;

#@operator_abbreviations=("multEqbyX","replaceLHSXwithLHSY");
#@operator_descriptions=("multiply both sides by X","Replace LHS of Eq X with LHS of Eq Y"); # http://www.tizag.com/perlT/perlarrays.php

$chosen_operator_indx = choose_operator(@operator_descriptions);

$resulting_equation_indx = specify_resulting_operation($rand_size);

$optional_equation_indx = "";

#$opName = @operator_abbreviations[$chosen_operator_indx-1];
$opName = $operator_abbreviations[$chosen_operator_indx-1];

open(CONFILE,'>>'.$CnFilename);
print CONFILE "$initial_equation_indx | $opName | $resulting_equation_indx | $optional_equation_indx\n";
close(CONFILE);

system("perl statement2png.pl");

system("eog out.png");

# end of program

# FUNCTIONS: http://affy.blogspot.com/p5be/ch05.htm
sub specify_resulting_operation {
  print "Specify result of operation: ";
  $resultingEq = <>;
  chomp($resultingEq);
  my $random_index = int(rand()*$_[0]); # http://perlmeme.org/howtos/perlfunc/rand_function.html
  open (EQFILE, '>>'.$EqFilename);
  print EQFILE "$random_index || $resultingEq\n";
  close(EQFILE);
  return($random_index);
}


sub specify_initial_equation {
  print "Specify initial equation: ";
  $initialEq = <>;
  chomp($initialEq);
  # reject empty strings, string which do not have LHS, RHS
  my $random_index = int(rand()*$_[0]); # http://perlmeme.org/howtos/perlfunc/rand_function.html
  open (EQFILE, '>>'.$EqFilename);
  print EQFILE "$random_index || $initialEq\n";
  close(EQFILE);
  return($random_index);
}


sub choose_operator {
  my($i)="";
  my($num)=0;
  my($operator_choice)="";
  my($multiply_by)=0;
  # FROM http://www.unix.com/shell-programming-scripting/134067-perl-how-make-output-command-numbered-list.html

  # print the main menu
  print "Please select from the following available operators\n\n";
  foreach $i (@_) {
    print ++$num,")  $i\n";
  }

  # prompt for user's choice of operator
  printf("\n%s", "Enter selection: ");

  # capture the choice
  $operator_choice = <STDIN>;

  # and finally print it
  print "You entered    : ",$operator_choice;
  #print "So you chose   : ",$operator_descriptions[$operator_choice-1],"\n\n";

  if ($operator_choice == 1) {
    print "Specify value to multiply both sides by: ";
    $multiply_by = <>;
    chomp($multiply_by);
  }
  return($operator_choice);
}

sub readOpFile {
  my @op_list;
  my @newRow;
  my($opIndx)=0;
  my($numArgs)=0;
  my($numInputEquations)=0;
  my($numOutputEquations)=0;
  my($comment)="";
  open (OPFILE, 'operators_database.txt');
  $opIndx=0;
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
#      print "operator is $operator.\n";
      $numArgs =~ s/\s+//g;
#      print "numArgs is $numArgs.\n";
      $numInputEquations =~ s/\s+//g;
#      print "numInputEq is $numInputEquations.\n";
      $numOutputEquations =~ s/\s+//g;
#      print "numOutputEq is $numOutputEquations.\n";
      $comment =~ s/^\s+//g;
#      print "comment is $comment.\n";
      
      push @op_list, ([$operator, $numArgs, $numInputEquations, $numOutputEquations, $comment]); # http://perldoc.perl.org/perllol.html#Growing-Your-Own

      # see also http://perlmeme.org/faqs/perl_thinking/returning.html
    }
  }
  
#   for(my $i = 0; $i <= $#op_list; $i++){
#      # $#array_2d gives the highest index from the array
#      print "$op_list[$i][4] ";
# #      for(my $j = 0; $j <= $#op_list ; $j++){
# #         print "$op_list[$i][$j] ";
# #      }
#      print "\n";
#   }

#   exit;
  return @op_list;
}



