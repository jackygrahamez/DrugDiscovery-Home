#!/usr/bin/perl
# Sets the projec directory
$PROJECT="/home/boincadm/projects/DrugDiscovery/";
#$df_command="df | head -n 3 | tail -n 1 | awk \'{ print substr( \$0, length(\$0) - 6, 4 ) }\'";
#print $df_command ."\n";
#$df=system($df_command);

#print $wu_name."\n";
#use the Cwd methods
        use Cwd;
#save the original directory path
        my $orig_dir = Cwd::abs_path;
print "my directory: " . $orig_dir."\n";
chdir($PROJECT);
$ga=$ARGV[0];
chomp($ga);
$ga_step=$ga * 0.1;
$ga_num_evals = 1000000;
#$ga_num_evals = 10; 

$receptor=$ARGV[1];
chomp($receptor);

$receptor_dir=$ARGV[2];
chomp($receptor_dir);

# Sets the ligand file index of ligands we have
$ligand_index=$ARGV[3];
chomp($ligand_index);
#$ligand_index=$PROJECT.$ligand_index;
print $ligand_index."\n";

$ligand_dir=$ARGV[4];
chomp($ligand_dir);
#$ligand_dir=$PROJECT.$ligand_dir;
print $ligand_dir."\n";


#Set Variables
#Project Directory
$rsc_fpops_est = ($ga * 1955928030229 * 0.1);
$rsc_fpops_bound = ($rsc_fpops_est * 1000 * 7);
$delay_bound = ($rsc_fpops_est * 0.0000001);
$weight = $ga * 0.10;
$tmp=$PROJECT."tmp_vps";
$priority=$ARGV[5];

# create a time stamp
$time=`date '+%s%N'`;
chomp ($time);

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
print $new_ligand."\n";
$df=`df | head -n 3 | tail -n 1 | awk \'{ print substr( \$0, length(\$0) - 4, 2 ) }\'`;
chomp($df);
$df=$df-1;
print $df."% full\n";
if ($df >80) {
print "over 80% full \n";
sleep(3600);
}

  my $range = 1000000;
  my $seed_1 = int(rand($range));
  print $seed_1 . "\n";
  my $seed_2 = int(rand($range));
  print $seed_2 . "\n";
  my $seed_3 = int(rand($range));
  print $seed_3 . "\n";
  my $seed_4 = int(rand($range));
  print $seed_4 . "\n";
  my $seed_5 = int(rand($range));
  print $seed_5 . "\n";
  my $seed_6 = int(rand($range));
  print $seed_6 . "\n";
  my $seed_7 = int(rand($range));
  print $seed_7 . "\n";
  my $seed_8 = int(rand($range));
  print $seed_8 . "\n";
  my $seed_9 = int(rand($range));
  print $seed_9 . "\n";
  my $seed_10 = int(rand($range));
  print $seed_10 . "\n";


$job="<job_desc>
    <task>
        <application>unzip.exe</application>
        <command_line> -qq -o \"./*.zip\" -d \".\"</command_line>
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
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py\" -l ligand.pdbqt -r receptor_2.pdbqt -p custom_parameter_file=1 -p parameter_file=AD4_parameters.dat</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_dpf4.py\" -l ligand.pdbqt -r receptor_2.pdbqt -p compute_unbound_extended_flag=0 -p ga_run=".$ga." -p ga_num_evals=".$ga_num_evals." -p seed=".$seed_2."</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>autogrid</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> -p receptor_2.gpf -l out.glg </command_line>
        <weight>1</weight>
    </task>    
    <task>
        <application>autodock</application>        
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> -p ligand_receptor_2.dpf -l out_2.dlg</command_line>
        <weight>".$weight."</weight>
	<fraction_done_filename>progress.txt</fraction_done_filename>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/summarize_docking.py\" -l out_2.dlg -r receptor_2.pdbqt -o summary_2.txt</command_line>
        <weight>1</weight>
    </task>
    <task>        
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py\" -l ligand.pdbqt -r receptor_4.pdbqt -p custom_parameter_file=1 -p parameter_file=AD4_parameters.dat</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/prepare_dpf4.py\" -l ligand.pdbqt -r receptor_4.pdbqt -p compute_unbound_extended_flag=0 -p ga_run=".$ga." -p ga_num_evals=".$ga_num_evals." -p seed=".$seed_4."</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>autogrid</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> -p receptor_4.gpf -l out_4.glg </command_line>
        <weight>1</weight>
    </task>    
    <task>
        <application>autodock</application>        
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> -p ligand_receptor_4.dpf -l out_4.dlg</command_line>
        <weight>".$weight."</weight>
	<fraction_done_filename>progress.txt</fraction_done_filename>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./MGLToolsPckgs/AutoDockTools/Utilities24/summarize_docking.py\" -l out_4.dlg -r receptor_4.pdbqt -o summary_4.txt</command_line>
        <weight>1</weight>
    </task>
    <task>
        <application>./Python25/python.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line>\"./top_summary.py\" summary_2.txt summary_4.txt</command_line> 
        <weight>1</weight>
    </task>
    <task>
        <application>7za.exe</application>
        <stdout_filename>stdout</stdout_filename>
        <stderr_filename>stderr</stderr_filename>
        <command_line> a out.7z *.dlg *.dpf summary_*.txt score.txt job.xml</command_line>
        <weight>1</weight>
    </task>
