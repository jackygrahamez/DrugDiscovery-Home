## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

#############################################################################
#
# Author: Michel F. SANNER
#
# Copyright: M. Sanner TSRI 2000
#
#############################################################################

# $Header: /opt/cvs/python/packages/share1.5/Pmv/moleculeViewer.py,v 1.142 2008/06/04 23:24:46 rhuey Exp $

#
# $Id: moleculeViewer.py,v 1.142 2008/06/04 23:24:46 rhuey Exp $
#

from MolKit.molecule import Atom, AtomSet, BondSet, Molecule , MoleculeSet
from MolKit.protein import Protein, ProteinSet, Residue, Chain, ResidueSet
from MolKit.stringSelector import CompoundStringSelector
from DejaVu.Geom import Geom
from ViewerFramework.VF import ViewerFramework, GeomContainer
from DejaVu.IndexedPolylines import IndexedPolylines
from DejaVu.Spheres import Spheres
from DejaVu.Points import CrossSet
from DejaVu.Cylinders import Cylinders
from Pmv.mvCommand import MVInteractiveCmdCaller
from mglutil.util.packageFilePath import getResourceFolderWithVersion, findFilePath
from mglutil.util.recentFiles import RecentFiles
import thread
from types import StringType, ListType
import Pmw
import os
from numpy.oldnumeric import array, fabs, maximum
from string import find, replace, split
from MolKit.tree import TreeNode, TreeNodeSet

from mglutil.util.packageFilePath import findFilePath
ICONPATH = findFilePath('Icons', 'Pmv')

class MolGeomContainer(GeomContainer):
    """
    Class to hold geometries used to represent molecules in a viewer.
    An instance of such a class called geomContainer is added to each Molecule
    as it is loaded into a Viewer
    """
    def __init__(self, mol, viewer):
        """constructor of the geometry container"""

        GeomContainer.__init__(self)

        self.mol = mol
        mol.geomContainer = self

        ## Dictionary of AtomSets used to track which atoms are currently
        ## each mode
        self.atoms = {}

        ## Dictionary of function to be called to expand an atomic
        ## property to the corresponding vertices in a geometry
        ## The function has to accept 4 arguments: a geometry name,
        ## a list of atoms,  the name of the property and an optional argument
        ## the propIndex default is None, specifying the index of the property
        ## when needed.
        ## the key is the geometry name
        self.atomPropToVertices = {}

        
        ## Dictionary of function to be called to convert a vertex into an atom
        ## if no function is registered, used default (1vertex to 1atom)
        ## mapping
        ## if None is registered: this geometry cannot represent atoms
        ## else, call the function registered for this geometry
        self.geomPickToAtoms = {}

        ## Dictionary of function to be called when a part into a bond
        ## if no function is registered, used default (1vertex to 1bond)
        ## mapping
        ## if None is registered: this geometry cannot represent bonds
        ## else, call the function registered for this geometry
        self.geomPickToBonds = {}

        ## this set of coordinates should really be shared by all geometries
        self.allCoords = mol.allAtoms.coords

        if viewer.hasGui:
            self.VIEWER = viewer.GUI.VIEWER
            # master Geometry
            self.masterGeom = Geom(mol.name, shape=(0,0), 
                                    pickable=0, protected=True)
            self.masterGeom.isScalable = 0
            self.geoms['master'] = self.masterGeom
            self.masterGeom.replace = True
            self.VIEWER.AddObject( self.masterGeom )

            # selection Geometry
            if viewer.viewSelectionIcon=='cross':
                self.geoms['selectionSpheres'] = CrossSet(
                    'selection', shape=(0,3), materials=((1.0, 1.0, 0.),),
                    lineWidth=2, inheritMaterial=0, protected=True)
            elif viewer.viewSelectionIcon=='labels':
                from DejaVu.glfLabels import GlfLabels
                self.geoms['selectionSpheres'] = GlfLabels(
                    'selection', shape=(0,3), 
                    font='times_new1.glf',
                    bilboard=True,
                    fontScales=(.5,.5,.5),
                    materials=((1.0, 1.0, 0.),), 
                    inheritMaterial=0, 
                    protected=True)
            else:
                self.geoms['selectionSpheres'] = Spheres(
                    'selection', shape=(0,3), radii=0.3, quality = 3, 
                    materials = ((1.0, 1.0, 0.),), inheritMaterial=0, protected=True)
            self.geoms['selectionSpheres'].pickable=0
            self.VIEWER.AddObject(self.geoms['selectionSpheres'],
                                      parent=self.masterGeom, redo=0 )


    def addGeom(self, geom, parent=None, redo=False):
        # add geometry to to geomContainer, create atom set and set pointer
        # from geom to molecule
        
        GeomContainer.addGeom(self, geom, parent, redo)
        self.atoms[geom.name]=AtomSet([])
        # FIXME we should use a weakreference to mol here
        geom.mol = self.mol  #need for backtracking picking


    def getGeomColor(self, geomName):
        # build a list of colors for a geometry from the atom's colors
        if self.atomPropToVertices.has_key(geomName):
            func = self.atomPropToVertices[geomName]
            geom = self.geoms[geomName]
            atms = self.atoms[geomName]
            col = func(geom, atms, 'colors', propIndex=geomName)

        else:
            if geomName in self.atoms.keys():
                col = map(lambda x, geomName=geomName: x.colors[geomName],
                          self.atoms[geomName])
            else:
                return

        if col is not None:
            colarray = array(col, 'f')
            diff = colarray - colarray[0]
            maxi = maximum.reduce(fabs(diff.ravel()))
            if maxi==0:
                return [colarray[0].tolist()]
            else:
                return col


    def updateColors(self, geomName=[], updateOpacity=0):
        for name in geomName:
            if geomName=='master': continue
            if geomName=='selectionSpheres': continue
            if self.atoms.has_key(name) and len(self.atoms[name])==0: continue 
            col = self.getGeomColor(name)

            if updateOpacity:
                self.geoms[name].Set( materials = col, redo=1,
                                      tagModified=False)
                opac = self.getGeomOpacity(name)
            else: opac = None
            
            if col is not None and opac is not None:
                self.geoms[name].Set( materials=col, opacity=opac, redo=1,
                                      tagModified=False)
            elif col is not None:
                self.geoms[name].Set( materials=col, redo=1, tagModified=False)
            elif opac is not None:
                self.geoms[name].Set( opacity=opac, redo=1, tagModified=False)


    def getGeomOpacity(self, geomName):
        if self.atomPropToVertices.has_key(geomName):
            func = self.atomPropToVertices[geomName]
            geom = self.geoms[geomName]
            atms = self.atoms[geomName]
            col = func(geom, atms, 'opacities', propIndex = geomName)
        else:
            if geomName in self.atoms.keys():
                col = map(lambda x, geomName=geomName: x.opacities[geomName],
                              self.atoms[geomName])
                
            else:
                return
        if col is not None:
            colarray = array(col, 'f')
            diff = colarray - colarray[0]
            maxi = maximum.reduce(fabs(diff.ravel()))
            if maxi==0:
                return colarray[0]
            else:
                return col


    def updateOpacity(self, geomName=[]):
        for name in geomName:
            if geomName=='master': continue
            if geomName=='selectionSpheres': continue
            if len(self.atoms[name])==0: continue
            col = self.getGeomColor(name)
            if col:
                col = array(col, 'f')
                self.geoms[name].Set( materials = col, redo=1,
                                      tagModified=False)


