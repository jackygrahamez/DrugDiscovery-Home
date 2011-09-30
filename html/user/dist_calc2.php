<?php

if ($_GET["lat"] == "" || $_GET["lon"] == "") {
$lat=40;
$lon=25;
echo "LAX";
}
else {
$lat=$_GET["lat"];
$lon=$_GET["lon"];

$con = mysql_connect("localhost","boincadm","!QAZxsw2");
if (!$con)
  {
  die('Could not connect: ' . mysql_error());
  }

// some code
mysql_select_db("airports", $con);

//$sql="SELECT IATA, LAT, LON, ABS(180+LAT-180+".$lat.") +  ABS(180+LON-180+".$lon.") AS DIST, ROUND(SQRT(POW((69.1 * (LAT-".$lat.")), 2) + POW((53 *  LON-".$lon."),2)),1) AS distance, ABS(180+LAT-180+".$lat.") AS DLAT, ABS(180+LON-180+".$lon.") AS DLON from airports order by DIST LIMIT 10";

$sql="SELECT IATA, LAT, LON, ((ACOS(SIN(".$lat." * PI() / 180) * SIN(LAT * PI() / 180) + COS(".$lat." * PI() / 180) * COS(LAT * PI() / 180) * COS((".$lon." - LON) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) AS DIST, ROUND(SQRT(POW((69.1 * (LAT-".$lat.")), 2) + POW((53 *  LON-".$lon."),2)),1) AS distance, ABS(180+LAT-180+".$lat.") AS DLAT, ABS(180+LON-180+".$lon.") AS DLON from airports order by DIST LIMIT 10";


$result = mysql_query($sql);
echo "<TABLE>";
echo "<tr>";
while($row = mysql_fetch_array($result))
  {
  echo "<td>".$row['IATA']."<td>".$row['LAT']."</td><td>".$row['LON']."</td><td>".$row['distance']."</td><td>".$row['DIST']."</td><td>".$row['DLAT']."</td><td>".$row['DLON'];
  echo "</tr>";
  }
echo "</tr>";
echo "</TABLE>";

mysql_close($con);
}
?>
