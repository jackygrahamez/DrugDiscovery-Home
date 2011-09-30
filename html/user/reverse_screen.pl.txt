#!/usr/bin/perl
# Sets the projec directory

$check = system("ps ax | grep reverse_screen.pl | wc -l");
chomp($check);
print "Checking if script is running\n";
if ($check > 3) {
print "Already running\n";
exit 0;
}

$PROJECT="/home/boincadm/projects/DrugDiscovery/";
$ga=$ARGV[0];
$pdb_index=$ARGV[1];
$lig_index=$ARGV[2];
$lig_dir=$ARGV[3];
$lig_index=$PROJECT.$lig_index;
$pdb_index=$PROJECT.$pdb_index;
chomp($pdb_index);

#Set Variables
#Project Directory
$rsc_fpops_est = ($ga * 1955928030229 * 0.01);
$rsc_fpops_bound = ($rsc_fpops_est * 1000);
$delay_bound = ($rsc_fpops_est * 5);
$weight = $ga * 10;
$old_pdb = "";
$old_lig = "";
$prepare_dir = "/home/boincadm/projects/DrugDiscovery/autodock_prep";


$job="<job_desc>
    <task>
        <application>unzip</application>
        <command_line> -qq -o \"./MGLTools*.zip\" -d \".\"</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>7za.exe</application>
        <command_line> e ligand.mol2.7z</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <command_line>make_sitecustomize.py \".\"</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <command_line>\"./MGLToolsPckgs/Support/sitecustomize.py\"</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_ligand4.py\" -l ligand.mol2 -o ligand.pdbqt</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py\" -U nphs_lps_waters -r receptor.pdb -o receptor.pdbqt</command_line>
        <weight>1</weight>
    </task>
    <task>        
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py\" -l ligand.pdbqt -r receptor.pdbqt -p custom_parameter_file=1 -p parameter_file=AD4_parameters.dat</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_dpf4.py\" -l ligand.pdbqt -r receptor.pdbqt -p compute_unbound_extended_flag=0 -p ga_run=".$ga."</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>autogrid</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> -p receptor.gpf -l out.glg </command_line>
        <weight>1</weight>
    </task>    
    <task>
        <application>autodock</application>        
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> -p ligand_receptor.dpf -l out.dlg</command_line>
        <weight>".$weight."</weight>
        <fraction_done_filename>progress.txt</fraction_done_filename>
    </task>
    <task>
        <application>7za.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> a out.7z out.dlg out.glg receptor.gpf ligand_receptor.dpf job.xml</command_line>
        <weight>1</weight>
    </task>
</job_desc>";


$ARG="rm -rf ".$prepare_dir."/*";
print $ARG."\n";
system($ARG);

#use the Cwd methods
        use Cwd;
#save the original directory path
        my $orig_dir = Cwd::abs_path;

print $pdb_index."\n";