from MolKit.molecule import Molecule, MoleculeSet
from ViewerFramework.VFCommand import Command, CommandGUI
import Tkinter

class MoleculeViewer(ViewerFramework):
    """
    package    : Pmv
    module     : moleculeViewer
    class      : MoleculeViewer
    description:
       Class derived from the ViewerFramework base class. It provides a 3D
       molecular viewer.
    """
    

    def getSelLev(self):
        return self.selection.elementType


    def setSelLev(self, value):
        if value==Protein: value = Molecule
        assert value in [Molecule, Chain, Residue, Atom]
        self.setSelectionLevel(value)

    selectionLevel = property(getSelLev, setSelLev)

    def __init__(self, title="Molecule Viewer", logMode='no',
                 libraries=[], gui=1, resourceFile = '_pmvrc',
                 customizer = None, master=None, guiVisible=1,
                 withShell=1, verbose=True, trapExceptions=True):
        """
        * title:
          string used as a title. 
        * logMode:
          string specifying the mode of logging of mv.
            'no': for no loging of commands at all
            'overwrite': the log files overwrite the one from the previous
                         session the log files = mvAll.log.py
            'unique': the log file name include the date and time

        * libraries:
          list of the Python packages containing modules and commands
          that can be loaded in the application. Such a package needs the
          following files : cmdlib.py and modlib.py
        * gui :
          Flag specifying whether or not to run the application with a gui.
        * resourceFile:
          file sourced at startup and where userpreference  made as default
          are saved (default: '.pmvrc')
        * customizer :
          file when specified is sourced at startup instead of the resourceFile
        * master:
          can be specified to run PMV withing another GUI application.
        * guiVisible:
          Flag to specify whether or not to show the GUI.
        - trapExceptions should be set to False when creating a ViewerFramework
          for testing, such that exception are seen by the testing framework
        """
        libraries = ['Pmv', 'Volume','AutoDockTools'] + libraries
        _pmvrc = Find_pmvrc(resourceFile)
        if _pmvrc:
            resourceFile = _pmvrc
        if withShell:
            from traceback import print_exception
            
            def print_exception_modified(etype, value, tb, limit=None, file=None):
                """
                Modified version of traceback.print_exception
                Deiconifies pyshell when Traceback is printed
                """
                print_exception(etype, value, tb, limit, file)
                if hasattr(self, 'GUI'):
                    self.GUI.pyshell.top.deiconify()
                if not 'Pmv' in tb.tb_frame.f_code.co_filename:
                    return
                if etype == ImportError:
                    if hasattr(value,'message'):
                        package = value.message.split()[-1]
                        print "Please install " +package + " to fix this problem."
                elif etype == AssertionError:
                    pass
                else:
                    print "Please include this Traceback in your bug report. Help --> Report a Bug in PMV/ADT."
            import traceback 
            
            traceback.print_exception = print_exception_modified
        ViewerFramework.__init__(self, title, logMode, libraries, gui,
                                 resourceFile, master=master,
                                 guiVisible=guiVisible, withShell=withShell,
                                 verbose=verbose, trapExceptions=trapExceptions)
        #if sys.platform == 'win32': #this needed to account for camera size
        #    geometry = '%dx%d+%d+%d' % (800,600, 30, 30)
        #else:
        #    geometry = '%dx%d+%d+%d' % (800,200, 30, 30)    
        #self.GUI.ROOT.geometry(geometry)

        # Establish interface to Visual Programming environment.
        if self.visionAPI is not None:
            # add Molecule, Pmv, Viewer to lookup table
            from Pmv.VisionInterface.PmvNodes import PmvMolecule, PmvNode, \
                 PmvViewer, PmvSetNode, PmvVolume
            self.visionAPI.addToLookup(Protein, PmvMolecule, "Molecules")
            self.visionAPI.addToLookup(MoleculeViewer, PmvNode, "PMV")
            from DejaVu import Viewer
            self.visionAPI.addToLookup(Viewer, PmvViewer, "PMV")
            self.visionAPI.addToLookup(TreeNodeSet, PmvSetNode, "Sets")

            # Note: Molecules are added to the interface in addMolecule() below
            
            # put Pmv instance into list of objects to be added to Vision
            self.visionAPI.add(self, "Pmv", kw={
                'vf':self,
                'constrkw':{'vf':'masterNet.editor.vf'} } )
            # put Pmv Viewer instance in list of objects to be added to Vision
            if self.hasGui:
                self.visionAPI.add(self.GUI.VIEWER, "Pmv Viewer", kw={
                'viewer':self.GUI.VIEWER,
                'constrkw':{'viewer':'masterNet.editor.vf.GUI.VIEWER'} } )
            
        self.selection = MoleculeSet()  # store current selection
        # replace interactive command caller by MVInteractiveCmdCaller
        # we need the ICmdCaller even if there is no GUI because it has
        # the level variable used byu selection commands
        self.ICmdCaller = MVInteractiveCmdCaller( self )
        from mvCommand import MVSetIcomLevel
        self.addCommand( MVSetIcomLevel(), 'setIcomLevel', None )
        from mvCommand import MVSetSelectionLevel, MVSetSelectionLevelGUI
        self.addCommand( MVSetSelectionLevel(), 'setSelectionLevel',  MVSetSelectionLevelGUI)

        self.setSelectionLevel(Molecule, topCommand = 0) #should this be Protein?
        from Pmv.displayCommands import BindGeomToMolecularFragment
        from Pmv.displayCommands import BindGeomToMolecularFragmentGUI

        self.addCommand( BindGeomToMolecularFragment(),
                         'bindGeomToMolecularFragment',
                         BindGeomToMolecularFragmentGUI )

