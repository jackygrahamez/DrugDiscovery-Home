<?php

// This file is part of BOINC.
// http://boinc.berkeley.edu
// Copyright (C) 2008 University of California
//
// BOINC is free software; you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License
// as published by the Free Software Foundation,
// either version 3 of the License, or (at your option) any later version.
//
// BOINC is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with BOINC.  If not, see <http://www.gnu.org/licenses/>.

$status = $argv[1];
$name = $argv[2];
$bt = $argv[3];
$lig = $argv[4];
$ts = $argv[5];
$steps = $argv[6];
$nsteps = $argv[7];
$complete = $argv[8];
$dist1 = $argv[9];
$dist2 = $argv[10];
$dist3 = $argv[11];
$dist4 = $argv[12];
$dist5 = $argv[13];

$cli_only = true;
require_once("../inc/util_ops.inc");

db_init();

$query="INSERT INTO mdrun_progress (status, name, bt, lig, ts, steps, nsteps, complete, dist1, dist2, dist3, dist4, dist5) VALUES ($status, '$name', '$bt', '$lig', '$ts', $steps, $nsteps, $complete, $dist1, $dist2, $dist3, $dist4, $dist5)";
echo $query."\n";
$result = mysql_query($query);

?>
