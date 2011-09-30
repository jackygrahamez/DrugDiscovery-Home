#!/usr/bin/perl
$PROJECT="/home/boincadm/projects/DrugDiscovery/";
$parameters = $ARGV[0];
$input = $ARGV[1];
$gro = $ARGV[2];

chomp($parameters);
chomp($input);
chomp($gro);

$time=`date '+%s%N'`;
chomp ($time);
$new_work=substr($parameters,0,length($parameters)-19);

$ARG="cp ".$PROJECT."/biotarget/".$parameters." `bin/dir_hier_path asgn_job_".$new_work."_".$time.".txt`";
print $ARG . "\n";
system($ARG);

$ARG="cp ".$PROJECT."/biotarget/".$input." `bin/dir_hier_path asgn_".$new_work."_".$time.".txt`";
print $ARG . "\n";
system($ARG);

$ARG="cp ".$PROJECT."/biotarget/".$gro." `bin/dir_hier_path asgn_".$new_work."_".$time."gro.txt`";
print $ARG . "\n";
system($ARG);

$ARG=$PROJECT."bin/create_work -appname mdrun_cuda -wu_name asgn_".$new_work."".$time." -wu_template templates/mdrun_cuda_wu -result_template templates/mdrun_cuda_result --assign_team_all 557 asgn_job_".$new_work."_".$time.".txt asgn_".$new_work."_".$time.".txt asgn_".$new_work."_".$time."gro.txt --assign_team_all 557";
print $ARG . "\n";
system($ARG);

$ARG2="touch ".$PROJECT."reread_db";
print $ARG2 . "\n";
system($ARG2);
sleep(1);

