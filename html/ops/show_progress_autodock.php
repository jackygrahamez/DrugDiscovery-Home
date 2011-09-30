<?php
require_once("../inc/util.inc");
require_once("../inc/user.inc");
require_once("../inc/db.inc");
require_once("../inc/forum.inc");
require_once("../inc/result.inc");

db_init();

#$result = mysql_query("select * from mdrun_progress");
#$result = mysql_query("SELECT `bt`,`lig`, `ts`, `nsteps`, max(`steps`) as STEPS, `complete`,`dist1`, `dist2`, `dist3`, `dist4`, `dist5` FROM `mdrun_progress` GROUP By `lig`, `bt` Having max(steps) order by `steps` DESC");
$result = mysql_query("SELECT `bt`,`lig`, `ts`, max(`steps`) as STEPS, AVG(`dist2`)*10 as AVG_DIST, STD(`dist2`)*10 as STD_DIST, (AVG(`dist2`) - STD(`dist2`)*2)*10 as MIN, (AVG(`dist2`) + STD(`dist2`)*2)*10 as MAX FROM `mdrun_progress` where bt like '%Autodock.pdb' GROUP By `lig`, `bt` Having max(steps) order by `steps` DESC");

echo "<head><script src=\"sorttable.js\"></script></head><link rel=\"stylesheet\" type=\"text/css\" href=\"mystyle.css\" />";

echo "<body><h1>MDRUN PROGRESS REPORT</h1></body><p>Click table headers to sort</p>";
echo "<table border='1' class='sortable'>
<tr>
<th>BT</th>
<th>LIG</th>
<th>TS</th>
<th>Current Step</th>
<th>AVG_DIST_ANGSTROM</th>
<th>STD_DIST_ANGSTROM</th>
<th>MIN 95% Confidence</th>
<th>MAX 95% Confidence</th>
</tr>";


while ($row = mysql_fetch_assoc($result)) {
    echo "<tr>";
    echo "<td>". $row['bt']."</td>";
    echo "<td>". $row['lig']."</td>";
    echo "<td>". $row['ts']."</td>";
    echo "<td>". $row['STEPS']."</td>";  
    echo "<td>". $row['AVG_DIST']."</td>";
    echo "<td>". $row['STD_DIST']."</td>";
    echo "<td>". $row['MIN']."</td>";
    echo "<td>". $row['MAX']."</td>";
    echo "</tr>";
}
echo "</table>";

?>

