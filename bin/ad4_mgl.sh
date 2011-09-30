#!/bin/bash
PROJECT="/home/boincadm/projects/DrugDiscovery/"
#rm ${PROJECT}reread_db
time=`date '+%s'`
#wu=substr("Test1234567890", 10)

cp chemdiv/${1} `bin/dir_hier_path ${1}_${time}`
cp bin/fzd8min_renum_SS.pdb `bin/dir_hier_path fzd8min_renum_SS.pdb_${time}`
cp ${2} `bin/dir_hier_path ${2}_${time}`

echo `bin/dir_hier_path ${1}_${time}`
echo `bin/dir_hier_path fzd8min_renum_SS.pdb_${time}`
echo `bin/dir_hier_path ${2}_${time}`

bin/create_work \
-appname autodock_mgl \
-wu_name asgn_${2}_${1}_${time} \
-wu_template templates/asgn_ad_wu_mgl \
-result_template templates/ad_mgl_result \
$3 $4 \
${1}_${time} \
fzd8min_renum_SS.pdb_${time} \
${2}_${time}
touch ${PROJECT}reread_db

