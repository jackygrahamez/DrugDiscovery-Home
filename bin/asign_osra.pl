#!/usr/bin/perl
# Sets the projec directory
$PROJECT="/home/boincadm/projects/DrugDiscovery/";

# create a time stamp
$time=`date '+%s%N'`;
chomp ($time);

$ARG="touch asgn_input_".$time.".7z";
system($ARG);

$ARG="mv ".$PROJECT."asgn_input_".$time.".7z \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path asgn_input_".$time.".7z\`";
print $ARG ."\n";
system($ARG);
# Now we create the workunit!!!! we give it a name specific to the job file_ligand_timestamp
$ARG=$PROJECT."bin/create_work -appname osra -wu_name asgn_input_".$time.".7z -wu_template /home/boincadm/projects/DrugDiscovery/templates/osra_wu -result_template ../templates/osra_result --assign_team_all 557  asgn_input_".$time.".7z";
print $ARG ."\n";
system($ARG);
