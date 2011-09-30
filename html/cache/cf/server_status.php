<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"><html><head><title>Server status page</title>
<link rel=stylesheet type="text/css" href="main.css" media="all" />
		<link rel=stylesheet type="text/css" href="http://boinc.drugdiscoveryathome.com/white.css">
        <link rel=alternate type="application/rss+xml" title="DrugDiscovery@Home RSS 2.0" href="http://boinc.drugdiscoveryathome.com/rss_main.php">
        
        </head>
    <body>
<!-- SVN VERSIONS -->
<!-- $Id: translation.inc 19194 2009-09-28 04:24:18Z davea $ -->
<!-- $Id: pm.inc 14019 2007-11-01 23:04:39Z davea $ -->
<!-- $Id: text_transform.inc 19194 2009-09-28 04:24:18Z davea $ -->
<!-- $Id: stats_sites.inc 17954 2009-04-30 21:48:20Z davea $ -->
<!-- $Id: team.inc 17456 2009-03-03 21:58:03Z davea $ -->
<!-- $Id: user.inc 19201 2009-09-28 16:19:20Z davea $ -->
<!-- $Id: profile.inc 16749 2008-12-29 18:44:11Z jbk $ -->
<!-- $Id: util.inc 19194 2009-09-28 04:24:18Z davea $ -->

        <p>
        <span class="page_title">Server status page</span>
        <p>
    30 Sep 2011 21:57:34 UTC
        <table width=100%>
        <tr>
        <td width=40% valign=top>
        <p>Server status Disk Full: 27% 
</p><p>Available Memory       26  
 MB of   3956    
 MB</p>
        <!--<p>Pass Percentage <a href=http://boinc.drugdiscoveryathome.com/pass_percentage_by_platform.php?appid=5&nsecs=86400>Autodock_MGL</a> <a href=http://boinc.drugdiscoveryathome.com/pass_percentage_by_platform.php?appid=8&nsecs=86400>GROMACS</a></p> -->
        <table border=0 cellpadding=4>
        <tr><th>Program</th><th>Host</th><th>Status</th></tr>
    <tr><td>data-driven web pages</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>upload/download server</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>scheduler</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>feeder</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>transitioner</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>file_deleter</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>autodock_mgl_validator</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>autodock_mgl_assimilator</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>mdrun_validator</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>mdrun_assimilator</td><td>vps</td><td class="running">Running</td>
</tr>
<tr><td>mdrun_cuda_validator</td><td>vps</td><td class="disabled">Disabled</td>
</tr>
<tr><td>mdrun_cuda_assimilator</td><td>vps</td><td class="disabled">Disabled</td>
</tr>

        <tr><td align=right><b>Running:</b></td>
        <td colspan=2>Program is operating normally</td></tr>
        <tr><td align=right><b>Not Running:</b></td>
        <td colspan=2>Program failed or ran out of work<br>
           (or the project is down)</td></tr>
        <tr><td align=right><b>Disabled:</b></td>
        <td colspan=2>Program has been disabled by staff<br>
           (for debugging/maintenance)</td></tr>
        </table>
        </td>
        <td width=40% valign=top>
        <h2>Database/file status</h2>
    
            <table border=0 cellpadding=4>
            <tr><th>State</th><th>#</th></tr>
        <tr><td>Results ready to send</td><td>0</td></tr><tr><td>Results in progress</td><td>249</td></tr><tr><td>Workunits waiting for validation</td><td>0</td></tr><tr><td>Workunits waiting for assimilation</td><td>333</td></tr><tr><td>Workunits waiting for deletion</td><td>0</td></tr><tr><td>Results waiting for deletion</td><td>0</td></tr><tr><td>Transitioner backlog (hours)</td><td>0</td></tr></table>
        </td>
        <td>&nbsp;</td>
        </tr>
        </table>
    <br><hr noshade size=1><center><a href="http://drugdiscoveryathome.com/">Home</a> | <a href=index.php>Project</a> | <a href=home.php>My Account</a> | <a href=forum_index.php>Message Boards</a><br>
<br><br>Copyright &copy; 2011 DRUGDISCOVERY@HOME</center>
</body>
        </html>
    