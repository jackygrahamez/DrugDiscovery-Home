#!/usr/bin/perl -w
#Check if already running

$rcs_target=$ARGV[0];

print $rcs_target."\n";
#@files = </home/boincadm/projects/DrugDiscovery/sample_results/rcs/rcs_*\$rcs_target\*.7z>;
@files = `ls /home/boincadm/projects/DrugDiscovery/sample_results/rcs_*$rcs_target\*.7z`;

#Loop through the list of Priority results to generate top 100 scores
foreach $file (@files) {
print $file."\n";
}
