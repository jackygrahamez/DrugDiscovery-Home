# $Header: /opt/cvs/python/packages/share1.5/Pmv/__init__.py,v 1.40 2008/01/21 22:06:23 vareille Exp $
# $Id: __init__.py,v 1.40 2008/01/21 22:06:23 vareille Exp $
# this makes this directory a package

import os
import sys
import getopt
import time
from string import split

from Support.version import __version__, __revision__

def setdmode(mode, mv):
    """
load display commands for mode and set them as default command for new molecule
"""
    if mode=='cpk':
        mv.browseCommands('displayCommands', commands=['displayCPK'],
              log=0, package='Pmv')
        mv.addOnAddObjectCmd(mv.displayCPK)

    elif mode=='lines':
        mv.browseCommands('bondsCommands',
              commands=('buildBondsByDistance',), log=0)
        mv.addOnAddObjectCmd(mv.buildBondsByDistance)
        mv.browseCommands('displayCommands', commands=('ribbon',), log=0)
        mv.addOnAddObjectCmd(mv.displayLines)

    elif mode=='ss':
        mv.browseCommands('secondaryStructureCommands',
              commands=('ribbon',), log=0)
        mv.addOnAddObjectCmd(mv.ribbon)

    elif mode=='sb':
        mv.browseCommands('bondsCommands',
                          commands=('buildBondsByDistance',), log=0)
        mv.addOnAddObjectCmd(mv.buildBondsByDistance)
        mv.browseCommands('displayCommands',
                          commands=('displaySticksAndBalls',), log=0)
        mv.addOnAddObjectCmd(mv.displaySticksAndBalls, (),
                             {'sticksBallsLicorice':'SticksAndBalls', 'cquality':0, 'bquality':0})

    elif mode=='lic':
        mv.browseCommands('bondsCommands',
                          commands=('buildBondsByDistance',), log=0)
        mv.addOnAddObjectCmd(mv.buildBondsByDistance)
        mv.browseCommands('displayCommands',
                          commands=('displaySticksAndBalls',), log=0)
        mv.addOnAddObjectCmd(mv.displaySticksAndBalls, (),
                             {'sticksBallsLicorice':'Licorice', 'cquality':0, 'cradius':.2})

    elif mode=='ms':
        mv.browseCommands('msmsCommands', commands=('computeMSMS',), log=0)
        mv.browseCommands('msmsCommands', commands=('displayMSMS',), log=0)
        mv.addOnAddObjectCmd(mv.computeMSMS, (), {'density':3.0})
        mv.addOnAddObjectCmd(mv.displayMSMS)
    
    elif mode=='ca':
        mv.browseCommands('traceCommands', commands=('computeTrace',), log=0)
        mv.browseCommands('traceCommands', commands=('extrudeTrace',), log=0)
        mv.browseCommands('traceCommands', commands=('displayTrace',), log=0)
        mv.addOnAddObjectCmd(mv.computeTrace)
        mv.addOnAddObjectCmd(mv.extrudeTrace)
        mv.addOnAddObjectCmd(mv.displayTrace)

    elif mode=='bt':
        mv.browseCommands('bondsCommands',
              commands=('buildBondsByDistance',), log=0)
        mv.browseCommands('displayCommands',
              commands=('displayBackboneTrace',), log=0)
        mv.addOnAddObjectCmd(mv.displayBackboneTrace, (), 
                 {'cquality':0, 'bquality':0, 'cradius':0.25,
                  'bRad':0.33} )
        
    elif mode=='sp':
        mv.browseCommands('splineCommands', commands=('computeSpline',), log=0)
        mv.browseCommands('splineCommands', commands=('extrudeSpline',), log=0)
        mv.browseCommands('splineCommands',
              commands=('displayExtrudedSpline',), log=0)
        mv.addOnAddObjectCmd(mv.computeSpline)
        mv.addOnAddObjectCmd(mv.extrudeSpline)
        mv.addOnAddObjectCmd(mv.displayExtrudedSpline)

    elif mode=='sssb':
        mv.browseCommands('displayCommands',
              commands=('displaySSSB',), log=0, package='Pmv')
        mv.addOnAddObjectCmd(mv.displaySSSB)