open(LIGAND_FILE,$lig_index) or die ("Error trying to open the ligand index.\n");
do {$new_lig = <LIGAND_FILE>;
	chomp($new_lig);

open (RECEPTOR_FILE,$pdb_index) or die ("Error trying to open the receptor index.\n");
do {$new_pdb = <RECEPTOR_FILE>;
	chomp($new_pdb);
=top
$check = system("ps ax | grep reverse_screen.pl | wc -l");
chomp($check);
print "Checking if script is running\n";
if ($check > 3) {
print "Already running\n";
exit 0;
}
=cut

$df=`df | head -n 3 | tail -n 1 | awk \'{ print substr( \$0, length(\$0) - 4, 2 ) }\'`;
chomp($df);
$df=$df-1;
print $df."% full\n";
if ($df >80) {
print "over 80% full \n";
sleep(5200);
}

$time=`date '+%s%N'`;
chomp ($time);

print $new_pdb."\n";
$ARG="wget --retr-symlinks -P ".$PROJECT."autodock_prep ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/pdb/pdb".$new_pdb.".ent.gz";
print $ARG."\n";
system($ARG);

#clean the path string
        chomp($prepare_dir);
#change to new directory
        chdir($prepare_dir);

$ARG="gunzip pdb".$new_pdb.".ent.gz";
print $ARG."\n";
system($ARG);


$tleap="source /usr/local/amber10/dat/leap/cmd/leaprc.ff99SB
str1=loadpdb pdb".$new_pdb.".ent
savepdb str1 receptor.pdb
quit";
        open (MYFILE, ">>".$prepare_dir."/tleap.in");
        print MYFILE $tleap."\n";        close (MYFILE);

$ARG="egrep -v HETATM pdb".$new_pdb.".ent | egrep -v CONNECT | egrep -v WAT | egrep -v HOH > pdb".$new_pdb.".pdb";
print $ARG."\n";
system($ARG);

sleep(10);

$ARG="tleap -s -f tleap.in > tleap.out";
print $ARG."\n";
system($ARG);

sleep(10);
=top
$ARG="pdb2gmx -ff amber99sb -f pdb".$new_pdb.".pdb -water spce -ignh";
print $ARG."\n";
system($ARG);

$filename = 'conf.gro';
if (-e $filename) {

#Copy the em.mdp parameter file to current working directory
        $ARG15="cp ".$PROJECT."/bin/em.mdp .";
        print $ARG15 . "\n";
        system($ARG15);

#Run editconf on the Complex.pdb
        $ARG15="editconf -bt triclinic -f Complex.pdb -o Complex.pdb -d 1.0";
        print $ARG15 . "\n";
        system($ARG15);

#Run genbox on Complex.pdb
        $ARG16="genbox -cp Complex.pdb -cs ffamber_tip3p.gro -o Complex_b4ion.pdb -p Complex.top";
        print $ARG16 . "\n";
        system($ARG16);

#Run grompp
        $ARG17="grompp -f em.mdp -c Complex_b4ion.pdb -p Complex.top -o Complex_b4ion.tpr";
        print $ARG17 . "\n";
        system($ARG17);

#copy the Complex.top to Complex_ion.top
        $ARG18="cp Complex.top Complex_ion.top";
        print $ARG18 . "\n";
        system($ARG18);

#Run genion
        $ARG19="echo 13| genion -s Complex_b4ion.tpr -o Complex_b4em.pdb -neutral -conc 0.15 -p Complex_ion.top -norandom";
        print $ARG19 . "\n";
        system($ARG19);

#rename the Complex_ion.top Complex.top
        $ARG20="mv Complex_ion.top Complex.top";
        print $ARG20 . "\n";
        system($ARG20);

#Run the grompp
        $ARG21="grompp -f em.mdp -c Complex_b4em.pdb -p Complex.top -o em.tpr";
        print $ARG21 . "\n";
        system($ARG21);

my $timeout = 180;
my $pid = fork;

if ( defined $pid ) {
  if ( $pid ) {
      # this is the parent process
      local $SIG{ALRM} = sub { die "TIMEOUT" };
      alarm 300;
      # wait until child returns or timeout occurs
      eval {
          waitpid( $pid, 0 );
      };
      alarm 0;

      if ( $@ && $@ =~ m/TIMEOUT/ ) {
          # timeout, kill the child process
          kill 9, $pid;
      }
  }
  else {
      # this is the child process
      # this call will never return. Note the use of exec instead of system
      exec "mdrun -v -deffnm em -maxh 0.08";
  }
}
else {
  die "Could not fork.";
}

}
=cut

chdir($orig_dir);


#print $job ."\n";
$ligand=substr($new_ligand,0,length($new_lig)-8);
print $new_ligand."\n";
        open (MYFILE, ">>".$PROJECT."/job_".$ga.".xml");
        print MYFILE $job."\n";        close (MYFILE);

# copy the ligand file from our ligand directory and place in download. Note simply copy and paste wont work
# BOINC requires you place input in a special directory that is specified by dir_hier_path
$ARG="cp ".$lig_dir."/".$new_lig." \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path  ".$new_lig."_".$time.".7z\`";
print $ARG ."\n";
# Use system because other methods of running system commands will not wait until termination.
# For example if you run backtick with these copies, files will not be in the download directory when expected
system($ARG);

# Copy the job file
$ARG="cp ".$PROJECT."job_".$ga.".xml \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path job_".$ga."_".$time."\`";
print $ARG ."\n";
system($ARG);

$ARG="cp ".$prepare_dir."/receptor.pdb  \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path pdb".$new_pdb.".pdb_".$time."\`";
print $ARG."\n";
system($ARG);

$ARG=$PROJECT."bin/create_work -appname autodock_mgl -wu_name rs_ga_run_".$ga."_bt_".$new_pdb."_lig_".$new_lig."_ts_".$time." -wu_template /home/boincadm/projects/DrugDiscovery/templates/ad_wu_mgl -result_template ../templates/ad_mgl_result --rsc_fpops_est ".$rsc_fpops_est." --rsc_fpops_bound ".$rsc_fpops_bound." --delay_bound ".$delay_bound." ".$new_lig."_".$time.".7z pdb".$new_pdb.".pdb_".$time." job_".$ga."_".$time;
print $ARG ."\n";
system($ARG);

sleep(606060606060);

$ARG="rm -rf ".$prepare_dir."/*";
print $ARG."\n";
system($ARG);

} while ($new_pdb ne $old_pdb);

} while ($new_lig ne $new_lig);

