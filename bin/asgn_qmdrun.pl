#!/usr/bin/perl -w
#Check if already running

$complexes=$ARGV[0];
chomp($complexes);

$protein=$ARGV[1];
chomp($protein);

$ARG="date";
print $ARG."\n";
system($ARG);

$check = system("ps ax | grep asgn_qmdrun.pl | wc -l");
chomp($check);
print "Checking if script is running\n";
if ($check > 3) {
print "Already running\n";
exit 0;
}

#Set Variables
#Project Directory
#$steps=50000;
$steps=5000;
$nsteps = 2500000;
#$steps=500;
$start=0;
$end = $start + $steps;
$nstxout=($steps * 0.10);
$nstvout=($steps * 0.10);
$nstxtcout=($steps * 0.10);
$rsc_fpops_est = ($steps * 319500000);
$rsc_fpops_bound = ($rsc_fpops_est * 1000);
$rsc_memory_bound = 500000000;
$delay_bound = ($steps * 7);
#$delay_bound = ($steps * 70);
$PROJECT="/home/boincadm/projects/DrugDiscovery";
$OPS=$PROJECT."/html/ops";
$qmdrun=$PROJECT."/qmdrun";
$biotarget=$PROJECT."/biotarget";
$complexes_index=$biotarget."/".$complexes;

        $time=`date '+%s%N'`;
        chomp ($time);

$job_file = "
<job_desc>
    <task>
        <application>mdrun.exe</application>
        <command_line> -v -x -c md.pdb -o -e -cpi md.cpt -cpt 1 -deffnm md</command_line>
        <weight>100</weight>
	<checkpoint_filename>state.cpt</checkpoint_filename>
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

