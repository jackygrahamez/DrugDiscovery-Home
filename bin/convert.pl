#!/usr/bin/perl -w

@files = <omega*.pdb>;
foreach $file (@files) {
$filesize = -s $file;
#Error handle: If file size is not greater than 0 bytes, skip this file
  if ($filesize > 0) {
  chomp($file);
  print $file."\n";
  $ligand=substr($file,0, 12);
  print $ligand."\n";

#copy the receptor file pdb file to the working directory
  $ARG3="babel -ipdb ".$ligand.".pdb -omol2 ligand.mol2";
  system($ARG3);
  print $ARG3."\n";

  $ARG4="rm -rf ".$ligand.".pdb";
  print $ARG4."\n";
  system($ARG4);

#Extract the result file into working directory
  $ARG4="7za a ".$ligand.".mol2.7z ligand.mol2";
  print $ARG4."\n";
  system($ARG4);

  $ARG4="rm -rf ligand.mol2";
  print $ARG4."\n";
  system($ARG4);


  #sleep(10);

  }
}