#        if self.hasGui:
#            from Pmv.mvCommand import MVPrintNodeNames, MVCenterOnNodes
#            self.addCommand( MVPrintNodeNames(), 'printNodeNames ', None )
#            self.addCommand( MVCenterOnNodes(), 'centerOnNodes', None )

            # load out default interactive command which prints out object
            # names
            #self.ICmdCaller.setCommands( self.printNodeNames )

        self.ICmdCaller.go()
        self.addMVBasicMenus()

        # load out default interactive command
        self.ICmdCaller.setCommands( self.printNodeNames, modifier=None )
        self.ICmdCaller.setCommands( self.select, modifier='Shift_L' )
        self.ICmdCaller.setCommands( self.centerOnNodes, modifier='Control_L' )
        self.ICmdCaller.setCommands( self.deselect, modifier='Alt_L' )

        #self.setIcomLevel(Molecule, topCommand = 0)
        self.setIcomLevel(Atom, topCommand = 0)

        self.Mols = MoleculeSet() # store the molecules read in
        self.objects = self.Mols
        from MolKit.sets import Sets
        self.sets = Sets()  # store user-defined sets in this dict

        # lock needs to be acquired before volume can be added
        self.volumesLock = thread.allocate_lock()

        self.Vols = [] # list of Grid3D objects storing volumetric data
        if self.visionAPI is not None:
            from Volume.Grid3D import Grid3D
            self.visionAPI.addToLookup(Grid3D, PmvVolume, "Volumes")

        self.allAtoms = AtomSet() # set of all atoms (across molecules)

        #if self.hasGui:
        #    from Pmv.controlPanelCommands import ControlPanel,ControlPanel_GUI
        #    self.addCommand(ControlPanel(), "controlPanel",ControlPanel_GUI)
        choices = ['caseSensitive', 'caseInsensitive',
                   'caseInsensWithEscapedChars']

        self.userpref.add('selectStringMatchMode', 'caseSensitive', validValues=choices,
                          doc = """When set to caseSensitive the string match
mode will be case sensitive the other possibility is to be case insensitive or
case insensitive with escaped characters.
""")
        choices = [1,0]
        self.userpref.add('showSelectionSpheres', 1, validValues=choices,
                          doc = """When set to 1 the selection visual feedback
which are the little yellow crosses will be displayed.""")
        choices = [1,0]
        self.userpref.add('raiseExceptionForMissingKey', 1, validValues=choices,
                          callbackFunc = [self.setRaiseException],
                          doc = """When set to 1 an exception will be raised
is a a key is not found in a dictionnary.
""")
        
        choices = [1, 0]
        self.userpref.add('expandNodeLogString', 0, validValues=choices,
                          doc = """When set to 1 the log string representing
the node argument of a doit will be expanded to the full name of each element
of the TreeNodeSet, when set to 0 the log string representing the node argument
of a doit will be 'self.getSelection()'. In the last case the command log will
depend on the current selection.""")

        # overwrite firstObject only with firstMoleculeOnly
        self.userpref['centerScene']['validValues'][0] = 'firstMoleculeOnly'
        self.userpref.set('centerScene', 'firstMoleculeOnly')
        
        choices = ['yes','no']
        self.userpref.add('useDepthCueing', 'yes', validValues=choices,
                          doc = """ When set to 'yes' the depthCueing is
turned on by default""")

        doc = """When set to yes a warning message is displayed when an empty
selection is about to be expanded to all the  molecules loaded in the 
application"""
        self.userpref.add('warnOnEmptySelection', 'no', validValues=choices, doc=doc)

        if self.hasGui:
            self.GUI.VIEWER.suspendRedraw = True
    
            self.GUI.drop_cb = self.drop_cb
            self.GUI.pickLabel.bind("<Button-1>",self.setSelectionLevel.guiCallback)
            if self.userpref['useDepthCueing']['value']=='yes':
                self.GUI.VIEWER.currentCamera.fog.Set(enabled=1,
                                                      tagModified=False)

            if title != 'AutoDockTools':
                toolbarDict = {}
                toolbarDict['name'] = 'ADT'
                toolbarDict['type'] = 'Checkbutton'
                toolbarDict['icon1'] = 'adt.png'
                toolbarDict['balloonhelp'] = 'AutoDock Tools'
                toolbarDict['icon_dir'] = ICONPATH
                toolbarDict['index'] = 7
                toolbarDict['cmdcb'] = self.Add_ADT
                toolbarDict['variable'] = None
                self.GUI.toolbarList.append(toolbarDict)
            self.GUI.configureToolBar(self.GUI.iconsize)
            # overwrite unsollicited picking with a version that prints atom names
            #self.GUI.VIEWER.RemovePickingCallback("unsolicitedPick")
            #self.GUI.VIEWER.AddPickingCallback(self.unsolicitedPick)

            top = self.GUI.ROOT.winfo_toplevel()
            geom = top.geometry()
            geom = geom.split('x')
            self.GUI.menuBars['Toolbar']._frame.update_idletasks()
            winfo_width = self.GUI.menuBars['Toolbar']._frame.winfo_width()        
            if int(geom[0]) < winfo_width + 10:
                geom[0] = str(winfo_width + 10)
            top.geometry(geom[0]+'x'+geom[1])   
            if not trapExceptions and customizer == './.empty':
                top.update_idletasks()
                top.deiconify()  
                #self.GUI.vwrCanvasFloating.deiconify()
                self.GUI.naturalSize()
            from Pmv.updateCommands import Update, UpdateGUI
            self.addCommand( Update(), 'update', UpdateGUI )
    
            from Pmv.aboutCommands import About, AboutGUI
            self.addCommand( About(), 'about', AboutGUI )
    
            self.GUI.VIEWER.suspendRedraw = False
            self.browseCommands('deleteCommands',package='Pmv', topCommand=0)
            self.GUI.ROOT.bind('<Delete>', self.deleteAtomSet.guiCallback)
            self.GUI.vwrCanvasFloating.bind('<Delete>', self.deleteAtomSet.guiCallback)
            self.browseCommands ('dashboardCommands', package='Pmv', topCommand=0)
        self.customize(customizer)
        if self.hasGui:
            try:
                import grid3DCommands
                self.browseCommands("grid3DCommands",package="Pmv", topCommand=0)
            except ImportError:
                print "UTpackages are not installed. Disabling grid3DCommands..."
        
        rcFile = getResourceFolderWithVersion()
        if rcFile:
            rcFile += os.sep + 'Pmv' + os.sep + "recent.pkl"
            
        if self.hasGui:
            fileMenu = self.GUI.menuBars['menuRoot'].menubuttons['File'].menu
    
            self.recentFiles = RecentFiles(self, fileMenu, filePath=rcFile, 
                                           menuLabel = 'Recent Files')
            try:
                from DejaVu.Camera import RecordableCamera
                if isinstance(self.GUI.VIEWER.cameras[0], RecordableCamera):
                    from Pmv.videoCommands import VideoCommand, VideoCommandGUI 
                    self.addCommand(VideoCommand(), 'videoCommand', VideoCommandGUI)
            except:
                pass
                #print "Recordable camera is not available"
            if len(self.dashboard.tree.columns)==0:
                # this warning is wrong, it appears during test_pmvscript
                #print "WARNING: update your _pmvrc file to load the dashboard commands"
                from Pmv.dashboard import loadAllColunms
                loadAllColunms(self)


    def drop_cb(self, files):
        for file in files:
            self.readMolecule(file)
        
    #def getSelectionLevel(self):
    #    return self.selection.elementType
            

    def getMolFromName(self, name):
        mols = filter(lambda x: x.name == name, self.Mols)
        if len(mols):
            mol = mols[0]
        else:
            mol = None
        return mol

    def setRaiseException(self, name, oldval, val):
        import MolKit.molecule
        MolKit.molecule.raiseExceptionForMissingKey = val


    def unsolicitedPick(self, pick):
        """treat an unsollicited picking event"""
        
        if pick is None: return
        vi = self.GUI.VIEWER
        if vi.isShift() or vi.isControl():
            vi.unsolicitedPick(pick)
        else:
            atom = self.findPickedAtoms(pick)
            if atom:
                level = self.ICmdCaller.level.value
                if level == Molecule: level = Protein
                node = atom.findType(level)
                for n in node:
                    self.message( n.full_name() )


    def loadMoleculeIfNeeded(self, filename):
        """load a molecule only if it doesn't exist yet in Pmv, else it
        aborts silent"""

        if not os.path.exists(filename):
            print 'Error! %s not found!'%filename
            return
        
        # find what name would be
        name = os.path.split(filename)[-1]
        try:
            spl = split(name, '.')
        except:
            spl = [name]
        name = spl[0]

        # ask if name already used
        if self.Mols:
            for mol in self.Mols.data:
                if name == mol.name:
                    # break and return mol
                    return mol
        
        # else load molecule
        if not hasattr(self, 'readMolecule'):
            self.browseCommands(
                'fileCommands',
                commands=['readMolecule'], package='Pmv', topCommand=0)

        mol = self.readMolecule(filename)
        return mol
        
        
    def addMolecule(self, newmol, ask=1):
        """
        Add a molecule to this viewer
        """
        #IN ANY CASE: change any special characters in name to '-'

        from MolKit.molecule import Molecule
        if self.hasGui:
            Molecule.configureProgressBar = self.GUI.progressBarConf
            Molecule.updateProgressBar = self.GUI.progressBarUpd
        
        spChar=['?','*','.','$','#',':','-',',']        
