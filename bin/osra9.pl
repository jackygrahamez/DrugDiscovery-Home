#!/usr/bin/perl
# Sets the projec directory
$PROJECT="/home/boincadm/projects/DrugDiscovery/";

# create a time stamp
$time=`date '+%s%N'`;
chomp ($time);

$index = "/home/boincadm/projects/DrugDiscovery/bin/pid_index.txt";
chomp($index);

open (INDEX_FILE,$index) or die ("Error trying to open the pid index file.\n");

foreach $pid (<INDEX_FILE>) {
	chomp($pid);


#smiles = subprocess.Popen([\"osra.exe\", \"-e\", \"-p\", \"-g\", \"-r 300\", \"patent.pdf\"], stdout=subprocess.PIPE).communicate()[0]


$osra_script = " 
import os
import os.path
import sys
import commands
import subprocess
import urllib2
import time


request = urllib2.Request('http://boinc.drugdiscoveryathome.com/patents/".$pid."%0a.pdf')
request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.13) Gecko/2009073021 Firefox/3.0.13')
opener = urllib2.build_opener() 
page = opener.open(request).read()

localFile = open('patent.pdf', 'wb')
localFile.write(page)
localFile.close()

exec_dir = os.getcwd()
OMP_NUM_THREADS = \"1\"
PATH = exec_dir + \";\bin;\lib;\" + os.getenv(\"PATH\")
MAGICK_CONFIGURE_PATH = exec_dir
os.environ[\"exec_dir\"] = exec_dir
os.environ[\"OMP_NUM_THREADS\"] = OMP_NUM_THREADS
os.environ[\"PATH\"] = PATH
os.environ[\"MAGICK_CONFIGURE_PATH\"] = MAGICK_CONFIGURE_PATH

smiles = subprocess.Popen([\"osra.exe\", sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]], stdout=subprocess.PIPE).communicate()[0]

output = os.getcwd() + \"output.txt\"

if os.path.exists(output):

	file = open(\"output.txt\",\"a\")
	file.write(\"".$pid."\")
	file.write(\"\\n\")
	file.write(smiles)
	file.close()

else:

	file = open(\"output.txt\",\"w\")
        file.write(\"".$pid."\")
	file.write(\"\\n\")
	file.write(smiles)
	file.close()
print output";

open(MYFILE, ">>osra_".$pid.".py");
print MYFILE $osra_script;
close(MYFILE);


$ARG="mv ".$PROJECT."osra_".$pid.".py \`/home/boincadm/projects/DrugDiscovery/bin/dir_hier_path osra_".$pid."_".$time.".py\`";
print $ARG ."\n";
system($ARG);
# Now we create the workunit!!!! we give it a name specific to the job file_ligand_timestamp
$ARG=$PROJECT."bin/create_work -appname osra -wu_name osra_9_".$pid."_".$time." -wu_template /home/boincadm/projects/DrugDiscovery/templates/osra_wu -result_template ../templates/osra_result osra_".$pid."_".$time.".py";
print $ARG ."\n";
system($ARG);
sleep(10);
}
