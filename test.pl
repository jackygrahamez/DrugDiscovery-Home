#!/usr/bin/perl -w
#-- list the processes running on your system
open(PS,"ps -e |") || die "Failed: $!\n";
while ( <PS> )
{
  system('du -h --max-depth=1');
}