##         spChar=['?','*','.','$','#',':','_',',']        
        for item in spChar:
            newmol.name = replace(newmol.name,item,'_')
##             newmol.name = replace(newmol.name,item,'-')
        if len(self.Mols) > 0:
            if newmol.name in self.Mols.name:
                if ask==1: 
                    from mglutil.gui.InputForm.Tk.gui import InputFormDescr
                    idf = self.ifd = InputFormDescr(title = '')
                    idf.append({'widgetType':Pmw.EntryField,
                                'name':'newmol',
                                'required':1,
                                'wcfg':{'labelpos':'w',
                                        'label_text':'New Name: ',
                                        'validate':None,
                                        'value':'%s-%d'%(newmol.name,
                                                         len(self.Mols))},
                                'gridcfg':{'sticky':'we'}})

                    vals = self.getUserInput(idf)
                    if len(vals)>0:
                        assert not vals['newmol'] in self.Mols.name
                        newmol.name = vals['newmol']
                    else:
                        return None
                else:
                    newmol.name='%s_%d'%(newmol.name,len(self.Mols))

        newmol.allAtoms.setStringRepr(newmol.full_name()+':::')
        
        # provide hook for progress bar
        # old code: newmol.allAtoms._bndIndex_ = range(len(newmol.allAtoms))

        allAtomsLen = len(newmol.allAtoms)
        if allAtomsLen == 0:
            import warnings
            warnings.warn("%s is empty molecule cannot add it to the viewer"%newmol.name)
            return None
        if self.hasGui:
            self.GUI.configureProgressBar(init=1, mode='increment',
                                      max=allAtomsLen,
                                      labeltext='add molecule to viewer')
        i = 0
        for a in newmol.allAtoms:
            a._bndIndex_ = i
            if self.hasGui:
                self.GUI.updateProgressBar()
            i = i + 1

        g = None
        if self.hasGui:
            g = MolGeomContainer( newmol, self )
        # addObject calls updateProgressBar on its own
        self.addObject('mol%s'%len(self.Mols), newmol, g)

        self.Mols.setStringRepr(self.Mols.full_name())

        # add object to visionAPI (to add them as nodes to Vision library)
        if self.visionAPI:
            self.visionAPI.add(newmol, newmol.name, kw={
                'molecule':newmol,
                'constrkw':{
                    'molecule':
                    'masterNet.editor.vf.expandNodes("%s")[0]'%newmol.name} } )

        self.allAtoms = self.allAtoms + newmol.allAtoms
        self.allAtoms.setStringRepr(self.Mols.full_name()+':::')
        
        #used by cpk command to decide whether or not to compute radii
        newmol.unitedRadii = None # set to None to force initial radii assignment
        return newmol


    def addVolume(self, name, grid):
        # FIXME we need to check for name unicity and have a repalcement policy

        #self.volumesLock.acquire()
        self.Vols.append(grid)
        grid.name = name
        #self.volumesLock.release()

        if self.visionAPI:
            self.visionAPI.add(grid, name, kw={
                'grid':grid,
                'constrkw':{
                    'grid':
                    'masterNet.editor.vf.gridFromName("%s")[0]'%grid.name} } )

    
    def getSelection(self):
        # FIXME why not return self.Mols always on empty selection ??
        # this should speed thing up
        #ICmdCallerLevel = self.ICmdCaller.level.value
        selLevel = self.selectionLevel

        if len(self.selection)==0:
            # empty selection
            if self.userpref['warnOnEmptySelection']['value']=='yes':
                if self.askOkCancelMsg('expand empty selection to all molecules?'):
                    #selection = self.Mols.findType(selLevel)#, uniq=1)
                    return self.Mols
                    #try:
                    #    selection = self.Mols.findType(selLevel)#, uniq=1)
                    #except:
                    #    if selLevel==Molecule:
                    #        selection = self.Mols.findType(Protein)
                    #return selection
                else:
                    #selection = self.Mols.findType(selLevel)#, uniq=1)
                    return self.Mols
                    #try:
                    #    selection = self.Mols.findType(selLevel)#, uniq=1)
                    #except:
                    #    if selLevel==Molecule:
                    #        selection = self.Mols.findType(Protein)
                    #return selection
            else:
                #selection = self.Mols.findType(selLevel)#, uniq=1)
                return self.Mols
                #try:
                #    selection = self.Mols.findType(selLevel)#, uniq=1)
                #except:
                #    if selLevel==Molecule:
                #        selection = self.Mols.findType(Protein)
                #return selection
                
        else:
            # not empty select
            #try:
            #    selection = self.selection.findType(selLevel, uniq=1)
            #except:
            #    if selLevel==Molecule:
            #        selection = self.selection.findType(Protein)
            return self.selection
            #selection = self.selection.findType(selLevel, uniq=1)
            #return selection

