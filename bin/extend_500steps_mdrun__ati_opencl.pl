#!/usr/bin/perl -w
# DrugDiscovey@Home Extend Script. Processes the name of workunits
# and parses the numbe of steps (nsteps) step interval int_startend
# extends the simulation by 

#Check if already running
$check = system("ps ax | grep extend.pl | wc -l");
chomp($check);
print "Checking if script is running\n";
if ($check > 3) {
print "Already running\n";
exit 0;
}
#Set Variables
#Project Directory

$PROJECT="/home/boincadm/projects/DrugDiscovery";
$OPS=$PROJECT."/html/ops";
$make_ndx = "0 q ";
$protein_lig = "protein LIG ";
$g_energy = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 ";

#$ARG="cp ".$PROJECT."/sample_results/nsteps*.7z /home/boincadm/projects/DrugDiscovery/html/ops/complexes/";
#print $ARG."\n";
#system($ARG);

#step dependent variables
$steps = 500;
$extend = $steps * 0.002;
$nsteps = 5000;
#$start = 500;
#$end = $start + $steps;
$rsc_fpops_est = ($steps * 319500000);
$rsc_fpops_bound = ($rsc_fpops_est * 1000);
$rsc_memory_bound = 500000000;
$delay_bound = ($steps * 10);

#use the Cwd methods
        use Cwd;
#save the original directory path
        my $orig_dir = Cwd::abs_path;
#clean the path string
        chomp($OPS);
#change to new directory
        chdir($OPS);


#change to original
        chdir($orig_dir);

#Sample Results Directory
$results=$PROJECT."/sample_results";

$ARG="cp ".$results."/nsteps*.7z ".$PROJECT."/backup";
print $ARG."\n";
system($ARG);

#working directory for extension script
$tmp=$results."/ext";
if (-d $tmp) {
system("rm -rf ".$tmp);
}

#creating a temporary working directory under samples
$create_tmp="mkdir ".$tmp;
print $create_tmp . "\n";
system($create_tmp);

$mv_to_tmp="mv ".$results."/nsteps_2500000_int_*.7z ".$tmp;
#$mv_to_tmp="mv ".$results."/nsteps_2500000_int_0*.7z ".$tmp;
print $mv_to_tmp . "\n";
system($mv_to_tmp);

#An array of all file times for analysis
@files = </home/boincadm/projects/DrugDiscovery/sample_results/ext/nsteps*.7z>;
#@files = </home/boincadm/projects/DrugDiscovery/sample_results/ext/nsteps_2500000_int_0*.7z>;
my %seen = ();
foreach $file (@files) {
#clean the complexes directory
	unless ($seen{$file}) {
		push @files, $file;
		$seen{$file} = 1;
		print $file."\n";
	}
}


