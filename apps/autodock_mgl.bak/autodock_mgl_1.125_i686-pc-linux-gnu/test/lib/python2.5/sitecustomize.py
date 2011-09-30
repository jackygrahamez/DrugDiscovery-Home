mglroot = '/root/mgltools_i86Linux2_1.5.2'# specify mglroot here
import sys, os
path = os.path.join(".", "MGLToolsPckgs")
sys.path.insert(0,path)

from Support.path import setSysPath
setSysPath(path)
#sys.path.insert(0,'.')
