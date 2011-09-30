<?php

// each news item is an array:
// 0: date
// 1: content
// 2: title (optional)
// 3: category (optional)
//    suggested values:
//          "server status"
//          "news"
//          "emergency"
$project_news = array(
    array("April 18, 2010", "On Friday, May 20, NYAS will host the upcoming conference entitled, &quot;New Frontiers in Marine Drug Discovery&quot; at our conference center in New York City. This 1-day symposium will overview the current state of the art in Marine Biomedicine and its role in the context of the drug discovery process  from the perspectives of both academia and industry. More information about this event http://www.nyas.org/MarineBiomed"),

    array("July 20, 2010", "Hydrogen@Home is raising money to build GPU support for OpenMM GROMACS. These modifications will be made available to other projects including DD@H. We encourage people to contribute to this development"),

    array("June 6, 2010", "Protein-ligand interactions evaluation using distributed volunteer computing project Drugdiscovery@home has been accepted for poster presentation at the NCI/NCRI Joint Conference Biomedical Informatics without Borders, being held at the Doubletree Bethesda Hotel, Bethesda MD, June 21-22, 2010", "Abstract Submission"),
    array("April 2, 2010", "We have updated the error rates for Autodock and GROMACs applications in our forum for different opperational systems (Number crunching-stats status update). ", "Error rate update"),
    array("December 31, 2009", "Just allocated some additional space for our project. Happy New Years! Be safe.", "Disk Allocation"),
    array("December 29, 2009","Drugdiscovery@home team wishes you a merry Christmas and Happy New year to all our project participants as well as to all other people involved in volunteer computing projects", "Happy Holidays"),
    array("December 15, 2009","MDRUN app is working very well on Windows and 64-bit Linux. There is a little problem on startup for 32-bit Linux where the wrapper fails to execute. It should be fixed in a few days. Otherwise the project is looking spectacular!", "Progress Report"),
    array("November 18, 2009","Taking down the server to shrink the database", "Disk Management"),

    array("November 14, 2009","Currently the project is down for some maintenance. We hope to restore it in a few hours.", "Project Down"),

    array("November 8, 2009","recommended boinc client version. 6.10.17+ please update to this version so that we all are on the same client version.", "Client Version"),

    array("October 14, 2009","Please, join the discussion at our meassage boards on organizational questions of the legal entity for the Drugdiscovery@home project and project status.", "Organizational form"),    
    array("October 13, 2009","We are preparing to migrate the server to a host provided by IronScale. Workunits are disabled at the moment", "Migration"), 

    array("October 5, 2009", "We are improving the progress bar for our apps. This is especially important for mdrun where we want to run simulations for several days. With a progress bar that updates every 100 steps of a 5 million step simulation, a cruncher should be more confident that the simulation is running properly if they see th progress bar updating over the course of 5 days. In addition, checkpointing is already a feature native to this app, so if you pause, you should be able to return to the same point in the simulation. -Jack", "Progress bar update"),

    array("September 23, 2009", "The group on Drugdiscovery@home project was created at Facebook. It's called: \"Drugdiscovery@home - help us making new cures for age related diseases\". We'll be glad to invite people interested in distributed computing application for the early drug discovery process. ","Drugdiscovery@home group at Facebook"),    
    array("September 14, 2009", "We have translated www.drugdiscoveryathome.com content into several languages. If you still see some strange translation for your language - this means that we need  your help with translation.","Translations"),    
    array("September 10, 2009", "Drugdiscovery@home project was presented on SENS4 conference at Cambridge (UK) during 3-7th of September. If you are interested in acceleration of early drug discovery research in the fields of aging, cancer and stem cells - please join our project.","Project presentation on SENS4"),  
    array("September 8, 2009", "Please help us translate our pages on www.drugdiscoveryathome.com","Translations"),

    array("September 3, 2009", 
"See our demo simulation posted on www.drugdiscoveryathome.com","Demo Animation"),

    array("August 26, 2009",
"Our project is back online. We now have a workflow to further analyze docking results using molecular dynamics. We are also on the verge of providing GPU support. Our project needs its volunteers to come back. Your credits can be restored. Just provide us your username, authenticator and email address. We also have account creation temporarily enabled so you can register. -Jack",
"Need more hosts!", ""),

    array("August 10, 2009",
"We are in the process of restoring user data",
"Project Up"),

    array("August 2, 2009",
"We have a problem with a corrupt database",
"Project Down"),

    array("July 17, 2009",
	"We are working on several things, resolving problems with certain ligands, experimenting with GPUs and studying the feasability of optimizing gromacs for PS3s for our project. I am also planning another BOINC Meetup. This time a social gathering on the US National Mall to watch Close Encounters of the 3rd Kind. Bring your SETI Shirts http://opensource.meetup.com/84/",
),

    array("July 14, 2009",
	"Happy Bastille Day! We are now looking at GPU integration for GROMACS. We may need a little help with this integration. Here is a thread I started which includes links to related code. There is a msvc solution for building gromacs and there are various pre-compiled libraries for integrating cuda called OpenMM, read more http://boinc.drugdiscoveryathome.com/forum_thread.php?id=84",
),

    array("July 13, 2009",
	"We submitted a large batch of flexible docking last night. Almost 200,000 workunits pending. Come and kill this queue and please if there are any Macs, by all means attach. -Jack",
    ),

    array("May 29, 2009",
	"Recently purchased a system with nvidia cards and will begin testing cuda code for GROMACS. We will also be running flexible docking simulations in the next few days. And then taking those results and simulating the docking complexes with GROMACS."
    ),
    array("May 6, 2009",
        "Our project Designs and Tests prospective drug-like compounds for regulation of signaling pathways involved in tissue engineeering and cancer. Currently we are benchmarking Autodock on Lysozyme and H1N1 Neurominidase."
    ),
    array("May 11, 2009",
	"In the process of converting some 600,000 molecular structures to a pdbqt format for analysis with Autodock."
    )
);

?>
