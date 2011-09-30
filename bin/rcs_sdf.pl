#!/usr/bin/perl -w
#Check if already running

$gmx_targets=$ARGV[0];
chomp($gmx_targets);
$rcs_target=$ARGV[1];
chomp($rcs_target);
$lig_grp=$ARGV[2];
chomp($lig_grp);

$ARG="date";
print $ARG."\n";
system($ARG);

$check = system("ps ax | grep rcs_mdrun.pl | wc -l");
chomp($check);
print "Checking if script is running\n";
if ($check > 3) {
print "Already running\n";
exit 0;
}

#Set Variables
#Project Directory
#$steps=50000;
$nsteps = 2500000;
$steps=50000;
$start=0;
$end = $start + $steps;
$nstxout=($steps * 0.10);
$nstvout=($steps * 0.10);
$nstxtcout=($steps * 0.10);
$rsc_fpops_est = ($steps * 319500000);
$rsc_fpops_bound = ($rsc_fpops_est * 1000);
$rsc_memory_bound = 500000000;
$delay_bound = ($steps * 100);
#$delay_bound = ($steps * 70);
$PROJECT="/home/boincadm/projects/DrugDiscovery";
$OPS=$PROJECT."/html/ops";

        $time=`date '+%s%N'`;
        chomp ($time);

$job_file = "
<job_desc>
    <task>
        <application>mdrun.exe</application>
        <command_line> -v -x -c -o -e -cpi md.cpt -cpt 1 -deffnm md</command_line>
        <weight>100</weight>
        <fraction_done_filename>progress.txt</fraction_done_filename>
    </task>
    <task>
        <application>7za.exe</application>
        <weight>1</weight>
        <command_line> a -y -tzip out.7z *.log *.tpr *.gro *.mdp *.edr *.cpt job.xml *.top</command_line>
    </task>
</job_desc>
";

$make_ndx = "0 q ";
$protein_lig = "protein LIG ";
$g_energy = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 ";

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

#remove old assignment files
#$ARG1="find ".$PROJECT."/upload/ -name \"asgn_\*\" -daystart -mtime +1 -exec rm -f \{\} \\;";
#system($ARG1);
#$ARG1="find ".$PROJECT."/download/ -name \"asgn_\*\" -daystart -mtime +1 -exec rm -f \{\} \\;";
#system($ARG1);

#Sample Results Directory
$results=$PROJECT."/sample_results";
$tmp=$results."/".$rcs_target;

$ARG="rm -rf ".$tmp;
print $ARG."\n";
system($ARG);

if (-d $tmp) {
system("rm -rf ".$tmp);
}

$create_tmp="mkdir ".$tmp;
print $create_tmp . "\n";
system($create_tmp);

#Change to cp for asgn
$mv_to_tmp="mv ".$results."/rcs_*".$rcs_target."*ChemDiv_*.7z ".$tmp;
print $mv_to_tmp . "\n";
system($mv_to_tmp);

#All Priority groups in sample_results directory
@files = `ls /home/boincadm/projects/DrugDiscovery/sample_results/$rcs_target\/*rcs_*$rcs_target\*ChemDiv_*.7z`;
sleep(5);
#Loop through the list of Priority results to generate top 100 scores
foreach $file (@files) {
chomp($file);
print $file."\n";
if ($file eq '') {
exit;
}

sleep(1);
$ARG="date";
print $ARG."\n";
system($ARG);

#Check if already running
$check = system("ps ax | grep rcs_mdrun.pl | wc -l");
chomp($check);
print "Checking if script is running\n";
if ($check > 3) {
print "Already running\n";
exit 0;
}
sleep(1);
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
#  $ARG3="cp ".$PROJECT."/bin/receptor.pdb ".$wu_name;
#  system($ARG3);
#  print $ARG3."\n";
#Extract the result file into working directory
  $ARG4="7za e -y -o".$wu_name." ".$file;
  print $ARG4."\n";
  sleep(5);
  system($ARG4);

  $ARG="chmod a+r ".$wu_name."/*";
  print $ARG."\n";
  system($ARG);

  $filename=$wu_name."/score.txt";
  if (-e $filename)  {
  open(SCORE, $filename) || die("Could not open file!");
  $score=<SCORE>;
  close(SCORE);

  chomp($wu_name);
  print $wu_name."\n";
  open (MYFILE, ">>".$wu_name."_score.txt");
  print MYFILE $wu_name.", ".$score."\n";
  close (MYFILE);
  }

  $ARG="rm -rf ".$wu_name;
  print $ARG."\n";
  system($ARG);

  chdir($orig_dir);
	}
}

