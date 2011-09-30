<?php

require_once("../inc/util.inc");
require_once("../inc/user.inc");
require_once("../inc/db.inc");
require_once("../inc/forum.inc");
require_once("../inc/result.inc");


// show the home page of whoever's logged in

db_init();
$user = get_logged_in_user();
$user_id = '<a href="'.$ub.'show_user.php?userid='.$user->id.'">'.$user->name.'</a>';
$send = 0;

//echo "<pre>test $user_id $user->id</pre>";
$deadline = 86400;
$query = "select create_time from workunit where id = (select max(id) from workunit)";
$result = mysql_query($query);
$timestamp = mysql_result($result,0);
$c_time = time();
$lig_type = trim(strtolower($_GET["lig"]));
$rec = trim(strtolower($_GET["pdb2"]));
$mol1 = trim(strtolower($_GET["mol1"]));
$pdb1 = trim(strtolower($_GET["pdb1"]));
$mol2 = trim(strtolower($_GET["mol2"]));
$host = trim(strtolower($_GET["host"]));
$send = trim(strtolower($_GET["send"]));
$deadline = trim(strtolower($_GET["deadline"]));
$project = "/home/boincadm/projects/DrugDiscovery/";

if ($deadline == "" || $deadline < 86400)
{
$deadline=259200;
}


//echo "Deadline " . $deadline;

//Parameters
$compute_unbound_extended_flag=0;
$ga_run=1;

$user = get_logged_in_user();
$query = "select userid from host where id = ". $host ;
$result = mysql_query($query);
        if ($result) {
	//echo "No Host!";
	//$host_userid = mysql_result($result, 0);
        }

$host_userid = mysql_result($result, 0);
$user_id = $user->id;

                if ($lig_type=="mol1")
                {
                $lig = $mol1;
		$full_lig = "nsc". $lig .".mol2";
                `wget -O ${project}download/nsc${lig}.mol2 'http://cactus.nci.nih.gov/cgi-bin/nci2.tcl?output=sybyl2&op1=nsc&data1=${lig}&conflist=-1&passid=&nomsg=1'`;
		`chmod a+w ${project}download/nsc${lig}.mol2`;
		$NoQuery_lig = `grep -o 'No query' ${project}download/nsc${lig}.mol2 | head -n 1`;
		$Illegal_lig = `grep -o Illegal ${project}download/nsc${lig}.mol2 | head -n 1`;
		$NoMatches_lig = `grep -o 'No matches' ${project}download/nsc${lig}.mol2 | head -n 1`;

                }
                else
                {
                $lig = $pdb1;
		$full_lig = "pdb". $lig .".pdb";
                `wget --retr-symlinks -P ${project}download ftp://ftp.rcsb.org/pub/pdb/data/structures/all/pdb/pdb${lig}.ent.Z`;
		`chmod a+w ${project}download/pdb${lig}.ent.Z`;
                `gunzip ${project}download/pdb${lig}.ent.Z`;
                `mv ${project}download/pdb${lig}.ent ${project}download/pdb${lig}.pdb`;
		$NoQuery_lig = `grep -o 'No query' ${project}download/pdb${lig}.pdb | head -n 1`;
		$Illegal_lig = `grep -o Illegal ${project}download/pdb${lig}.pdb | head -n 1`;
		$NoMatches_lig = `grep -o 'No matches' ${project}download/nsc${lig}.mol2 | head -n 1`;
                }

	$full_rec = "pdb" . $rec . ".pdb";
        `wget --retr-symlinks -P ${project}download ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/pdb/pdb${rec}.ent.gz`;
	//`wget --retr-symlinks -P /home/boincadm/projects/DrugDiscovery/download/ /home/boincadm/projects/DrugDiscovery/download/pdb1uwq.ent.gz`;
	// `/home/boincadm/projects/DrugDiscovery/bin//home/boincadm/projects/DrugDiscovery/`;

        `gunzip ${project}download/pdb${rec}.ent.gz`;
        `mv ${project}download/pdb${rec}.ent ${project}download/pdb${rec}.pdb`;
        $NoQuery_rec = `grep -o 'No query' ${project}download/pdb${rec}.pdb | head -n 1`;
        $Illegal_rec = `grep -o Illegal ${project}download/pdb${rec}.pdb | head -n 1`;
	$NoMatches_rec = `grep -o 'No matches' ${project}download/pdb${rec}.pdb | head -n 1`;


