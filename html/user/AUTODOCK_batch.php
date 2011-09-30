<?php

require_once("../inc/util.inc");
require_once("../inc/user.inc");
require_once("../inc/db.inc");
require_once("../inc/forum.inc");
require_once("../inc/result.inc");
db_init();
$user = get_logged_in_user();
$user_id = '<a href="show_user.php?userid='.$user->id.'">'.$user->name.'</a>';
$send = 0;

$query = "select userid from forum_preferences where special_user <> 0 AND userid = " . $user->id;
$query = trim($query);
$result = mysql_query($query);

        if (!$result) {
        die('Could not query:' . mysql_error());
        }

if (mysql_result($result, 0) != $user->id) {
	die("I'm sorry, please contact the administer for help submiting GROMACS Workunits.");
}

$timeDate = time();
mysql_free_result($result);
$deadline = 86400;
$query = "select create_time from workunit where id = (select max(id) from workunit)";
$result = mysql_query($query);
$timestamp = mysql_result($result,0);
$c_time = time();
$host = trim(strtolower($_POST["host"]));
$jobfile = trim($_POST["jobfile"]);
$deadline = trim(strtolower($_POST["deadline"]));
$name = trim(strtolower($_POST["workunit_name"]));
$ligand = trim($_POST["ligand"]);
$receptor = trim($_POST["receptor"]);
$project = "/home/boincadm/projects/DrugDiscovery/";
$user = get_logged_in_user();
$user_id = $user->id;

$job_path = $project . 'download/job.xml=' . $timeDate;
$ligand_path = $project . 'download/ligand=' . $timeDate;
$receptor_path = $project . 'download/receptor=' . $timeDate;


        if (!($fp = fopen($job_path, 'w'))) {
        return;
        }

        fprintf($fp, "%s", $jobfile);
        fclose($fp);

	if (!($fp = fopen($ligand_path, 'w'))) {
    	return;
	}

	fprintf($fp, "%s", $ligand);
	fclose($fp);

        if (!($fp = fopen($receptor_path, 'w'))) {
        return;
        }

        fprintf($fp, "%s", $receptor);
        fclose($fp);

        `${project}bin/autodock_batch_work ${name} ${timeDate}`;
	sleep(5);

        if ($host != "") {
        db_init();
        $query = "UPDATE result SET hostid = " . $host . ", userid = " . $user->id  .  ", server_state = 4,  sent_time = UNIX_TIMESTAMP() + 0 , report_deadline = UNIX_TIMESTAMP() + " . $deadline . " WHERE name = '". $name  . "_" . $timeDate . "_0'";
        $query = trim($query);
        $result = mysql_query($query);
        if (!$result) {
        die('Could not query:' . mysql_error());
        }
        }


        if ($send == 1) {
        $query = "INSERT INTO email_result (userid, sent, workunitid, resultid) VALUES ('" . $user->id . "' , 0, (select max(id) from workunit where name = '". $name  . "_" . $timeDate . "'), (select max(id) from result where name = '". $name  . "_" . $timeDate . "_0'))";
        $query = trim($query);
        $result = mysql_query($query);
        if (!$result) {
          die('Could not query:' . mysql_error());
          }
        }

        $query = "select id from workunit where name = '". $name  . "_" . $timeDate . "'";
        $query = trim($query);

        $result = mysql_query($query);
        if (!$result) {
        die('Could not query:' . mysql_error());
        }

        $wuid = mysql_result($result, 0);
	//echo "<br>$wuid<br>";

        $wu = lookup_wu($wuid);
        if (!$wu) {
                error_page("can't find workunit ");
        }
        page_head("Workunit <pre> Deadline: $deadline WU ID: $wuid User $user->id <a href=\"workunit.php?wuid=$wuid\">Refresh?</a></pre>");
        $app = lookup_app($wu->appid);
	
        start_table();
	row2("", "<pre><a href=\"workunit.php?wuid=$wuid\">Refresh?</a></pre>");
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
	//}
        $query = "select id from workunit where name = '". $name  . "_" . $timeDate . "'";
        $query = trim($query);


     	ult_table_start(false, true, true);
        $result = mysql_query("select * from result where workunitid=$wuid");
        while ($res = mysql_fetch_object($result)) {
                show_result_row($res, false, true, true);
        }
        mysql_free_result($result);
  	$result = mysql_query($query);
        if (!$result) {
        die('Could not query:' . mysql_error());
        }

        $wuid = mysql_result($result, 0);
	page_tail();
?>
