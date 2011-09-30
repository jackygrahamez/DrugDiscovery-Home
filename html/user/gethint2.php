<?php

require_once("../inc/util.inc");
require_once("../inc/uotd.inc");
require_once("../inc/profile.inc");

db_init();
//get the q parameter from URL
$q=$_GET["q"];

//lookup all hints from array if length of q>0
if (strlen($q) > 0)
  {
  $hint="";
  $result = mysql_query("select name from user where name like 'Jaxis%'");
  echo $result;
  $row = mysql_fetch_row($result);

	if (!$result) {
    	echo 'Could not run query: ' . mysql_error();
    	exit;
	}

  $hint = ($row[0]);

  }

// Set output to "no suggestion" if no hint were found
// or to the correct values
if ($hint == "")
  {
  $response="no suggestion";
  }
else
  {
  $response=$hint;
  }

//output the response
echo $response;
?>