##             if self.userpref['warnOnEmptySelection']['value']=='yes':
##                 if self.askOkCancelMsg('expand empty selection to all molecules?'):
##                     selection = self.Mols.findType(selLevel)#, uniq=1)
##                     #try:
##                     #    selection = self.Mols.findType(selLevel)#, uniq=1)
##                     #except:
##                     #    if selLevel==Molecule:
##                     #        selection = self.Mols.findType(Protein)
##                     return selection
##                 else:
##                     selection = self.Mols.findType(selLevel)#, uniq=1)
##                     #try:
##                     #    selection = self.Mols.findType(selLevel)#, uniq=1)
##                     #except:
##                     #    if selLevel==Molecule:
##                     #        selection = self.Mols.findType(Protein)
##                     return selection
##             else:
##                 selection = self.Mols.findType(selLevel)#, uniq=1)
##                 #try:
##                 #    selection = self.Mols.findType(selLevel)#, uniq=1)
##                 #except:
##                 #    if selLevel==Molecule:
##                 #        selection = self.Mols.findType(Protein)
##                 return selection
                
##         else:
##             # not empty select
##             #try:
##             #    selection = self.selection.findType(selLevel, uniq=1)
##             #except:
##             #    if selLevel==Molecule:
##             #        selection = self.selection.findType(Protein)
##             selection = self.selection.findType(selLevel, uniq=1)
##             return selection
            

    def getItems(self, selString=""):
        """Takes a string and returns a TreeNodeSet
The string  can contain a series of set descriptors with operators
separated by / characters.  There is always a first set, followed by pairs of
operators and sets.  All sets have to describe nodes of the same level.
example:
    '1crn:::CA*/+/1crn:::O*' describes the union of all CA ans all O in 1crn
    '1crn:::CA*/+/1crn:::O*/-/1crn::TYR29:' 
"""
        assert type(selString)==StringType
        return self.expandNodes(selString)
            
        
    def expandNodes(self, nodes):
        """Takes nodes as string or TreeNode or TreeNodeSet and returns
a TreeNodeSet
If nodes is a string it can contain a series of set descriptors with operators
separated by / characters.  There is always a first set, followed by pairs of
operators and sets.  All sets ahve to describe nodes of the same level.

example:
    '1crn:::CA*/+/1crn:::O*' describes the union of all CA ans all O in 1crn
    '1crn:::CA*/+/1crn:::O*/-/1crn::TYR29:' 
"""
        if isinstance(nodes,TreeNode):
            result = nodes.setClass([nodes])
            result.setStringRepr(nodes.full_name())

        elif type(nodes)==StringType:
            stringRepr = nodes
            css = CompoundStringSelector()
            result = css.select(self.Mols, stringRepr)[0]