def setcmode(mode, mv):
    """
load color commands for mode and set them as default command for new molecule
"""
    if mode=='ca':
        mv.browseCommands('colorCommands', commands=('colorByAtomType',),
              log=0, package='Pmv')
        mv.addOnAddObjectCmd(mv.colorByAtomType)

    elif mode=='cr':
        mv.browseCommands('colorCommands',
              commands=('colorByResidueType',), log=0)
        mv.addOnAddObjectCmd(mv.colorByResidueType)
        
    elif mode=='cc':
        mv.browseCommands('colorCommands', commands=('colorByChains',),
              log=0, package='Pmv')
        mv.addOnAddObjectCmd(mv.colorByChains)

    elif mode=='cm':
        mv.self.browseCommands('colorCommands', commands=('colorByMolecules',),
                   log=0, package='Pmv')
        mv.addOnAddObjectCmd(mv.colorByMolecules)

    elif mode=='cdg':
        mv.browseCommands('colorCommands', commands=('colorAtomsUsingDG',),
              log=0, package='Pmv')
        mv.addOnAddObjectCmd(mv.colorAtomsUsingDG)

    elif mode=='cs':
        mv.browseCommands('colorCommands',
              commands=('colorResiduesUsingShapely',), log=0 )
        mv.addOnAddObjectCmd(mv.colorResiduesUsingShapely)

    elif mode=='css':
        mv.browseCommands('secondaryStructureCommands',
              commands=('colorBySecondaryStructure',), log=0)
        mv.addOnAddObjectCmd(mv.colorBySecondaryStructure)


##################################################################
# Define a bunch of useful methods
##################################################################
def ed():
    return mv.vision.ed


def net():
    return mv.vision.ed.currentNetwork


def nodes():
    return mv.vision.ed.currentNetwork.nodes


