#!/usr/bin/perl -w

$time=`date '+%s%N'`;
chomp ($time);
$PROJECT="/home/boincadm/projects/DrugDiscovery";
$input="mdrun_".$time.".tpr";
$job="job_".$time.".txt";
$wu_name="mdrun_".$time;

$ARG="cp bin/md.tpr \`bin/dir_hier_path ".$input."\`";
        print $ARG . "\n";
        system($ARG);

$ARG="cp bin/job_mdrun_openmm.xml \`bin/dir_hier_path ".$job."\`";
        print $ARG . "\n";
        system($ARG);


$ARG=$PROJECT."/bin/create_work -appname mdrun -wu_name ".$wu_name." -wu_template ".$PROJECT."/templates/mdrun_wu_cuda_test -result_template templates/mdrun_result ".$input." ".$job;
        print $ARG . "\n";
        system($ARG);