$Illegal_lig = trim($Illegal_lig);
$NoQuery_lig = trim($NoQuery_lig);
$NoMatches_lig = trim($NoMatches_lig);
$Illegal_rec = trim($Illegal_rec);
$NoQuery_rec = trim($NoQuery_rec);
$NoMatches_rec = trim($NoMatches_rec);


//error handling

if (($c_time - $timestamp) < 1) {
page_head("Workunits already created");
}

elseif ($lig == "" ) {
page_head("No Ligand!");
}

elseif ($NoQuery_lig == "No query") {
page_head("No Ligand!");
}

elseif ($NoMatches_lig == "No matches") {
page_head("No Ligand!");
}

elseif ($mol1 == "" && $mol2 == "" && $pdb1 == ""  ) {
page_head("No Parameters!");
}

elseif ($Illegal_lig == "Illegal") {
page_head("Bad Ligand!");
}

elseif ($rec == ""  ) {
page_head("No Receptor!");
}

elseif ($NoQuery_rec == "No query") {
page_head("No Receptor!");
}

elseif ($NoMatches_rec == "No query") {
page_head("No Receptor!");
}

elseif ($Illegal_rec == "Illegal") {
page_head("Bad Receptor!");
}

elseif ($host_userid != $user_id && $host != "") {
page_head("Not Your Host");
}



