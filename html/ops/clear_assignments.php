<?php
//require_once("../inc/util.inc");
//require_once("../inc/user.inc");
require_once("../inc/db.inc");
//require_once("../inc/forum.inc");
//require_once("../inc/result.inc");


// show the home page of whoever's logged in

db_init();
$query = "delete from assignment";
$result = mysql_query($query);
?>
