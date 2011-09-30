#!/usr/bin/perl
$PROJECT="/home/boincadm/projects/DrugDiscovery/";
# $parameters = $ARGV[0];
# $host = $ARGV[1];
chomp($parameters);
chomp($host);

$time=`date '+%s%N'`;
chomp ($time);
# $new_work=substr($parameters,0,length($parameters)-19);

$ARG1="cp ".$PROJECT."bin/alanylalanine_capped_processed.box.em.md.tpr `bin/dir_hier_path alanylalanine_capped_processed.box.em.md.tpr_".$time."`";
print $ARG1 . "\n";
system($ARG1);

$ARG2=$PROJECT."bin/create_work -appname mdrun_cuda -wu_name ala_cuda_".$time." -wu_template templates/mdrun_cuda_wu -result_template templates/mdrun_cuda_result alanylalanine_capped_processed.box.em.md.tpr_".$time;
print $ARG2 . "\n";
system($ARG2);

#$ARG2="touch ".$PROJECT."reread_db";
#print $ARG2 . "\n";
#system($ARG2);
sleep(1);