else {



	$timeDate = time();

	if ($lig_type=="mol1")
	{
	shell_exec("echo \"<job_desc>
    <task>
        <application>prepare_ligand4</application>
        <command_line> -l ". $timeDate . "_nsc". $lig .".mol2 -o nsc". $lig .".pdbqt</command_line>    
    </task>
    <task>
        <application>prepare_receptor4</application>
        <command_line> -U nphs_lps_waters -r ". $timeDate ."_pdb". $rec .".pdb -o pdb". $rec .".pdbqt</command_line>
    </task>
    <task>        
	<application>prepare_gpf4</application>
        <command_line> -l nsc". $lig .".pdbqt -r pdb". $rec .".pdbqt -p custom_parameter_file=1 -p parameter_file=AD4_parameters.dat</command_line>    
    </task>
    <task>
        <application>prepare_dpf4</application>
        <command_line> -l nsc". $lig .".pdbqt -r pdb". $rec .".pdbqt -p compute_unbound_extended_flag=". $compute_unbound_extended_flag ." -p ga_run=". $ga_run ."</command_line>
    </task>
    <task>
        <application>autogrid</application>
        <command_line> -p pdb". $rec .".gpf -l out.glg </command_line>
    </task>    
    <task>
        <application>autodock</application>        
	<command_line> -p nsc". $lig ."_pdb". $rec .".dpf -l out.dlg </command_line>
    </task>
    <task>
        <application>write_all_complexes</application>
        <command_line> -d out.dlg -r pdb". $rec .".pdbqt -o out </command_line>
    </task>
    <task>
        <application>summarize_results4</application>
        <command_line> -d . -r pdb". $rec .".pdbqt -o summary.txt </command_line>
    </task>
    <task>
        <application>zip.exe</application>
        <command_line>out -q -r out . -i *.pdb *.dlg</command_line>
    </task>
</job_desc>
\" > ${project}download/ad_nsc". $lig .".mol2_pdb". $rec .".pdb_". $timeDate);

	`${project}bin/make_autodock nsc${lig}.mol2 pdb${rec}.pdb ${timeDate} ${deadline} ${lig} ${rec}`;
	}
	else
        {
        shell_exec("echo \"<job_desc>
    <task>
        <application>prepare_ligand4</application>
        <command_line> -l ". $timeDate ."_pdb". $lig .".pdb -o pdb". $lig .".pdbqt</command_line>  
    </task>
    <task>
        <application>prepare_receptor4</application>
        <command_line> -U nphs_lps_waters -r ". $timeDate ."_pdb". $rec .".pdb -o pdb". $rec .".pdbqt</command_line>
    </task>
    <task>
        <application>prepare_gpf4</application>
        <command_line> -l pdb". $lig .".pdbqt -r pdb". $rec .".pdbqt</command_line>
    </task>
    <task>
        <application>prepare_dpf4</application>
        <command_line> -l pdb". $lig .".pdbqt -r pdb". $rec .".pdbqt -p compute_unbound_extended_flag=". $compute_unbound_extended_flag ." -p ga_run=". $ga_run ."</command_line>
    </task>
    <task>
        <application>autogrid</application>
        <command_line> -p pdb". $rec .".gpf -l out.glg </command_line>
    </task>
    <task>
        <application>autodock</application>
        <command_line> -p pdb". $lig ."_pdb". $rec .".dpf -l out.dlg </command_line>
    </task>
    <task>
        <application>write_all_complexes</application>
        <command_line> -d out.dlg -r pdb". $rec .".pdbqt -o out </command_line>
    </task>
    <task>
        <application>summarize_results4</application>
        <command_line> -d . -r pdb". $rec .".pdbqt -o summary.txt </command_line>
    </task>
    <task>
        <application>zip.exe</application>
        <command_line>out -q -r out . -i *.pdb *.dlg</command_line>
    </task>
</job_desc>
\" > ${project}download/ad_pdb". $lig .".pdb_pdb". $rec .".pdb_". $timeDate);


        `/home/boincadm/projects/DrugDiscovery/bin/cp_bin_dir2 pdb${lig}.pdb pdb${rec}.pdb ${timeDate} ${deadline} ${lig} ${rec}`;
        }

	sleep(20);
	
	if ($host != "") {
	db_init();
	$query = "UPDATE result SET hostid = " . $host . ", userid = " . $user->id  .  ", server_state = 4,  sent_time = UNIX_TIMESTAMP() + 0 , report_deadline = UNIX_TIMESTAMP() + " . $deadline . " WHERE name = '" . $lig . "_" . $rec . "_" . $timeDate . "_0'"; 	
	//$query = "UPDATE result SET hostid = " . $host . ", userid = " . $user->id  .  ", server_state = 4,  name = '" . $lig . "_" . $rec . "_" . $timeDate . "_0'";
	//$query = "UPDATE result SET hostid = " . $host . " WHERE name = 'ad_" . $timeDate . "_0'";
	$query = trim($query);
	$result = mysql_query($query);
	//echo $result;
	if (!$result) {
    	die('Could not query:' . mysql_error());
	}	
        }

	if ($send == 1) {
        $query = "INSERT INTO email_result (userid, sent, workunitid, resultid) VALUES ('" . $user->id . "' , 0, (select max(id) from workunit where name = '" . $lig . "_" . $rec . "_" . $timeDate . "'), (select max(id) from result where name = '" . $lig . "_" . $rec . "_" . $timeDate . "_0'))";	
        $query = trim($query);
        $result = mysql_query($query);
        if (!$result) {
          die('Could not query:' . mysql_error());
       	  }
	}

	$query = "select id from workunit where name = '" . $lig . "_" . $rec . "_" . $timeDate . "'";
	$query = trim($query);


	$result = mysql_query($query);
	if (!$result) {
    	die('Could not query:' . mysql_error());
	}
	
	$wuid = mysql_result($result, 0);

	$wu = lookup_wu($wuid);
	if (!$wu) {
    		error_page("can't find workunit");
	}	
	page_head("Workunit <pre> Deadline: $deadline WU ID: $wuid User $user->id <a href=\"workunit.php?wuid=$wuid\">Refresh?</a></pre>");
	$app = lookup_app($wu->appid);
	start_table();
	row2("application", $app->user_friendly_name);
	row2("created", time_str($wu->create_time));
	row2("name", $wu->name);
	if ($wu->canonical_resultid) {
    		row2("canonical result", "<a href=result.php?resultid=$wu->canonical_resultid>$wu->canonical_resultid</a>");
    		row2("granted credit", format_credit($wu->canonical_credit));
	}
	row2("minimum quorum", $wu->min_quorum);
	row2("initial replication", $wu->target_nresults);
	row2("max # of error/total/success results",
    		"$wu->max_error_results, $wu->max_total_results, $wu->max_success_results"
	);
	if ($wu->error_mask) {
    		row2("errors", wu_error_mask_str($wu->error_mask));
	}
	if ($wu->need_validate) {
    		row2("validation", "Pending");
	}
	end_table();
	project_workunit($wu);

	result_table_start(false, true, true);
	$result = mysql_query("select * from result where workunitid=$wuid");
	while ($res = mysql_fetch_object($result)) {
    		show_result_row($res, false, true, true);
	}
	mysql_free_result($result);
	echo "</table>\n";
	}
//}
//else 
//{
//page_head("Not Your Host!");
//}

//else {
//page_head("Workunits already created");
//}

page_tail();
?>