def runPmv(argv=None, PmvScriptPath=None):
    """The main function for running PMV
"""
    import sys

    if argv is None:
        argv = ['Pmv/bin/runPmv.py', '-i']
        PmvScriptPath = ''        

    optlist, args = getopt.getopt(argv[1:], 'haid:c:v:', ['update',
                'help', 'again', 'overwriteLog', 'uniqueLog', 'noLog', 'die',
            'customizer=', 'interactive', 'dmode=', 'cmode=', 'noSplash', 'vision'] )
    
    help_msg = """usage: pmv <options>
            -h or --help       : print this message
            -a or --again      : play back lastlog file
            --overwriteLog     : overwrite log file
            --uniqueLog        : create a log file with a unique name
            --noLog            : turn off logging
            --noSplash         : turn off Splash Screen
            --die              : do not start GUI event loop
            --customizer file  : run the user specified file
            --lib packageName  : add a libraries of commands
            -v r or --vision run  : run vision networks on the command line
            -v o or --vision once : run vision networks and exit PMV
    
        --update [nightly|tested|clear] : update MGLTools
                if no arguments are given Update Manager GUI is provided
                'nightly': download and install Nightly Builds
                'tested' : download and install tested Nightly Builds
                'clear'  : clear/uninstall all the updates      
    
        -d or --dmode modes : specify a display mode
                modes can be any a combination of display mode
               'cpk'  : cpk
               'lines': lines
               'ss'   : secondary structure ribbon
               'sb'   : sticks and balls
               'lic'  : licorice
               'ms'   : molecular surface
               'ca'   : C-alpha trace
               'bt'   : backbone trace
               'sp'   : CA-spline
               'sssb' : secondary structure for proteins,
                        sticks and balls for other residues with bonds
                    lines for other residues without bonds
    
        -c or --cmode modes : specify a dispaly mode
                    color scheme:
                'ca' : color by atom
                'cr' : color by residue (RASMOL scheme)
                'cc' : color by chain
                'cm' : color by molecule
                'cdg': color using David Goodsell's scheme
                'cs' : color residues using Shapely scheme
                'css': color by secondary structure element
                
              example:
              display protein as ribbon, non protein as sticks and balls
              and color by atom type
                 pmv -i --dmode sssb --cmode cr myprot.pdb
                 pmv -i -m sssb -c cr myprot.pdb
    
    """

    customizer = None
    logmode = 'overwrite'
    libraries = []
    again = 0
    interactive = 0
    die=0
    noSplash = False
    dmode = cmode = None
    dmodes = ['cpk', 'lines', 'ss', 'sb', 'lic', 'ms', 'ca', 'bt', 'sp', 'sssb' ]
    cmodes = ['ca', 'cr', 'cc', 'cm', 'cdg', 'cs', 'css']
    visionarg = None
    
    for opt in optlist:
        if opt[ 0] in ('-h', '--help'):
            print help_msg
            sys.exit()
        elif opt[ 0] in ('-a', '--again'):
            again = 1
            os.system("mv mvAll.log.py .tmp.py")
        elif opt[ 0] =='--overwriteLog': logmode = 'overwrite'
        elif opt[ 0] =='--uniqueLog': logmode = 'unique'
        elif opt[ 0] =='--noLog': logmode = 'no'
        elif opt[ 0] =='--die': die = 1
        elif opt[ 0] =='--noSplash': noSplash = True
        elif opt[ 0] == '--customizer':
            customFile = opt[1]
        elif opt[ 0] == '--lib':
            libraries.append(opt[1])
        elif opt[ 0] in ('-i', '--interactive'):
            interactive = 1
        elif opt[ 0] in ('-d', '--dmode'):
            assert min([mo in dmodes for mo in opt[1].split('|')])==True
            dmode = opt[1]
        elif opt[ 0] in ('-c', '--cmode'):
            assert min([mo in cmodes for mo in opt[1].split('|')])==True
            cmode = opt[1]
        elif opt[0] == '--update':
            try:
                from Support.update import Update
            except ImportError:
                print "Support package is needed to get updates"
                break
                
            update = Update()
            if 'nightly' in args:
                update.latest = 'nightly'
                update.getUpdates()
            elif 'tested' in args:
                update.latest     = 'tested'
                update.getUpdates()
            elif 'clear' in args:
                print "Removing all updates"
                update.clearUpdates()
            else:
                waitTk = update.gui()
                update.master.wait_variable(waitTk)
        elif opt[ 0] in ('-v', '--vision'):
            if opt[1] in ('o', 'once'):
                visionarg = 'once'
            elif opt[1] in ('r', 'run'):
                visionarg = 'run'
        else:
            print "unknown option %s %s"%tuple(opt)
            print help_msg
            sys.exit(1)
    
    #import sys
    text = 'Python executable     : '+ sys.executable +'\n'
    text += 'PMV script                : '+ PmvScriptPath +'\n'
    text += 'MGLTool packages '+'\n'
    
    from Support.path import path_text, release_path
    from Support.version import __version__, __revision__
    version = __version__
    text += path_text
    text += version+': '+release_path
    
    path_data = text
            
    print 'Run PMV from ', __path__[0]
    # if MGLPYTHONPATH environment variable exists - insert the specified path
    # into sys.path
    
    #if os.environ.has_key("MGLPYTHONPATH"):
    #    if sys.platform == "win32":
    #        mglPath = split(os.environ["MGLPYTHONPATH"], ";")
    #    else:
    #        mglPath = split(os.environ["MGLPYTHONPATH"], ":")
    #    mglPath.reverse()
    #    for p in mglPath:
    #        sys.path.insert(0, os.path.abspath(p))
        
    try:
        ##################################################################
        # Splash Screen
        ##################################################################
        image_dir = os.path.join( __path__[0],'Icons','Images')
        copyright = """(c) 1999-2008 Molecular Simulation Laboratory, The Scripps Research Institute
    ALL RIGHTS RESERVED """
        authors = """Authors: Michel F. Sanner, Chris Carrillo, Kevin Chan, 
Sophie Coon, Sargis Dallakyan, Alex Gillet, Ruth Huey, Sowjanya Karnati, 
William (Lindy) Lindstrom, Garrett M. Morris, Brian Norledge, Anna Omelchenko, 
Daniel Stoffler, Vincenzo Tschinke, Guillaume Vareille, Yong Zhao"""
        icon = os.path.join(__path__[0],'Icons','64x64','ss64.png')
        third_party = """Fast Isocontouring, Volume Rendering -- Chandrait Bajaj, UT Austin
Adaptive Poisson Bolzman Solver (APBS) -- Nathan Baker Wash. Univ. St Louis
GL extrusion Library (GLE) -- Linas Vepstas
Secondary Structure Assignment (Stride) -- Patrick Argos EMBL
Mesh Decimation (QSlim 2.0) -- Micheal Garland,  Univeristy of Illinois
Tiled Rendering (TR 1.3) -- Brian Paul
GLF font rendering library --  Roman Podobedov
PyMedia video encoder/decoder -- http://pymedia.org"""
        title="Python Molecule Viewer"
        #create a root and hide it
        try:
            from TkinterDnD2 import TkinterDnD
            root = TkinterDnD.Tk()
        except ImportError:
            from Tkinter import Tk
            root = Tk()    
        root.withdraw()
    
        from mglutil.splashregister.splashscreen import SplashScreen
        from mglutil.splashregister.about import About
        about = About(image_dir=image_dir, third_party=third_party,
                      path_data=path_data, title=title, version=version,
                      revision=__revision__, 
                      copyright=copyright, authors=authors, icon=icon)
        splash =  SplashScreen(about, noSplash=noSplash)
    
        from Pmv.moleculeViewer import MoleculeViewer

        mv = MoleculeViewer( logMode=logmode, customizer=customizer, master=root,
                             title=title, withShell= not interactive, verbose=False)
    #                        libraries=libraries)
        mv.help_about = about

        font = mv.GUI.ROOT.option_get('font', '*')
        mv.GUI.ROOT.option_add('*font', font)    

        try:
            import Vision
            mv.browseCommands('visionCommands', commands=('vision',), topCommand=0)
            mv.browseCommands('coarseMolSurfaceCommands', topCommand=0)
            if hasattr(mv,'vision') and mv.vision.ed is None:
                mv.vision(log=0)
        except ImportError:
            pass


        #show the application after it built
        splash.finish()
        root.deiconify()
        globals().update(locals())

        mv.GUI.VIEWER.suspendRedraw = True
        cwd = os.getcwd() 
        #mv._cwd differs from cwd when 'Startup Directory' userpref is set
        os.chdir(mv._cwd)
        if dmode is not None or cmode is not None:
            # save current list of commands run when a molecule is loaded
            addCmds = mv.getOnAddObjectCmd()
        # remove them
            if dmode is not None:
                for c in addCmds:
                    mv.removeOnAddObjectCmd(c[0])
                # set the mode
                setdmode(dmode, mv)
    
            if cmode is not None:
            # set the mode
                setcmode(cmode, mv)
    
        for a in args:
            if a[0]=='-':# skip all command line options
                continue
    
            elif (a[-10:]=='_pmvnet.py') or (a[-7:]=='_net.py'):  # Vision networks
                mv.browseCommands('visionCommands', commands=('vision',) )
                if mv.vision.ed is None:
                    mv.vision()
                mv.vision.ed.loadNetwork(a)
                if visionarg == 'run' or visionarg == 'once':
                    mv.vision.ed.currentNetwork.run()
    
            elif a[-3:]=='.py':     # command script
                print 'sourcing', a
                mv.source(a)
    
            elif a[-4:] in ['.pdb', '.pqr', 'pdbq', 'mol2', '.cif', '.gro'] or a[-5:]=='pdbqs' or a[-5:]=='pdbqt':
                mv.readMolecule(a)
                
            elif a in ['clear', 'tested', 'nighlty']:
                pass
            
            else:
                print 'WARNING: unable to process %s command line argument'%a
        if again:
            mv.source(".tmp.py")
        if dmode is not None or cmode is not None:
            # get current list of commands run when a molecule is loaded
            cmds = mv.getOnAddObjectCmd()
            # remove them
            for c in cmds:
                mv.removeOnAddObjectCmd(c[0])
            # restore original list of commands
            for c in addCmds:
                apply( mv.addOnAddObjectCmd, c )
    
        mv.GUI.VIEWER.suspendRedraw = False
        os.chdir(cwd)
        if visionarg != 'once':
            if interactive:
                sys.stdin = sys.__stdin__
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                import code
                mod = __import__('__main__')
                mod.__dict__.update({'self':mv})
                try: # hack to really exit code.interact 
                    code.interact( 'Pmv Interactive Shell', local=mod.__dict__)
                except:
                    pass
                mod.__dict__.pop('self')
            elif not die:
                mv.GUI.pyshell.interp.locals = globals()
                mv.GUI.ROOT.mainloop()
    
    except:
        import traceback
        traceback.print_exc()
        raw_input("hit enter to continue")
        import sys
        sys.exit(1)


FlagCheck = 1

CRITICAL_DEPENDENCIES =['numpy', 'Pmw', 'mglutil', 'ViewerFramework', 'MolKit', 'DejaVu', 'opengltk']
NONCRITICAL_DEPENDENCIES =['ZSI', 'geomutils', 'UTpackages', 'SpatialLogic', 'bhtree', 'sff', 'PyBabel', 'Volume', 'mslib', 'Vision', 'NetworkEditor', 'ARTK', 'PIL', 'symserv','QSlimLib', 'AutoDockTools', 'PyMead', 'isocontour','Support']