#use the Cwd methods
	use Cwd;
#save the original directory path
#	my $orig_dir = Cwd::abs_path;
#clean the path string
	chomp($tmp);
#change to new directory
	chdir($tmp);

#write every summary file into summary_1.0.txt
  $ARG="cat ".$tmp."/*_score.txt > ".$tmp."/all_scores.txt";
  print $ARG."\n";
  system($ARG);
#Sort the file, ascending by LE
  $ARG="cat ".$tmp."/all_scores.txt | sort -k2n -t, > ".$tmp."/all_scores.sort";
  print $ARG."\n";
  system($ARG);

  $ARG = "cat all_scores.txt | awk '{ print substr(\$1, 0, match(\$0, \", \") - 1) }' | sed \-n \'G\; s\/\\n\/\&\&\/\; \/\^\\\(\[ \-\~\]\*\\n\\\).\*\\n\\1\/d\; s\/\\n\/\/\; h\; P\' | head -n 100 > ".$tmp."/rank.sort";
  print $ARG."\n";
  system($ARG);

  $ARG = "echo EOF >> ".$tmp."/rank.sort";
  print $ARG."\n";
  system($ARG);

  $ARG = "cp ".$tmp."/all_scores.sort ".$results."/rcs_scores_".$time.".txt";
  print $ARG."\n";
  system($ARG);


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


#Remove the remaining summaries
#  $ARG10="rm -rf ".$tmp."/*.txt";
#  print $ARG10."\n";
#  system($ARG10);