#Loop through the list of Priority results to generate top 100 scores
foreach $file (@files) {

chomp($file);
print "filename: ".$file."\n";
$time=`date '+%s%N'`;
chomp($time);

#Check if already running
$check = system("ps ax | grep extend.pl | wc -l");
chomp($check);
print "Checking if script is running\n";
if ($check > 3) {
print "Already running\n";
exit 0;
}

$filesize = "";
#Calculate file size


  $nsteps=substr($file, rindex($file, "nsteps_")+7, rindex($file, "_int_")-rindex($file, "nsteps_")-7)."\n";
  chomp($nsteps);
  print "total steps: ".$nsteps."\n";
#Error handle: If file size is not greater than 0 bytes, skip this file
#print "File Size: ".$filesize."\n";
#$start=substr($file, rindex($file, "int_"), rindex($file, "_-_") - rindex($file, "int_"));
  

  $start=substr($file, rindex($file, "_int_")+5, rindex($file, "_-_") - rindex($file, "_int_") - 5);

  print "Start: ".$start."\n";

  $end=substr($file, rindex($file, "_-_")+3, rindex($file, "_bt_") - rindex($file, "_-_") - 3); 
  #$end = $start + $steps;
  print "End: ".$end."\n";
  #$steps = $end - $start;
  $rsc_fpops_est = ($steps * 319500000);
  $rsc_fpops_bound = ($rsc_fpops_est * 10);
  print "Steps: ".$steps."\n";
  print $steps." * 0.002\n";
  $extend = ($steps) * 0.002;
  print "Extend ps: ".$extend."\n";
  $half_extend = $extend * 0.5;
  $nstart = $start + $steps;
  $nend = $end + $steps;

  $rsc_fpops_est = ($steps * 319500000);
  $rsc_fpops_bound = ($rsc_fpops_est * 100);
  $rsc_memory_bound = 500000000;
  $delay_bound = ($steps * 10);
  print "$nend >= $nsteps\n";

#sleep(30);

  if ($nend >= $nsteps) {
	$ARG="cp ".$file." ".$results;
	print $ARG."\n";
	system($ARG);
   }

  if ($nend <= $nsteps) {

$df=`df | head -n 3 | tail -n 1 | awk \'{ print substr( \$0, length(\$0) - 4, 2 ) }\'`;
chomp($df);
$df=$df-1;
print $df."% full\n";
if ($df >80) {
print "over 70% full \n";
sleep(5200);
}

  print "File match\n";
#Extract the workunit name from the file path, removes the .7z file extension from name

  $wu_name=substr($file,0,length($file)-3);
#Remove existing analysis directory for this workunit if its still exists from last run
  print $wu_name."\n";

  chomp($wu_name);
#Name
#$ga_run=substr($file, rindex($file,"_#ga_run_")+8, rindex($file,"_bt_") - rindex($file,"_ga_run_")-8);
#print "ga_run: ".$ga_run."\n";
$bt=substr($file, rindex($file,"_bt_")+4, rindex($file,"_lig_") - rindex($file,"_bt_")-4);
print "bt: ".$bt."\n";
$lig=substr($file, rindex($file,"_lig_")+5, rindex($file,"_ts_") - rindex($file,"_lig_")-5);
print "lig: ".$lig."\n";
$ts=substr($file, rindex($file,"_ts_")+4, 19);
print "ts: ".$ts."\n";
$name="_bt_".$bt."_lig_".$lig."_ts_".$time;

  #$name=substr($wu_name, rindex($wu_name, "ext/")+4, length($wu_name) - 97);
  print $name."\n";
  $length=length($wu_name);
  print $length."\n";

#sleep(10);

  $ARG1="rm -rf ".$wu_name;
  system($ARG1);
  print $ARG1."\n";

#Creates a working directory for this workunit
  $ARG2="mkdir ".$wu_name;
  system($ARG2);
  print $ARG2."\n";


#Extract the result file into working directory
  $ARG4="7za x -r -y -o".$wu_name." ".$file;
  print $ARG4."\n";
  system($ARG4);

#  $ARG4="7za x -o".$wu_name." ".$wu_name."/Ligand.acpypi.7z";
#  print $ARG4."\n";
#  system($ARG4);

#exit;

#use the Cwd methods
        use Cwd;
#save the original directory path
        my $orig_dir = Cwd::abs_path;
#clean the path string
        chomp($wu_name);
#change to new directory
        chdir($wu_name);

$ENV{'PATH'} = '/usr/local/gromacs/bin/:/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/antechamber-1.27:/usr/local/antechamber-1.27/exe:/home/boincadm/bin';
$ENV{'ACHOME'} = '/usr/local/antechamber-1.27';
$ENV{'AMBERHOME'} = '/usr/local/antechamber-1.27/exe';

$ARG="cp *.tpr md.tpr";
print $ARG."\n";
system($ARG);

$filesize = -s "md.tpr";

if ($filesize > 10)
{

$ARG="cp md*.gro md.gro";
print $ARG."\n";
system($ARG);

$filesize = -s "md.gro";

if ($filesize > 10)
{

$ARG="cp *.xtc md.xtc";
print $ARG."\n";
system($ARG);

$filesize = -s "md.xtc";

if ($filesize > 10)
{

#settup edr
  $ARG4="cp *.edr md.edr";
  print $ARG4."\n";
  system($ARG4);

#Set permissions on this directory
  $ARG5="chmod a+rxw md.tpr job.xml";
  print $ARG5."\n";
  system($ARG5);

#sleep(5);

$job_file = "
<job_desc>
    <task>
        <application>mdrun.exe</application>
        <command_line> -v -x -c -o -e -cpi md.cpt -cpt 1 -deffnm md</command_line>
        <fraction_done_filename>progress.txt</fraction_done_filename>
        <weight>99</weight>
    </task>
    <task>
        <application>7za.exe</application>
        <weight>1</weight>
        <command_line> a -y -tzip out.7z *.log *.tpr *.gro *.mdp *.edr *.cpt job.xml *.xtc </command_line>
    </task>
</job_desc>
";

open (MYFILE, ">>".$wu_name."/make_ndx.txt");
print MYFILE $make_ndx."\n";
close (MYFILE);

open (MYFILE, ">>".$wu_name."/protein_lig.txt");
print MYFILE $protein_lig."\n";
close (MYFILE);

open (MYFILE, ">>".$wu_name."/new_job.xml");
print MYFILE $job_file."\n";
close (MYFILE);

$ARG1="make_ndx -f md.tpr \< make_ndx.txt";
  print $ARG1."\n";
  system($ARG1);

$ARG1="g_dist -f md.gro -s md.tpr -n index.ndx \< protein_lig.txt";
  print $ARG1."\n";
  system($ARG1);

#sleep(10);

#$ARG1=$PROJECT."/bin/check_drift.bash dist.xvg";
#  print $ARG1."\n";
#  $check = system($ARG1);
#  $check = `/home/boincadm/projects/DrugDiscovery/bin/check_drift.bash dist.xvg`;
#  chomp($check);
#  print "check returned: ".$check."\n";
#sleep(5);

open(FILE, "dist.xvg") or die;
$char="";
$pos = -2;  # Use this to get past EOF and last newline
$drift = 0.5;

while($char ne "\n")
{
     seek FILE, $pos, 2;
     read FILE, $char, 1;
     $pos--;
}
$check = 1;
$final = <FILE> ;
my @values = split(' ',$final);
print "drift ".$values[1]."\n";

#if ($values[1] < 0.5) {

#use the Cwd methods
        use Cwd;
#save the original directory path
        my $orig_dir = Cwd::abs_path;
#clean the path string
        chomp($OPS);
#change to new directory
        chdir($OPS);

$complete = 0;
if ($nend >= $nsteps) {
$complete = 1;
}

$ARG="php update_progress.php ".$check." ".$name." ".$bt." ".$lig." ".$ts." ".$end." ".$nsteps." ".$complete." ".$values[0]." ".$values[1]." ".$values[2]." ".$values[3]." ".$values[4];
print $ARG."\n";
system($ARG);

#change to original
        chdir($orig_dir);

if ($check == 1) {
#Prep file for extension
#  $ARG6="mv next.cpt md.cpt";
#  print $ARG6."\n";
#  system($ARG6);

# $ARG6="mv md.next.cpt md.cpt";
#  print $ARG6."\n";
#  system($ARG6);

  $ARG5="tpbconv -s md.tpr -extend ".$extend." -o next.tpr";
  print $ARG5."\n";
  system($ARG5);

$date_time = `date`;
$ARG="echo \"Drift Test Passed ".$date_time."nsteps_".$nsteps."_int_".$nstart."_-_".$nend.$name."\" >> ".$PROJECT."/html/ops/complexes/mdrun_progress.txt";
print $ARG."\n";
system($ARG);

$ARG="tail -n 1 dist.xvg >> ".$PROJECT."/html/ops/complexes/mdrun_progress.txt";
print $ARG."\n";
system($ARG);

  chdir($PROJECT);

#copy the md.tpr used by mdrun workunit. Copy to the download directory using the dir_hier_path which sets the proper fanout directory
  $ARG1="cp ".$wu_name."/next.tpr \`bin/dir_hier_path nsteps_".$nsteps."_int_".$nstart."_-_".$nend.$name.".tpr\`";
  print $ARG1 . "\n";
  system($ARG1);

  $ARG1="cp ".$wu_name."/new_job.xml \`bin/dir_hier_path job_".$nsteps."_int_".$nstart."_-_".$nend.$name.".txt\`";
  print $ARG1 . "\n";
  system($ARG1);

  $ARG1="cp ".$wu_name."/md.cpt \`bin/dir_hier_path next_".$nsteps."_int_".$nstart."_-_".$nend.$name.".cpt\`";
  print $ARG1 . "\n";
  system($ARG1);


$ARG1=$PROJECT."/bin/create_work -appname mdrun__ati_opencl -wu_name nsteps_".$nsteps."_int_".$nstart."_-_".$nend.$name." -wu_template ".$PROJECT."/templates/mdrun_wu_extend -result_template templates/mdrun_result --rsc_fpops_est ".$rsc_fpops_est." --rsc_fpops_bound ".$rsc_fpops_bound." --delay_bound ".$delay_bound." nsteps_".$nsteps."_int_".$nstart."_-_".$nend.$name.".tpr job_".$nsteps."_int_".$nstart."_-_".$nend.$name.".txt next_".$nsteps."_int_".$nstart."_-_".$nend.$name.".cpt";
  print $ARG1 . "\n";
  system($ARG1);
exit;

#$ARG="7za a -r /home/boincadm/projects/DrugDiscovery/html/ops/complexes/nsteps_".$nsteps."_int_".$nstart."_-_".$nend.$name."_ts_".$time.".7z ".$wu_name;
#print $ARG."\n";
#system($ARG);

#sleep(10);

#end check for drift condition if
#}

#else 
#{
#$date_time = `date`;
#$ARG="echo \"Drift Test Failed ".$date_time."nsteps_".$nsteps."_int_".$nstart."_-_".$nend.$name."_ts_".$time."\" >> ".$PROJECT."/html/ops/complexes/mdrun_progress.txt";
#print $ARG."\n";
#system($ARG);

#$ARG="tail -n 1 dist.xvg >> ".$PROJECT."/html/ops/complexes/mdrun_progress.txt";
#print $ARG."\n";
#system($ARG);

#}

}

}
}
}
#end filesize check

$ARG="rm -rf ".$wu_name;
print $ARG."\n";
system($ARG);

#end check for file size and naming convention if
}


#change to original
        chdir($orig_dir);
#sleep(5);

$ARG="rm ".$file;
print $ARG."\n";
system($ARG);

#end foreach file loop
}


$ARG="mv ".$tmp."/*.7z ".$PROJECT."/backup";
print $ARG."\n";
system($ARG);

$ARG="rm -rf ".$tmp;
print $ARG."\n";
system($ARG);
	
