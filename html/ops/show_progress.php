<?php
require_once("../inc/util.inc");
require_once("../inc/user.inc");
require_once("../inc/db.inc");
require_once("../inc/forum.inc");
require_once("../inc/result.inc");

db_init();

#$result = mysql_query("select * from mdrun_progress");
$result = mysql_query("SELECT `bt`,`lig`, `ts`, `nsteps`, max(`steps`) as STEPS, `complete`,`dist1`, `dist2`, `dist3`, `dist4`, `dist5` FROM `mdrun_progress` GROUP By `lig`, `bt` Having max(steps) order by `steps` DESC");

echo "<table border='1'>
<tr>
<th>BT</th>
<th>LIG</th>
<th>TS</th>
<th>Total Steps</th>
<th>Current Step</th>
<th>Complete</th>
<th>Dist1</th>
<th>Dist2</th>
<th>Dist3</th>
<th>Dist4</th>
<th>Dist5</th>
</tr>";


while ($row = mysql_fetch_assoc($result)) {
    echo "<tr>";
    echo "<td>". $row['bt']."</td>";
    echo "<td>". $row['lig']."</td>";
    echo "<td>". $row['ts']."</td>";
    echo "<td>". $row['nsteps']."</td>";   
    echo "<td>". $row['STEPS']."</td>";  
    echo "<td>". $row['complete']."</td>";
    echo "<td>". $row['dist1']."</td>";  
    echo "<td>". $row['dist2']."</td>";  
    echo "<td>". $row['dist3']."</td>";  
    echo "<td>". $row['dist4']."</td>";  
    echo "<td>". $row['dist5']."</td>"; 
    echo "</tr>";
}
echo "</table>";

?>