open (COMPLEXES,$complexes_index) or die ("Error trying to open complexes.\n");

 do {$new_complex = <COMPLEXES>;
chomp($new_complex);

$wu_name=$new_complex."_qmdrun_".$time;

#use the Cwd methods
        use Cwd;
#save the original directory path
        my $orig_dir = Cwd::abs_path;
#clean the path string
        chomp($qmdrun);
#change to new directory
        chdir($qmdrun);




$ARG="date";
print $ARG."\n";
system($ARG);

#generate seed
#  use strict;
#  use warnings;
  my $range = 1000000;
  my $seed = int(rand($range));
  print $seed . "\n";

$md_param="integrator \= md
nsteps \= ".$steps."
dt \= 0.002
nstvout \= ".$nstvout."
nstlog \= 500
nstenergy \= 250
nstxtcout \= ".$nstxtcout."
nstxout \= ".$nstxout."
xtc_grps \= Protein
energygrps \= Protein  SOL
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

$ENV{'PATH'} = '/usr/local/gromacs/bin/:/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/antechamber-1.27:/usr/local/antechamber-1.27/exe:/home/boincadm/bin';
$ENV{'ACHOME'} = '/usr/local/antechamber-1.27';
$ENV{'AMBERHOME'} = '/usr/local/antechamber-1.27/exe';
$results=$PROJECT."/sample_results";

$ARG="rm -rf ".$qmdrun."/*";
print $ARG . "\n";
system($ARG);

$ARG="cp ".$biotarget."/".$protein." Protein.pdb";
print $ARG . "\n";
system($ARG);

$ARG="cp ".$biotarget."/".$new_complex." . ";
print $ARG . "\n";
system($ARG);

$ARG="grep -h LIG ".$new_complex." > Ligand.pdb";
print $ARG . "\n";
system($ARG);

#Acpypi preps the Ligand file for GROMACS
        $ARG="/usr/local/bin/acpypi -f -d -n 0 -i Ligand.pdb -s 120";
        print $ARG . "\n";
	system($ARG);

	$filename=$qmdrun."/Ligand.acpypi/Ligand_GMX.itp";
print $filename."\n";
if (-e $filename) {

#Copy the Ligand_GMX.itp to Ligand.itp
        $ARG="cp Ligand.acpypi/Ligand_GMX.itp Ligand.itp";
        print $ARG . "\n";
        system($ARG);

#Prep the Protein2.pb useing pdb2gmx
$ARG="pdb2gmx -ff amber99sb -f Protein.pdb -o Protein2.pdb -p Protein.top -water spce -ignh";
        print $ARG . "\n";
        system($ARG);

#Extract the ATOM Residues from Protein2.pdb and Ligand_NEW.pdb and redirect to Complex.pdb
        $ARG="grep -h ATOM Protein2.pdb Ligand.acpypi/Ligand_NEW.pdb >| Complex.pdb";
        print $ARG . "\n";
        system($ARG);

#Copy the Protein topology file to Complex.top
        $ARG="cp Protein.top Complex.top";
        print $ARG . "\n";
        system($ARG);

#Copy the Complex.top and insert #include "Ligand.itp" into new file Complex2.top
        $ARG="sed -i '/#include\ \\\"ffamber99sb.itp\\\"/a \#include \"Ligand.itp\"' Complex.top";
        print $ARG . "\n";
        system($ARG);

#Append Ligand   1 to Complex2.top
        $ARG="echo \"Ligand   1\" >> Complex.top";
        print $ARG . "\n";
        system($ARG);

#Copy the em.mdp parameter file to current working directory
        $ARG="cp ".$PROJECT."/bin/em.mdp .";
        print $ARG . "\n";
        system($ARG);

        $ARG="cp ".$PROJECT."/bin/em_r.mdp .";
        print $ARG . "\n";
        system($ARG);

        $ARG="cp ".$PROJECT."/bin/pr.mdp .";
        print $ARG . "\n";
        system($ARG);

#Run editconf on the Complex.pdb
        $ARG15="editconf -bt triclinic -f Complex.pdb -o Complex.pdb -d 1.0";
        print $ARG15 . "\n";
        system($ARG15);

#Run genbox on Complex.pdb
        $ARG16="genbox -cp Complex.pdb -cs ffamber_tip3p.gro -o Complex_b4ion.pdb -p Complex.top";
        print $ARG16 . "\n";
        system($ARG16);

#Run grompp
        $ARG17="grompp -f em_r.mdp -c Complex_b4ion.pdb -p Complex.top -o Complex_b4ion.tpr";
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

sleep(1);

#rename the Complex_ion.top Complex.top
        $ARG20="mv Complex_ion.top Complex.top";
        print $ARG20 . "\n";
        system($ARG20);
#Run the grompp
        $ARG21="grompp -f em_r.mdp -c Complex_b4em.pdb -p Complex.top -o em_r.tpr";
        print $ARG21 . "\n";
        system($ARG21);

my $timeout = 180;
my $pid = fork;

if ( defined $pid ) {
  if ( $pid ) {
      # this is the parent process
      local $SIG{ALRM} = sub { die "TIMEOUT" };
      alarm 3600;
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
      exec "mdrun -v -deffnm em_r -maxh 1";
  }
}
else {
  die "Could not fork.";
}

        $ARG21="grompp -f em.mdp -c em_r.gro -p Complex.top -o em.tpr";
        print $ARG21 . "\n";
        system($ARG21);

my $pid = fork;

if ( defined $pid ) {
  if ( $pid ) {
      # this is the parent process
      local $SIG{ALRM} = sub { die "TIMEOUT" };
      alarm 36000;
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
      exec "mdrun -v -deffnm em -maxh 1";
  }
}
else {
  die "Could not fork.";
}

        $ARG21="grompp -f pr.mdp -c em.gro -p Complex.top -o pr.tpr";
        print $ARG21 . "\n";
        system($ARG21);

my $pid = fork;

if ( defined $pid ) {
  if ( $pid ) {
      # this is the parent process
      local $SIG{ALRM} = sub { die "TIMEOUT" };
      alarm 3600;
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
      exec "mdrun -v -s pr.tpr -o pr.trr -c b4md.gro -g pr.log -e pr.edr";
  }
}
else {
  die "Could not fork.";
}

	open (MYFILE, ">>".$qmdrun."/md.mdp");
	print MYFILE $md_param."\n";
	close (MYFILE);

        $ARG21="grompp -f md.mdp -c b4md.gro -p Complex.top -o md.tpr";
        print $ARG21 . "\n";
        system($ARG21);

        open (MYFILE, ">>".$qmdrun."/md_job.xml");
        print MYFILE $job_file."\n";
        close (MYFILE);

	chdir($PROJECT);

#copy the md.tpr used by mdrun workunit. Copy to the download directory using the dir_hier_path which sets the proper fanout directory
        $ARG1="cp ".$qmdrun."/md.tpr \`bin/dir_hier_path asgn_md_".$wu_name.".tpr\`";
        print $ARG1 . "\n";
        system($ARG1);

        $ARG1="cp ".$qmdrun."/md.mdp \`bin/dir_hier_path asgn_md_".$wu_name.".mdp\`";
        print $ARG1 . "\n";
        system($ARG1);

        $ARG1="cp ".$qmdrun."/md_job.xml \`bin/dir_hier_path asgn_md_job_".$wu_name.".txt\`";
        print $ARG1 . "\n";
        system($ARG1);

        $ARG1="cp ".$qmdrun."/Complex.top \`bin/dir_hier_path asgn_complex".$wu_name.".txt\`";
        print $ARG1 . "\n";
        system($ARG1);

        $ARG1="chmod -R a+r ".$PROJECT."/download";
        print $ARG1 . "\n";
        system($ARG1);


$ARG2=$PROJECT."/bin/create_work -appname mdrun_beta -wu_name asgn_".$wu_name." -wu_template ".$PROJECT."/templates/mdrun_wu -result_template templates/mdrun_result --rsc_fpops_est ".$rsc_fpops_est." --rsc_fpops_bound ".$rsc_fpops_bound." --delay_bound ".$delay_bound." --assign_team_all 557 asgn_md_".$wu_name.".tpr asgn_md_".$wu_name.".mdp asgn_md_job_".$wu_name.".txt asgn_complex".$wu_name.".txt";
        

        print $ARG2 . "\n";
        system($ARG2);
	system("touch ".$PROJECT."/reread_db");

}

} while ($new_complex ne "EOF");
close (COMPLEXES);


