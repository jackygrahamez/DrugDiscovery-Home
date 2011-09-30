<?php
require_once("../inc/util.inc");
require_once("../inc/user.inc");
require_once("../inc/db.inc");
require_once("../inc/forum.inc");
require_once("../inc/result.inc");

db_init();

echo "<head><script src=\"sorttable.js\"></script></head><link rel=\"stylesheet\" type=\"text/css\" href=\"mystyle.css\" />";

$result = mysql_query("select id, MID(simulation, INSTR(simulation, '_ts_')+4, 19) as ts, simulation, lowest_energy from autodock_scores where simulation like '/home/boincadm/projects/DrugDiscovery/sample_results/PMC1IJY.zip/rcs%'");

echo "<table border='1' class='sortable'>
<tr>
<th>ID</th>
<th>ts</th>
<th>Simulation</th>
<th>Lowest Energy</th>
</tr>";


while ($row = mysql_fetch_assoc($result)) {
    echo "<tr>";
    echo "<td>".$row['id']."</td>"; 
    echo "<td>".$row['ts']."</td>";
    echo "<td>". $row['simulation']."</td>";
    echo "<td>". $row['lowest_energy']."</td>";
    echo "</tr>";
}
echo "</table>";

?>