##            setsStrings = stringRepr.split('/')
##            getSet = self.Mols.NodesFromName
##            result = getSet(setsStrings[0])
##            for i in range(1, len(setsStrings), 2):
##                op = setsStrings[i]
##                arg = setsStrings[i+1]
##                if op=='|': # or
##                    result += getSet(arg)
##                elif op=='-': # subtract
##                    result -= getSet(arg)
##                elif op=='&': # intersection
##                    result &= getSet(arg)
##                elif op=='^': # xor
##                    result ^= getSet(arg)
##                elif op=='s': # sub select (i.e. select from previous result)
##                    result = result.get(arg)
##                else:
##                    raise ValueError, '%s bad operation in selection string'%op
##            result.setStringRepr(stringRepr)

        elif isinstance(nodes,TreeNodeSet):
            result = nodes
        else:
            raise ValueError, 'Could not expand nodes %s\n'%str(nodes)
        
        return result

        
    def getNodesByMolecule(self, nodes, nodeType=None):
        """ moleculeSet, [nodeSet, nodeSet] <- getNodesByMolecule(nodes, nodeType=None)
        nodes can be either: a string, a TreeNode or a TreeNodeSet.
        This method returns a molecule set and for each molecule a TreeNodeSet
        of the nodes belonging to this molecule.
        'nodeType' enables a desired type of nodes to be returned for each
        molecule
        """

        # special case list of complete molecules to be expanded to atoms
        # this also covers the case where nothing is selected
        if isinstance(nodes, MoleculeSet) or isinstance(nodes, ProteinSet):
            if nodeType is Atom:
                atms = []
                for mol in nodes:
                    atms.append(mol.allAtoms)
                return nodes, atms
            elif (nodeType is Protein) or (nodeType is Molecule):
                return nodes, nodes
        
        # if it is a string, get a bunch of nodes from the string
        if type(nodes)==StringType:
            nodes = self.expandNodes(nodes)

        assert issubclass(nodes.__class__, TreeNode) or \
               issubclass(nodes.__class__, TreeNodeSet)

        # if nodes is a single TreeNode make it a singleton TreeNodeSet
        if issubclass(nodes.__class__, TreeNode):
            nodes = nodes.setClass([nodes])
            nodes.setStringRepr(nodes.full_name())

        if len(nodes)==0: return MoleculeSet([]), []

        # catch the case when nodes is already a MoleculeSet
        if nodes.elementType in [Molecule, Protein]:
            molecules = nodes
        else: # get the set of molecules
            molecules = nodes.top.uniq()

        # build the set of nodes for each molecule
        nodeSets = []

        # find out the type of the nodes we want to return
        searchType=0
        if nodeType is None:
            Klass = nodes.elementType # class of objects in that set
        else:
            assert issubclass(nodeType, TreeNode)
            Klass = nodeType
            if Klass != nodes.elementType:
                searchType=1

        for mol in molecules:
            # get set of nodes for this molecule
            mol_nodes = nodes.get(lambda x, mol=mol: x.top==mol)

            # get the required types of nodes
            if searchType:
                if Klass == Atom and hasattr(mol_nodes, 'allAtoms'):
                    mol_nodes = mol_nodes.allAtoms
                else:
                    mol_nodes = mol_nodes.findType( Klass ).uniq()

            stringRepr = nodes.getStringRepr()
            if stringRepr:
                if ':' in stringRepr:
                    mol_nodes.setStringRepr(
                        mol.name+stringRepr[stringRepr.index(':'):])
                else:
                    mol_nodes.setStringRepr(stringRepr)

            nodeSets.append( mol_nodes )

        return molecules, nodeSets


    def addMVBasicMenus(self):
        from Pmv.selectionCommands import MVSelectCommand, MVDeSelectCommand
        from Pmv.mvCommand import MVPrintNodeNames, MVCenterOnNodes
        self.addCommand( MVPrintNodeNames(), 'printNodeNames' )
        self.addCommand( MVSelectCommand(), 'select' )
        self.addCommand( MVDeSelectCommand(), 'deselect' )
        self.addCommand( MVCenterOnNodes(), 'centerOnNodes' )


    def findPickedAtoms(self, pick):
        """
given a PickObject this function finds all corresponding atoms.
Each atom in the returned set has its attribute pickedInstances set to a list
of 2-tuples [(geom, instance),...].
"""

        allatoms = AtomSet( [] )
        # loop over object, i.e. geometry objects
        for obj, values in pick.hits.items():

            # build a list of vertices and list of instances
            instances = map(lambda x: x[1], values)
            vertInds = map(lambda x: x[0], values)

            # only geometry bound to molecules is packable in PMV
            if not hasattr(obj, 'mol') or len(vertInds)<1:
                continue

            # only vertices of geometry have a mapping to atoms
            # for other types we return an empty atom set
            if pick.type!='vertices':
                return allatoms

            g = obj.mol.geomContainer

            # convert vertex indices into atoms
            if g.geomPickToAtoms.has_key(obj.name):
                # the geometry obj has a function to convert to atoms
                # specified it he geomContainer[obj], e.g. MSMS surface
                func = g.geomPickToAtoms[obj.name]
                if func:
                    atList = func(obj, vertInds)
                else:
                    atlist = []
            else:
                # we assume a 1 to 1 mapping of vertices with atoms
                # e.g. the lines geometry
                atList = []
                allAtoms = g.atoms[obj.name]
                for i in vertInds:
                    atList.append(allAtoms[int(i)])

            # build a dict of atoms used to set the pickedAtomInstance
            # attribute for the last picking operation
            pickedAtoms = {}

            # update the pickedAtoms dict
            for i, atom in enumerate(atList):
                atomInstList = pickedAtoms.get(atom, None)
                if atomInstList:
                    atomInstList.append( (obj, instances[i]) )
                else:
                    pickedAtoms[atom] = [ (obj, instances[i]) ]

            # FIXME atoms might appear multiple times because they were picked
            # in several geometries OR be cause they correspond to different
            # instances.  In the first case (i.e. multiple geometries)
            # duplicates should be removed, in the latter (multiple instances)
            # duplicate should be kept
            #
            # Apparently we do not get duplication for multiple geoemtry objects!
            allatoms = allatoms + AtomSet( atList )

            # loop over picked atoms and write the instance list into the atom
            for atom, instances in pickedAtoms.items():
                atom.pickedInstances = instances

        #print allAtoms
        return allatoms


    def findPickedBonds(self, pick):
        """do a pick operation and return a 2-tuple holding (the picked bond,
        the picked geometry)"""

        allbonds = BondSet( [] )
        for o, val in pick.hits.items(): #loop over geometries
            # loop over list of (vertices, instance) (e.g. (45, [0,0,2,0]))
            for instvert in val:
                primInd = instvert[0]
                if not hasattr(o, 'mol'): continue
                g = o.mol.geomContainer
                if g.geomPickToBonds.has_key(o.name):
                    func = g.geomPickToBonds[o.name]
                    if func: allbonds = allbonds + func(o, primInd)
                else:
                    l = []
                    bonds = g.atoms[o.name].bonds[0]
                    for i in range(len(primInd)):
                        l.append(bonds[int(primInd[i])])
                    allbonds = allbonds + BondSet(l)

        return allbonds


    def transformedCoordinatesWithInstances(self, nodes):
        """ for a nodeset, this function returns transformed coordinates.
This function will use the pickedInstance attribute if found.
"""
        # nodes is a list of atoms, residues, chains, etc. where each member
        # has a pickedInstances attribute which is a list of 2-tuples
        # (object, [i,j,..])
        vt = []
        for node in nodes:
            #find all atoms and their coordinates
            coords = nodes.findType(Atom).coords
            if hasattr(node, 'pickedInstances'):
                # loop over the pickedInstances of this node
                for inst in node.pickedInstances:
                    geom, instance = inst # inst is a tuple (object, [i,j,..])
                    M = geom.GetMatrix(geom.LastParentBeforeRoot(), instance[1:])
                    for pt in coords:
                        ptx = M[0][0]*pt[0]+M[0][1]*pt[1]+M[0][2]*pt[2]+M[0][3]
                        pty = M[1][0]*pt[0]+M[1][1]*pt[1]+M[1][2]*pt[2]+M[1][3]
                        ptz = M[2][0]*pt[0]+M[2][1]*pt[1]+M[2][2]*pt[2]+M[2][3]
                        vt.append( (ptx, pty, ptz) )
            else:
                # no picking ==> no list of instances ==> use [0,0,0,...] 
                g = nodes[0].top.geomContainer.geoms['master']
                M = g.GetMatrix(g.LastParentBeforeRoot())
                for pt in coords:
                    ptx = M[0][0]*pt[0]+M[0][1]*pt[1]+M[0][2]*pt[2]+M[0][3]
                    pty = M[1][0]*pt[0]+M[1][1]*pt[1]+M[1][2]*pt[2]+M[1][3]
                    ptz = M[2][0]*pt[0]+M[2][1]*pt[1]+M[2][2]*pt[2]+M[2][3]
                    vt.append( (ptx, pty, ptz) )
                
        return vt
        
    def Add_ADT(self):
        """Adds AutoToolsBar"""
        if self.GUI.toolbarCheckbuttons['ADT']['Variable'].get():
            #if self.GUI.menuBars.has_key('AutoTools4Bar'):
            #    self.GUI.menuBars['AutoTools4Bar'].pack(fill='x',expand=1)
            if hasattr(self.GUI, 'currentADTBar'):
                self.GUI.menuBars[self.GUI.currentADTBar].pack(fill='x',expand=1)
            else:
                self.browseCommands('autotors4Commands', commands = None, 
                                        package = 'AutoDockTools')
                self.browseCommands('autoflex4Commands', commands = None, 
                                     package = 'AutoDockTools')
                self.browseCommands('autogpf4Commands', commands = None, 
                                        package = 'AutoDockTools')
                self.browseCommands('autodpf4Commands', commands = None, 
                                        package = 'AutoDockTools')
                self.browseCommands('autostart4Commands', commands = None, 
                                        package = 'AutoDockTools')
                self.browseCommands('autoanalyze4Commands', commands = None, 
                                        package = 'AutoDockTools')
                self.GUI.currentADTBar = 'AutoTools4Bar'
                from AutoDockTools import setADTmode
                setADTmode('AD4.0', self)
                self.GUI.adt4ModeLabel.bind("<Double-Button-1>", self.ADTSetMode.guiCallback)
        else:
            #self.GUI.menuBars['AutoToolsBar'].pack_forget()
            self.GUI.menuBars[self.GUI.currentADTBar].pack_forget()

def Find_pmvrc(resourceFile):
    """
    This function tries to find resource file for Pmv in the User Home folder. 
    If it can't find one, it will copy it from Pmv._pmvrc
    """
    import mglutil
    try:            
        reload(mglutil) # this is needed for updates
    except RuntimeError, e:
        print "# this is needed for updates: unable to reload mglutil\n", e
    lResourceFolderWithVersion = getResourceFolderWithVersion()
    if lResourceFolderWithVersion is not None:
        pmvrcFolder = lResourceFolderWithVersion + os.sep + 'Pmv'
        if not os.path.exists(pmvrcFolder):
            os.mkdir(pmvrcFolder)
        pmvrcFile = pmvrcFolder + os.sep + resourceFile
        if not os.path.exists(pmvrcFile):
            file_out = open(pmvrcFile,'w')
            import Pmv
            file_in = open(Pmv.__path__[0] + os.sep + resourceFile )
            file_out.write(file_in.read())
        return pmvrcFile
    else:
        return None

if __name__ == '__main__':
    from Pmv.fileCommands import PDBQReader, PDBReader, PQRReader
    import pdb
    mv = MoleculeViewer(logMode='no')
    import pdb
