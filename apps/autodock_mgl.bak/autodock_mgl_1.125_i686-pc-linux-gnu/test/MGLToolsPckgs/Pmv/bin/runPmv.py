# $Header: /opt/cvs/python/packages/share1.5/Pmv/bin/runPmv.py,v 1.76 2007/11/16 23:39:52 vareille Exp $
# $Id: runPmv.py,v 1.76 2007/11/16 23:39:52 vareille Exp $

# pmv can be launched from a python shell like this:
#import Pmv; Pmv.runPmv()

import sys
import Pmv
if '__file__' in locals():
    Pmv.runPmv(sys.argv,__file__)
else:
    Pmv.runPmv(sys.argv,'')