#!/usr/bin/perl
$PROJECT="/home/boincadm/projects/DrugDiscovery/";
$parameters = $ARGV[0];
$assign = $ARGV[1]." ".$ARGV[2];
chomp($parameters);
chomp($host);

$time=`date '+%s%N'`;
chomp ($time);


$copy="cp ".$parameters." `bin/dir_hier_path ".$parameters."_".$time."`";
print $copy . "\n";
system($copy);


$ARG1=$PROJECT."bin/create_work -appname mdrun -wu_name asgn_".$parameters."_".$time." -wu_template templates/mdrun_wu_test -result_template templates/mdrun_result ".$assign." ".$parameters."_".$time;
print $ARG1 . "\n";
system($ARG1);

$ARG2="touch ".$PROJECT."reread_db";
print $ARG2 . "\n";
system($ARG2);
sleep(1);

