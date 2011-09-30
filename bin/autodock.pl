#!/usr/bin/perl
# Sets the projec directory
my $ARG="";
$PROJECT="/home/boincadm/projects/DrugDiscovery/";
$x=300;
$y=300;
$z=300;

#save the original directory path
my $orig_dir = Cwd::abs_path;
chdir($PROJECT);
$ga=$ARGV[0];
chomp($ga);

$target=$ARGV[1];
chomp($target);
$bt=substr($target, 10);

# Sets the ligand file index of ligands we have
$ligand_index=$ARGV[2];
chomp($ligand_index);
#$ligand_index=$PROJECT.$ligand_index;

$ligand_dir=$ARGV[3];
chomp($ligand_dir);
#$ligand_dir=$PROJECT.$ligand_dir;
#print $ligand_dir."\n";

$target=$PROJECT.$target;

$min_x=`cat $target | grep -v END | tr -s ' ' | cut  -d' ' -f6 | sort -k1n |  sed '/^\$/d' | head -n 1`;
$min_y=`cat $target | grep -v END | tr -s ' ' | cut  -d' ' -f7 | sort -k1n |  sed '/^\$/d' | head -n 1`;
$min_z=`cat $target | grep -v END | tr -s ' ' | cut  -d' ' -f8 | sort -k1n |  sed '/^\$/d' | head -n 1`;
$max_x=`cat $target | grep -v END | tr -s ' ' | cut  -d' ' -f6 | sort -k1nr |  sed '/^\$/d' | head -n 1`;
$max_y=`cat $target | grep -v END | tr -s ' ' | cut  -d' ' -f7 | sort -k1nr |  sed '/^\$/d' | head -n 1`;
$max_z=`cat $target | grep -v END | tr -s ' ' | cut  -d' ' -f8 | sort -k1nr |  sed '/^\$/d' | head -n 1`;
$size_x=$max_x - $min_x;
$size_y=$max_y - $min_y;
$size_z=$max_z - $min_z;

$center_x=($max_x + min_x)/2;
$center_y=($max_y + min_y)/2;
$center_z=($max_z + min_z)/2;

print $size_x.$size_y.$size_z.$center_x.$center_y.$center_z."\n";


# opens the ligand file index
open (LIGAND_FILE,$ligand_index) or die ("Error trying to open the ligand file.\n");
# Skipping all receptors yet processed for this ligand


#Set Variables
#Project Directory
$rsc_fpops_est = ($ga * 1955928030229 * 0.1);
$rsc_fpops_bound = ($rsc_fpops_est * 1000);
$delay_bound = ($rsc_fpops_est * 5);
$weight = $ga * 10;
$batch_time=`date '+%s%N'`;
chomp ($batch_time);

#sleep(10);

# Sets the ligand file index of ligands we have
#$ligand_file_name="/home/boincadm/projects/DrugDiscovery/bin/concord_index.txt";

# opens the ligand file index
open (LIGAND_FILE,$ligand_index) or die ("Error trying to open the ligand file.\n");
# Skipping all receptors yet processed for this ligand

# Reads the substring of the job file takes off the last 4 characters
#$job=substr($job_file, 0, length($job_file)-4);

# prints the output so we can debug
$old_ligand="";

# go through the list of ligands from that ligand index
do {$new_ligand = <LIGAND_FILE>; 
	chomp ($new_ligand);
$df=`df | head -n 3 | tail -n 1 | awk \'{ print substr( \$0, length(\$0) - 4, 2 ) }\'`;
chomp($df);
$df=$df-1;

if ($df >70) {
sleep(3600);
}

  my $range = 1000000;
  my $seed = int(rand($range));
  print $seed . "\n";


# error check to make sure the ligand file has data
if (length($new_ligand) > 1) {

$ARG="cp ".$target." ".$PROJECT."tmp_vps/receptor.pdb";
print $ARG."\n";
system($ARG);
$ARG="cp ".$ligand_dir."/".$new_ligand." ".$PROJECT."tmp_vps/ligand.mol2";
system($ARG);

$job="<job_desc>
    <task>
        <application>vina.exe</application>
        <command_line>--ligand ligand.pdbqt --receptor receptor.pdbqt --cpu 1 --center_x ".$center_x." --center_y ".$center_y." --center_z ".$center_z." --size_x ".$size_x." --size_y ".$size_y. " --size_z ".$size_z." --seed ".$seed." --exhaustiveness 20</command_line>
        <weight>1</weight>
    </task>
</job_desc>";


#print $job ."\n";
$ligand=substr($new_ligand,0,length($new_ligand)-8);

        open (MYFILE, ">>".$PROJECT."/job_".$ga.".xml");
        print MYFILE $job."\n";        close (MYFILE);


$ARG="cp ".$target." ".$PROJECT."tmp_vps/receptor.pdb";
system($ARG);

$ARG="/usr/local/bin/pythonsh /usr/local/MGLTools-1.5.4/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_ligand4.py -l ".$PROJECT."tmp_vps/ligand.mol2 -o ".$PROJECT."tmp_vps/ligand.pdbqt";
print $ARG . "\n";
system($ARG);

$ARG="/usr/local/bin/pythonsh /usr/local/MGLTools-1.5.4/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py -r ".$PROJECT."tmp_vps/receptor.pdb -o ".$PROJECT."tmp_vps/receptor.pdbqt";
print $ARG . "\n";
system($ARG);


# create a time stamp
$time=`date '+%s%N'`;
chomp ($time);

# copy the ligand file from our ligand directory and place in download. Note simply copy and paste wont work
# BOINC requires you place input in a special directory that is specified by dir_hier_path

# Copy the job file
$ARG="mv ".$PROJECT."job_".$ga.".xml \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path job_".$ga."_".$time.".txt\`";
print $ARG . "\n";
system($ARG);

# copy the protein!
$ARG="cp ".$PROJECT."tmp_vps/receptor.pdbqt \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path receptor.pdbqt_".$time.".txt\`";
print $ARG . "\n";
system($ARG);

$ARG="mv ".$PROJECT."tmp_vps/ligand.pdbqt \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path ligand.pdbqt_".$time.".txt\`";
print $ARG . "\n";
system($ARG);
# Now we create the workunit!!!! we give it a name specific to the job file_ligand_timestamp
$ARG=$PROJECT."bin/create_work -appname vina -wu_name autodock_ga_run_".$ga."_bt_".$bt."_lig_".$ligand."_ts_".$time." -wu_template ../templates/vina_wu -result_template ../templates/vina_result --rsc_fpops_est ".$rsc_fpops_est." --rsc_fpops_bound ".$rsc_fpops_bound." --delay_bound ".$delay_bound." job_".$ga."_".$time.".txt receptor.pdbqt_".$time.".txt ligand.pdbqt_".$time.".txt";
print $ARG . "\n";
system($ARG);
sleep(10);

}

    } while ($ligand ne $old_ligand);

close (LIGAND_FILE);

chdir($orig_dir);


  sub report_date {
  $ARG="date";
  print $ARG."\n";
  system($ARG);

  }

  sub run_system 
  {
  my $command;
  system(command);
  if ( $? == -1 )
  {
  print "command failed: $!\n";
  }
  else
  {
  printf $command.": command exited with value %d", $? >> 8;
  }
  }
