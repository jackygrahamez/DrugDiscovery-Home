#!/usr/bin/python

import os
import os.path
import sys
import commands
import subprocess
import urllib2
import time
import random

index = open('/home/boincadm/projects/DrugDiscovery/bin/pid_index2.txt', 'r')
for patent in index:
	request = urllib2.Request('http://www.google.com/patents/download/".$pid."_Process_for_the_preparation_of_a.pdf?id=ae8AAAAAEBAJ&output=pdf&sig=ACfU3U1DHEyY6MGCZYWEpD5fVTg0CTceAw&source=gbs_overview_r&cad=0')
	request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.13) Gecko/2009073021 Firefox/3.0.13')
	opener = urllib2.build_opener() 
	page = opener.open(request).read()
	localFile = open('/home/boincadm/projects/DrugDiscovery/patents/'+patent+'.pdf', 'wb')
	localFile.write(page)
	localFile.close()
	print patent
	time.sleep(600+60*random.randint(1,10))

index.close()
