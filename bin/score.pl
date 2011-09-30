#!/usr/bin/perl -w
#Set Variables
#Project Directory
$PROJECT="/home/boincadm/projects/DrugDiscovery";
#Sample Results Directory
$results=$PROJECT."/sample_results";
#Priority List
$PRIORITY="P*.7z";
#All Priority groups in sample_results directory
@files = </home/boincadm/projects/DrugDiscovery/sample_results/P*.7z>;

#make sure all top scores are back in sample results directory
$move_top_scores="find ".$PROJECT."/top_score_dir -name \"P*.7z\" -exec mv {} ".$PROJECT."/sample_results \\;";
print $move_top_scores ."\n";
system($move_top_scores);

#Loop through the list of Priority results to generate top 100 scores
foreach $file (@files) {

system("date");

#$status="ls sample_results/P*_summary.txt | wc -l | awk '{ print \"Files scored: \" $1}' && ls sample_results/P* | wc -l | awk '{ print \"Total Files: \" $1}'";
$status="ls sample_results/P*_summary.txt | wc -l | awk '{ print \"Files scored: \" \$1}' && ls sample_results/P*.7z | wc -l | awk '{ print \"Total Files: \" \$1}'";
system($status);

#print $status."\n";

#Calculate file size
$filesize = -s $file;
#Error handle: If file size is not greater than 0 bytes, skip this file
  if ($filesize > 0) {
  print $file."\n";
#Extract the workunit name from the file path, removes the .7z file extension from name
  $wu_name=substr($file,0,length($file)-3);
#Remove existing analysis directory for this workunit if its still exists from last run
  $ARG1="rm -rf ".$wu_name;
  system($ARG1);
  print $ARG1."\n";
#Creates a working directory for this workunit
  $ARG2="mkdir ".$wu_name;
  system($ARG2);
  print $ARG2."\n";
#copy the receptor file pdb file to the working directory
  $ARG3="cp ".$PROJECT."/sample_results/receptor.pdb ".$wu_name;
  system($ARG3);
  print $ARG3."\n";
#Extract the result file into working directory
  $ARG4="7za e -o".$wu_name." ".$file;
  print $ARG4."\n";
  system($ARG4);
#summarize the results of the workunit to get the top docking complexes and interaction energy, prints the energy in workunitname_summary.txt
  $ARG5="pythonsh /usr/local/MGLTools-1.5.2/mgltools_i86Linux2_1.5.2/MGLToolsPckgs/AutoDockTools/Utilities24/summarize_results4.py -v -d ".$wu_name." -r receptor.pdb -o ".$wu_name."_summary.txt";
  print $ARG5."\n"; 
  system($ARG5);
#remove the workunit directory don't need it at this moment
  $ARG6="rm -rf ".$wu_name;
  print $ARG6."\n";
  system($ARG6);
	}
}
#write every summary file into summary_1.0.txt
  $ARG7="cat ".$PROJECT."/sample_results/*_summary.txt > ".$PROJECT."/sample_results/summary_1.0.txt";
  print $ARG7."\n";
  system($ARG7);
#remove the redundant lines such as headers from the file
  $ARG8="sed \'\/\#dlgfn                      \#in cluster \#LE   \#rmsd \#ats \#tors/d\' ".$PROJECT."/sample_results/summary_1.0.txt > ".$PROJECT."/sample_results/summary_2.0.txt";
  print $ARG8."\n";
  system($ARG8);
#Sort the file, ascending by LE
  $ARG9="cat ".$PROJECT."/sample_results/summary_2.0.txt | sort -k3n -t, > ".$PROJECT."/sample_results/summary_2.0.sort";
  print $ARG9."\n";
  system($ARG9);
#Remove the remaining summaries
  $ARG10="rm -rf ".$PROJECT."/sample_results/*.txt";
  print $ARG10."\n";
  system($ARG10);
#take the top 100 from summary_2.0.sort and print file summary_3.0.sort
  $ARG11="cat ".$PROJECT."/sample_results/summary_2.0.sort | head -n 103 | tail -n 100 | awk \'{ print substr( \$0, 0, match(\$0, /,/) - 5 ) }\' | sed \-n \'G\; s\/\\n\/\&\&\/\; \/\^\\\(\[ \-\~\]\*\\n\\\).\*\\n\\1\/d\; s\/\\n\/\/\; h\; P\' > " .$PROJECT."/sample_results/summary_3.0.sort && echo EOF >> " .$PROJECT."/sample_results/summary_3.0.sort";
  print $ARG11."\n";
  system($ARG11);

  $ARG12="ls ".$PROJECT."/sample_results/P*.7z | grep -v summary_3.0.sort | xargs rm";
  print $ARG12."\n";
  system($ARG12);

