#!/usr/bin/perl
$PROJECT="/home/boincadm/projects/DrugDiscovery/";
#$parameters = $ARGV[0];
#$host = $ARGV[1];
chomp($parameters);
chomp($host);

@files = </home/boincadm/projects/DrugDiscovery/download/*/md_*>;
foreach $file (@files) {

$time=`date '+%s%N'`;
chomp ($time);
$new_work=substr($file,index($file,"md_"),length($file)-index($file,"md_")-20);

print $new_work . "\n";

#$ARG1="cp ".$PROJECT."download/*/".$parameters." `bin/dir_hier_path ".$new_work."".$time."`";
$ARG1="cp ".$file." `bin/dir_hier_path ".$new_work."_".$time."`";
print $ARG1 . "\n";
system($ARG1);

$ARG2=$PROJECT."bin/create_work -appname mdrun_cuda -wu_name cuda_".$new_work."_".$time." -wu_template templates/mdrun_cuda_wu -result_template templates/mdrun_cuda_result ".$new_work."_".$time;
print $ARG2 . "\n";
system($ARG2);

$ARG3="touch ".$PROJECT."reread_db";
print $ARG3 . "\n";
system($ARG3);
sleep(1);

}

