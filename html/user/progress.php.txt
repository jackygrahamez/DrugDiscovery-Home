<?php
require_once("../inc/db.inc");
db_init();

$result = mysql_query("SELECT `bt`,mid(`lig`,3,6) as LIG, max(`steps`) as STEPS, AVG(`dist2`)*10 as AVG_DIST, STD(`dist2`)*10 as STD_DIST, (AVG(`dist2`) - STD(`dist2`)*2)*10 as MIN, (AVG(`dist2`) + STD(`dist2`)*2)*10 as MAX FROM `mdrun_progress` GROUP By `lig`, `bt` Having max(steps) order by `steps` DESC");

echo "<head><script src=\"sorttable.js\"></script></head><link rel=\"stylesheet\" type=\"text/css\" href=\"mystyle.css\" />";

echo "<body><h1>MDRUN PROGRESS REPORT</h1></body><p>Click table headers to sort</p>";
echo "<table border='1' class='sortable'>
<tr>
<th>Ligand</th>
<th>Receptor</th>
<th>Current Step</th>
<th>AVG_DIST_ANGSTROM</th>
<th>STD_DIST_ANGSTROM</th>
<th>MIN 95% Confidence</th>
<th>MAX 95% Confidence</th>
</tr>";


while ($row = mysql_fetch_assoc($result)) {
    echo "<tr>";
    echo "<td>". $row['LIG']."</td>";
    echo "<td>". $row['bt']."</td>";
    echo "<td>". $row['STEPS']."</td>";  
    echo "<td>". $row['AVG_DIST']."</td>";
    echo "<td>". $row['STD_DIST']."</td>";
    echo "<td>". $row['MIN']."</td>";
    echo "<td>". $row['MAX']."</td>";
    echo "</tr>";
}
echo "</table>";

?>