$top_scores=$tmp."/rank.sort";
open (TOP_SCORES,$top_scores) or die ("Error trying to open top scores.\n");
# process top scores

 do {$new_score = <TOP_SCORES>;

print "New Score ".$new_score."\n";
$ARG="date";
print $ARG."\n";
system($ARG);

#generate seed
#  use strict;
#  use warnings;
  my $range = 1000000;
  my $seed = int(rand($range));
  print "Random Number: ".$seed. "\n";

$md_param="integrator \= md
nsteps \= ".$steps."
dt \= 0.002
nstvout \= ".$nstvout."
nstlog \= 500
nstenergy \= 250
nstxtcout \= ".$nstxtcout."
nstxout \= ".$nstxout."
xtc_grps \= Protein  LIG
energygrps \= Protein  SOL  LIG
constraints \= all-bonds
nstcomm \= 1
ns_type \= grid
rlist \= 1.2
rcoulomb \= 1.1
rvdw \= 1.0
vdwtype \= shift
rvdw-switch \= 0.9
coulombtype \= PME-Switch
Tcoupl \= v-rescale
tau_t \= 0.1 0.1
tc-grps \= protein non-protein
ref_t \= 300 300
Pcoupl \= parrinello-rahman
PcOupltype \= isotropic
tau_p \= 0.5
compressibility \= 4.5e-5
ref_p \= 1.0
gen_vel \= yes
lincs-iter \= 2
DispCorr \= EnerPres
optimize_fft \= yes
gen_seed = ".$seed;


$df=`df | head -n 3 | tail -n 1 | awk \'{ print substr( \$0, length(\$0) - 4, 2 ) }\'`;
chomp($df);
$df=$df-1;
print $df."% full\n";
if ($df >70) {
print "over 70% full \n";
sleep(5200);
}

	chomp($new_score);
	print $new_score . "\n"; 
#if not at the end of file
	if ($new_score ne "EOF")
	{
	$time=`date '+%s%N'`;
	chomp ($time);

#create a new score directory
	$ARG1="mkdir ".$new_score;
	system($ARG1);
	print $ARG1."\n";
 	$ARG2="7za e -o".$new_score." ".$new_score.".7z";
        print $ARG2."\n";
 	system($ARG2);

print $wu_name."\n";
#use the Cwd methods
        use Cwd;
#save the original directory path
        my $orig_dir = Cwd::abs_path;
#clean the path string
        chomp($new_score);
#change to new directory
	chdir($new_score);

        $ARG1="chmod -R a+r ".$new_score;
        print $ARG1 . "\n";
        system($ARG1);

#name of workunit extracted again
#  	$wu_name=substr($new_score,57,length($new_score)-3);

$bt=substr($new_score, rindex($new_score,"_bt_")+4, rindex($new_score,"_lig_") - rindex($new_score,"_bt_")-4);
print "bt: ".$bt."\n";
$lig=substr($new_score, rindex($new_score,"_lig_")+5, rindex($new_score,"_ts_") - rindex($new_score,"_lig_")-5);
print "lig: ".$lig."\n";
$ts=substr($new_score, rindex($new_score,"_ts_")+4);
print "ts: ".$ts."\n";
$wu_name="nsteps_".$nsteps."_int_".$start."_-_".$end."_bt_rcs_".$bt."_lig_".$lig."_ts_".$time;

	print "\n".$wu_name."\n";


$ENV{'PATH'} = '/usr/local/gromacs/bin/:/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/antechamber-1.27:/usr/local/antechamber-1.27/exe:/home/boincadm/bin';
$ENV{'ACHOME'} = '/usr/local/antechamber-1.27';
$ENV{'AMBERHOME'} = '/usr/local/antechamber-1.27/exe';
$results=$PROJECT."/sample_results";	


  $ARG="cat ".$new_score."/summary_*.txt > ".$new_score."/all_summary.txt";
  print $ARG."\n";
  system($ARG);

  $ARG="sed \'\/\#dlgfn\/d\' ".$new_score."/all_summary.txt | sort -k3n -t, | head -n 1 > top_score.txt";
  print $ARG."\n";
  system($ARG);

  open(TOP_SCORE, "top_score.txt") || die("Could not open file!");
  $score=<TOP_SCORE>;
  close(TOP_SCORE);

  $top_pdb=substr($score,0,index($score,",")).".pdb";
  $top_dlg=substr($score,0,index($score,",")).".dlg";

  print "Top PDBQT: ".$top_pdb." score index: ".index($score,",")."\n";
  $ARG = "cp ".$PROJECT."/biotarget/".$gmx_targets."/".$top_pdb." .";
  print $ARG."\n";
  system($ARG);

#MGLTools Script writes the largest cluster of ligands into a ligand_BC.pdbqt
	$ARG="/usr/local/bin/pythonsh /usr/local/MGLTools-1.5.4/MGLToolsPckgs/AutoDockTools/Utilities24/write_lowest_energy_ligand.py -f ".$top_dlg;
	print $ARG . "\n";

sleep(5);
	system($ARG);

$file=$new_score."/ligand_BE.pdbqt";
print $file . "\n";
#Calculate file size

$filesize = -s $file;
#Error handle: If file size is not greater than 10 bytes, skip this file
print "\nFilesize: ".$filesize ."\n";

#Convert PDBQT format to PDB
	$ARG2="/usr/local/bin/pythonsh /usr/local/MGLTools-1.5.4/MGLToolsPckgs/AutoDockTools/Utilities24/pdbqt_to_pdb.py -f ligand_BE.pdbqt -o ligand_BE.pdb";        
	print $ARG2 . "\n";        
	system($ARG2);
#Babel adds protons
	$ARG3="babel -ipdb ligand_BE.pdb -opdb ligand_BE.pdb -h";
        system($ARG3);
        print $ARG3 . "\n";
        $ARG3="sed -i \'s\/\<0\>\/LIG\/g\' ligand_BE.pdb";
        system($ARG3);
        print $ARG3 . "\n";
#Output only LIG residues
        $ARG4="grep LIG ligand_BE.pdb > Ligand.pdb";
        system($ARG4);
        print $ARG4 . "\n";

	$filename=$new_score."/Ligand.pdb";


if (-e $filename) {

#Copy the Protein file previously preped with Amber
#        $ARG6="cp ".$PROJECT."/biotarget/".$receptor_gro." .";
#        print $ARG6 . "\n";
#        system($ARG6);

#Extract the ATOM Residues from Protein2.pdb and Ligand_NEW.pdb and redirect to Complex.pdb
        $ARG9="grep -h ATOM ".$top_pdb." Ligand.pdb >| /home/boincadm/rcs_top100_complex/complex_".$top_pdb."_".$lig.".pdb";
        print $ARG9 . "\n";
        system($ARG9);

        $ARG="cp Ligand.pdb ".$lig.".pdb";
        print $ARG . "\n";
        system($ARG);

        $ARG="babel -ipdb ".$lig.".pdb -osdf ".$lig.".sdf";
        print $ARG . "\n";
        system($ARG);

        $ARG="cat ".$lig.".sdf >> ../../rcs_ligands.sdf";
        print $ARG . "\n";
        system($ARG);
	}
	}
    } while ($new_score ne "EOF");
close (TOP_SCORE);

	$ARG="date";
	print $ARG."\n";
	system($ARG);