</job_desc>";


#change to new directory
        chdir($PROJECT);

# error check to make sure the ligand file has data
if (length($new_ligand) > 1) {

$ARG="rm -f ".$PROJECT."job_".$ga.".xml";
print $ARG."\n";
system($ARG);

#print $job ."\n";
$ligand=substr($new_ligand,0,length($new_ligand)-8);
print $new_ligand."\n";
#sleep(10);
        open (MYFILE, ">>".$PROJECT."/job_".$ga.".xml");
        print MYFILE $job."\n";
        close (MYFILE);


chdir($orig_dir);
$ligand=substr($new_ligand,0,length($new_ligand)-5);
print $ligand."\n";

# copy the ligand file from our ligand directory and place in download. Note simply copy and paste wont work
# BOINC requires you place input in a special directory that is specified by dir_hier_path
$ARG="cp ".$PROJECT.$ligand_dir."/".$ligand.".mol2 \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path  ".$ligand."_".$time.".txt\`";
print $ARG ."\n";
system($ARG);

# create a time stamp
$wu_time=`date '+%s%N'`;
chomp ($wu_time);

$ARG="cp ".$PROJECT."bin/top_summary.py \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path top_summary_".$wu_time.".txt\`";
print $ARG ."\n";
system($ARG);
print `/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path top_summary_$wu_time\.txt`."\n";

# Copy the job file
$ARG="mv ".$PROJECT."job_".$ga.".xml \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path job_".$ga."_".$wu_time.".txt\`";
print $ARG ."\n";
system($ARG);
print `/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path job_$ga\_$wu_time\.txt`."\n";

$ARG="cp ".$PROJECT.$receptor_dir."/".$receptor." \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path ".$receptor."_".$wu_time.".zip\`";
print $ARG ."\n";
system($ARG);
print `/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path $receptor\_$wu_time\.zip`."\n";

# Now we create the workunit!!!! we give it a name specific to the job file_ligand_timestamp
$ARG=$PROJECT."bin/create_work -appname autodock_mgl -wu_name rcs_ga_run_".$ga."_bt_".$receptor."_lig_".$ligand."_ts_".$time." -wu_template /home/boincadm/projects/DrugDiscovery/templates/rcs_wu_mgl -result_template ../templates/ad_mgl_result --rsc_fpops_est ".$rsc_fpops_est." --rsc_fpops_bound ".$rsc_fpops_bound." --delay_bound ".$delay_bound." --priority ".$priority." ".$ligand."_".$time.".txt ".$receptor."_".$wu_time.".zip job_".$ga."_".$wu_time.".txt top_summary_".$wu_time.".txt";
print $ARG ."\n";
system($ARG);

sleep(10);

# summary_job4.txt";
# pal_wnt_bind.txt";

	#print $ARG3 . "\n";

	# runs the create project script
	#system($ARG3) == 0
        #or die "system @ARG3 failed: $?";
	#sleep(10);
}

    } while ($ligand ne $old_ligand);

close (LIGAND_FILE);

chdir($orig_dir);





