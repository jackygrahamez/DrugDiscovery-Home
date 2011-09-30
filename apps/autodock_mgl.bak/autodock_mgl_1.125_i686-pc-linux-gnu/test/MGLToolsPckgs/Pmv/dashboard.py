from mglutil.gui.BasicWidgets.Tk.trees.TreeWithButtons import \
     ColumnDescriptor ,TreeWithButtons, NodeWithButtons
from MolKit.molecule import MolecularSystem
import Pmw, Tkinter

from MolKit.stringSelector import CompoundStringSelector

class MolFragTreeWithButtons(TreeWithButtons):
    """Each node in the tree has an object associated in the node's .object
attribute.  The objects are expected to have a .parent and a .children
attribute describing the hierarchy."""

    def __init__(self, master, root, vf=None, iconsManager=None,
                 idleRedraw=True, nodeHeight=20, **kw):
        # add a compound selector entry
        self.vf = vf
        kw['iconsManager'] = iconsManager
        kw['idleRedraw'] = idleRedraw
        kw['nodeHeight'] = nodeHeight
        TreeWithButtons.__init__( *(self, master, root), **kw )

        # add selector entry
        self.selector = CompoundStringSelector()
        w = self.interior()
        #self.selectorEntry = Pmw.EntryField(
        #    w, labelpos='w', label_text='Sel.:',
        #    entry_width=12, validate=None, command=self.selectFromString)
        self.selectorEntry = Pmw.ComboBox(
            w, labelpos='w', label_text='Sel.:',
            ##scrolledlist_items = self.vf.sets.keys(),
            selectioncommand=self.selectFromString)
        
        cid = self.create_window( 2, 2, window=self.selectorEntry,
                                  anchor='nw', width=100, height=25,
                                  tags=('ColHeadersWidgets',))

        self.selectorHelp = """This entry is used to select entities in the Tree via a Pmv compound selector.\nOnly expanded nodes will be selected.  Selected nodes are outlined with a\nyellow selection box.  When a shape is clicked for a selected node, the\ncommand is applied to all selected nodes. The syntax for a compound selector\nis a ';' separated list of expressions. Each expression is a ':' separated list of\nselectors applying at the various levels of the Tree.\nFor instance:
    :::CA selects all alpha carbon atoms
    :A::CA selects all CA in chain A
    ::CYS* selects all cysteines"""
        self.balloon.bind(self.selectorEntry, self.selectorHelp)
        # add backbone only widget
        self.bbmodevar = Tkinter.StringVar()
        self.bbmodevar.set("CMD")
        self.bbmode_menu = Pmw.ComboBox(
            w, selectioncommand= self.bbmodevar.set,
            scrolledlist_items = ['CMD', 'BB', 'SC', 'SC+CA', 'ALL'],
            entryfield_entry_width=4)
        self.bbmode_menu.selectitem('CMD')
        self.bbmodeHelp = """This option menu is used to specify whether commands should be applied to the
backbone atoms only (BB), the side chain atoms only (SC), the sidechain atoms
and CA atoms (SC+CA) or the full molecular fragment (ALL).
This setting can be overridden by each column (CMD)"""
        self.balloon.bind(self.bbmode_menu, self.bbmodeHelp)
        cid = self.create_window(104, 2, window=self.bbmode_menu, anchor='nw',
                                 tags=('ColHeadersWidgets',))

        
    def addColumnDescriptor(self, columnDescr):
        vf = columnDescr.vf
        # load Pmv commands
        for cmd, module, package in columnDescr.pmvCmdsToLoad:
            #print 'loading', cmd, module, package
            vf.browseCommands(module, commands=(cmd,), package='Pmv', log=0)

        # register interest in Pmv commands
        dashboardCmd = vf.dashboard
        for cmd in columnDescr.pmvCmdsToHandle:
            #print 'register', cmd, columnDescr.title
            vf.cmdsWithOnRun[vf.commands[cmd]] = [dashboardCmd]

        cmd = columnDescr.cmd

        if isinstance(cmd[0], str):
            columnDescr.cmd = (vf.commands[cmd[0]], cmd[1], {'callListener':False})
            #cmd[2]['callListener'] = False # prevents dashboard issues commands
                                            # from calling dashboard.onCmdRun
        if columnDescr.title is None:
            columnDescr.title = name

        TreeWithButtons.addColumnDescriptor(self, columnDescr)


    def expandParents(self, object):
        """Expand all parents of the node"""
        p = object.parent
        if not self.objectToNode.has_key(p):
            self.expandParents(p)
            
        self.objectToNode[p].expand()


    def selectFromString(self, value):
        #value = self.selectorEntry.getvalue()
        molFrag = self.selector.select(self.root.object.children, value,
                                       sets=self.vf.sets)
        for obj in molFrag[0]:
            try:
                node = self.objectToNode[obj]
            except KeyError:
                self.expandParents(obj)
                node = self.objectToNode[obj]
            node.select(only=False)


    def rightButtonClick(self, columnDescr, event):
        columnDescr.bbmodeOptMenu(event)



from MolKit.molecule import Atom, AtomSet, Molecule, MoleculeSet
from MolKit.protein import Chain, ChainSet, Residue, ResidueSet, Protein, ProteinSet

class MolFragNodeWithButtons(NodeWithButtons):


    def deleteMolecule(self, event=None):
        self.tree().vf.deleteMol(self.object)

    def postMoleculeMenu(self,event):
        menu = Tkinter.Menu(tearoff=False)
        menu.add_command(label='delete', command=self.deleteMolecule)
        menu.add_command(label='view source', command=self.viewSource)
        menu.add_command(label='dismiss')
        menu.post(event.x_root, event.y_root)
        self.menu = menu
        self.label.master.bind('<FocusOut>', self.cancelManu)

    def viewSource(self, event=None):
        self.object.parser.viewSource()
        
    def cancelManu(self, event=None):
        self.menu.unpost()
        
    def button3OnLabel(self, event=None):
        obj = self.object
        if isinstance(obj, MolecularSystem):
            self.tree().vf.readMolecule.guiCallback()
        elif isinstance(obj, Protein) or isinstance(obj, Molecule):
            self.postMoleculeMenu(event)
            
    
    def getIcon(self):
        """return node's icons"""
        iconsManager = self.tree().iconsManager
        object = self.object
        if isinstance(object, Atom):
            icon = iconsManager.get("atom.png", self.tree().master)
        elif isinstance(object, Residue):
            icon = iconsManager.get("residue.png", self.tree().master)
        elif isinstance(object, Chain):
            icon = iconsManager.get("chain.png", self.tree().master)
        elif isinstance(object, Molecule):
            icon = iconsManager.get("ms.png", self.tree().master)
        else:
            icon = None

        if icon:
            self.iconWidth = icon.width()
        else:
            self.iconWidth = 0
        return icon


    def getNodes(self, column):
        tree = self.tree()
        # return the objects associated with this node
        # handle the backbone, sidechain and both value for the command
        result = molFrag = self.object
        if isinstance(result, MolecularSystem):
            result = result.children

        bbmode = tree.bbmodevar.get()

        if bbmode=='CMD':
            #print 'Cmd setting found'
            bbmode = tree.columns[column].bbmode

        #print 'bbmode in getNode', column, bbmode
        if bbmode!='ALL':
            if result.findType(Chain)[0].isProteic():
                atoms = result.findType(Atom)
                if bbmode=='BB':
                    result = atoms.get('backbone')
                elif bbmode=='SC+CA':
                    result = atoms.get('sidechain')+atoms.get('CA')
                else:
                    result = atoms.get('sidechain')
                try:
                    return result.setClass([result])
                except KeyError:
                    return result

        if hasattr(result,'setClass') and result.setClass:
            return result.setClass([result])
        else:
            return result
        

    def getObjects(self, column):
        # return a list of objects associated with this node and possibly
        # other seleted nodes.  For selection we return a list for each type
        # ( i.e. Atom, Residue, etc..)
        # if the node is selected, collect object from all other selected nodes
        resultAtoms = AtomSet([])
        resultResidues = ResidueSet([])
        resultChains = ChainSet([])
        resultMolecules = MoleculeSet([])
        buttonValue = self.chkbtval[column]
        tree = self.tree()
        fill = tree.columns[column].buttonColors
        if self.isSelected:
            for node in tree.selectedNodes:
                if node in tree.displayedNodes:
                    tree.canvas.itemconfigure(node.chkbtid[column],
                                              fill=fill[buttonValue])
                node.chkbtval[column] = buttonValue
                result = node.getNodes(column)
                obj = result[0]
                if isinstance(obj, Atom):
                    resultAtoms += result
                elif isinstance(obj, Residue):
                    resultResidues += result
                elif isinstance(obj, Chain):
                    resultChains += result
                elif isinstance(obj, Molecule) or isinstance(obj, Protein):
                    resultMolecules += result
            result = []
            if len(resultAtoms): result.append(resultAtoms)
            if len(resultResidues): result.append(resultResidues)
            if len(resultChains): result.append(resultChains)
            if len(resultMolecules): result.append(resultMolecules)
            return result
        else:
            return [self.getNodes(column)]


#####################################################################
#
#  Column Descriptors for common PMV commands
#
#####################################################################
ColumnDescriptors = []


class MVColumnDescriptor(ColumnDescriptor):         

    def __init__(self, name, cmd, btype='checkbutton', buttonSize=(15,15),
                 buttonShape='circle', buttonColors = ['white', 'green'],
                 inherited=True, title=None, color='black',
                 objClassHasNoButton=None,
                 pmvCmdsToLoad=[], pmvCmdsToHandle=[]):

        ColumnDescriptor.__init__(
            self, name, cmd, btype=btype, buttonSize=buttonSize,
            buttonShape=buttonShape, buttonColors=buttonColors,
            inherited=inherited, title=title, color=color,
            objClassHasNoButton=objClassHasNoButton)

        self.pmvCmdsToHandle = pmvCmdsToHandle #list of Pmv commands that
           # this column wants to know about

        self.pmvCmdsToLoad = pmvCmdsToLoad #list of Pmv commands that
           # need to be loaded. Each one is (command, module, package)

        self.bbmode = 'ALL'
        self.bbmodeWidgetcid = None

    def onPmvCmd(self, command, column, *args, **kw):
        pass

    def setBBmode(self, value):
        assert value in ['BB', 'SC', 'SC+CA', 'ALL']
        self.bbmode = value
        if self.bbmodeWidgetcid:
            self.tree.delete(self.bbmodeWidgetcid)
        self.bbmodeWidgetcid = None
        
    def bbmodeOptMenu(self, event):
        self.bbmodeWidget = Pmw.ComboBox(
            self.tree.interior(), selectioncommand=self.setBBmode,
            scrolledlist_items=['BB', 'SC', 'SC+CA', 'ALL'],
            entryfield_entry_width=4)#, dropdown=0)
        self.bbmodeWidget.selectitem(self.bbmode)

        self.bbmodeWidgetcid = self.tree.create_window(event.x, event.y,
                                         window=self.bbmodeWidget, anchor='nw')


        
from MolKit.molecule import Molecule, MolecularSystem
from MolKit.protein import Residue, Chain

class MVvisibilityColumnDescriptor(MVColumnDescriptor):         

    def onPmvCmd(self, command, column, *args, **kw):
        print 'fugu2', column
        tree = self.tree
        for molName in args[0]: # loop over molecule names
            mol = self.vf.expandNodes(molName)
            #try:
            node = tree.objectToNode[mol[0]]
            print molName, mol, node, not kw['negate']
            node.set(column, not kw['negate'])
            #except KeyError:
            #    pass


    def isOn(self, node):
        try:
            return node.geomContainer.masterGeom.visible
        except AttributeError:
            return 1 # at first the master geom is not there yet

visibilityColDescr = MVvisibilityColumnDescriptor(
    'showMolecules', ('showMolecules', (), {}), title='Show/\nHide',
    buttonColors=['white', 'grey75'], inherited=False,
    buttonShape='rectangle', buttonSize=(10, 14), color='black',
    objClassHasNoButton = [Atom, Residue, Chain, MolecularSystem],
    pmvCmdsToHandle = ['showMolecules'],
    pmvCmdsToLoad = [('showMolecules', 'displayCommands', 'Pmv'),
                     ] )
ColumnDescriptors.append(visibilityColDescr)


class MVSelectColumnDescriptor(MVColumnDescriptor):         


    def __init__(self, name, cmd, btype='checkbutton', buttonSize=(15,15),
                 buttonShape='circle', buttonColors = ['white', 'green'],
                 inherited=True, title=None, color='black',
                 objClassHasNoButton=None,
                 pmvCmdsToLoad=[], pmvCmdsToHandle=[]):

        MVColumnDescriptor.__init__(
            self, name, cmd, btype=btype, buttonSize=buttonSize,
            buttonShape=buttonShape, buttonColors=buttonColors,
            inherited=inherited, title=title, color=color,
            objClassHasNoButton=objClassHasNoButton,
            pmvCmdsToLoad=pmvCmdsToLoad, pmvCmdsToHandle=pmvCmdsToHandle)

        self.selectionDict = {}


    def isOn(self, node):
        return self.selectionDict.has_key(node.object)


    def onPmvCmd(self, command, column, *args, **kw):
        # clear all selection buttons and check buttons corresponding to
        # the curent slection

        tree = self.tree
        selDict = {}

        n = tree.root
        n.chkbtval[column] = 0
        while 1:
            n = n.nextNode()
            if n is None: break
            n.chkbtval[column] = 0
        if self.vf.selection:
            selection = self.vf.getSelection()
        else:
            selection = []

        if command!=self.vf.clearSelection:
            val = 1
            for o in selection:
                selDict[o] = 1
        else:
            val = 0
        self.selectionDict = selDict
        
        # loop over visible nodes in tree
        for obj in selection:
            try:
                tree.objectToNode[obj].chkbtval[column] = val
            except KeyError:
                pass
        tree.redraw()



selectColDescr = MVSelectColumnDescriptor(
    'select', ('select', (), {}), title='Sel.',
    buttonColors=['white', '#FFEA60'], inherited=False,
    buttonShape='rectangle', buttonSize=(10, 14), color='magenta',
    pmvCmdsToHandle = ['select', 'clearSelection', 'selectFromString',
                       'invertSelection', 'selectInSphere',
                       'setSelectionLevel'],
    pmvCmdsToLoad = [('select', 'selectionCommands', 'Pmv'),
                     ('clearSelection', 'selectionCommands', 'Pmv'),
                     ('selectFromString', 'selectionCommands', 'Pmv'),
                     ('invertSelection', 'selectionCommands', 'Pmv'),
                     ('selectInSphere', 'selectionCommands', 'Pmv'),
                     ] )
ColumnDescriptors.append(selectColDescr)


class MVDisplayColumnDescriptor(MVColumnDescriptor):         

    def onPmvCmd(self, command, column, *args, **kw):

        if self.commandType=='button':
            return  # only check buttons not managed upon PMV command

        molFrag = args[0]
        negate = kw['negate']
        for o in molFrag:
            try:
                node = self.tree.objectToNode[o]
                if node.chkbtval[column]==negate: # if button needs to be checked
                    node.set(column, negate==False)
            except KeyError:
                #print 'Failed to find object in tree', o
                pass
   

displayLinesColDescr = MVDisplayColumnDescriptor(
    'display lines', ('displayLines', (), {}),
    buttonColors=['white', '#FF4F44'], title='Lines', color='#5B49BF',
    pmvCmdsToHandle = ['displayLines'],
    pmvCmdsToLoad = [('displayLines', 'displayCommands', 'Pmv')])
ColumnDescriptors.append(displayLinesColDescr)


displayCPKColDescr = MVDisplayColumnDescriptor(
    'display CPK', ('displayCPK', (), {}),
    buttonColors=['white', '#FF4F44'], title='CPK', color='#BF7C66',
    pmvCmdsToHandle = ['displayCPK'],
    pmvCmdsToLoad = [('displayCPK', 'displayCommands', 'Pmv')])
ColumnDescriptors.append(displayCPKColDescr)


displaySandBColDescr = MVDisplayColumnDescriptor(
    'display S&B', ('displaySticksAndBalls', (), {}),
    buttonColors=['white', '#FF4F44'], title='S&B', color='purple',
    pmvCmdsToHandle = ['displaySticksAndBalls'],
    pmvCmdsToLoad = [('displaySticksAndBalls', 'displayCommands', 'Pmv')])
ColumnDescriptors.append(displaySandBColDescr)



class RibbonColumnDescriptor(MVDisplayColumnDescriptor):

    # override Ribbon.optMenu_cb to display panel of extrude SS
    def optMenu_cb(self, node, column, event=None):
        cmd = self.vf.extrudeSecondaryStructure
        cmd.guiCallback()


displaySSColDescr = RibbonColumnDescriptor(
    'display Second.Struct.', ('displayExtrudedSS', (), {}),
    buttonColors=['white', '#FF4F44'], title='Rib.', color='#333333',
    pmvCmdsToHandle = ['displayExtrudedSS'],
    pmvCmdsToLoad = [('displayExtrudedSS', 'secondaryStructureCommands', 'Pmv')])


ColumnDescriptors.append(displaySSColDescr)


import types
class MSMSColumnDescriptor(MVDisplayColumnDescriptor):

    def __init__(self, name, cmd, btype='checkbutton', buttonSize=(15,15),
                 buttonShape='circle', buttonColors = ['white', 'green'],
                 inherited=True, title=None, color='black',
                 pmvCmdsToLoad=[], pmvCmdsToHandle=[]):

        MVDisplayColumnDescriptor.__init__(
            self, name, cmd, btype=btype, buttonSize=buttonSize,
            buttonShape=buttonShape, buttonColors=buttonColors,
            inherited=inherited, title=title, color=color,
            pmvCmdsToLoad=pmvCmdsToLoad, pmvCmdsToHandle=pmvCmdsToHandle)

        self.msmsDefaultValues = {} #cache used to decide if we re-compute


    def onPmvCmd(self, command, column, *args, **kw):

        #print "MSMS dashboard. onPmvCommand", command.name
        if command.name=='computeMSMS':
            self.msmsDefaultValues.update(
                self.vf.computeMSMS.getLastUsedValues())
        elif command.name=='displayMSMS':
            MVDisplayColumnDescriptor.onPmvCmd( *((self,command,column)+args),
                                                **kw)


    def execute(self, node, colInd):

        val = node.chkbtval[colInd]
        cmd = self.vf.computeMSMS
        defaultValues = cmd.getLastUsedValues()
        defaultValues = cmd.fixValues(defaultValues)

        oldDefaultValues = self.msmsDefaultValues
        recompute = False
        if len(oldDefaultValues)==0:
            recompute=True
        else:
            for k,v in oldDefaultValues.items():
                nv = defaultValues.get(k, None)
                if nv!=v:
                    recompute=True
                    break

        molat = {}
        for obj in node.getObjects(colInd):
            molecules, atmSets = self.vf.getNodesByMolecule(obj, Atom)
            for mol, atoms in zip(molecules, atmSets):
                try:
                    molat[mol] += atoms
                except KeyError:
                    molat[mol] = atoms

        for mol, atoms in molat.items():
            if not mol.geomContainer.geoms.has_key('MSMS-MOL'):
                recompute=True
            if len(defaultValues):
                if defaultValues['perMol']==0 and val:
                    recompute=True
                if type(defaultValues['surfName'])==types.TupleType:
                    defaultValues['surfName']=defaultValues['surfName'][0]

            if recompute:
                #print 'computing', defaultValues
                apply( self.vf.computeMSMS, (atoms,), defaultValues)
            else:
                #print 'DSIPLAY', defaultValues
                pmvcmd = self.vf.displayMSMS
                #defaultValues = pmvcmd.getLastUsedValues()
                defaultValues['callListener'] = False
                pmvcmd(atoms, negate= not val, callListener=False)
                if pmvcmd.lastUsedValues['default'].has_key('callListener'):
                    del pmvcmd.lastUsedValues['default']['callListener']

        if recompute:
            self.msmsDefaultValues.update(defaultValues)


    # override MSMScol.optMenu_cb
    def optMenu_cb(self, node, column, event=None):
        cmd = self.vf.computeMSMS
        values = cmd.showForm(posx=event.x_root, posy=event.y_root)
        if len(values)==0: return # Cancel was pressed
        values = cmd.fixValues(values)
        cmd.lastUsedValues['default'].update(values)
        node.buttonClick(column, val=1)


displayMSMSColDescr = MSMSColumnDescriptor(
    'compute/display Molecular Surface', ('displayMSMS', (), {}),
    buttonColors=['white', '#FF4F44'], title='MS', color='#333333',
    pmvCmdsToHandle = ['displayMSMS', 'computeMSMS'],
    pmvCmdsToLoad = [('displayMSMS', 'msmsCommands', 'Pmv'),
                     ('computeMSMS', 'msmsCommands', 'Pmv')])
ColumnDescriptors.append(displayMSMSColDescr)


class LabelColumnDescriptor(MVDisplayColumnDescriptor):

    # override labelCol.optMenu_cb
    def optMenu_cb(self, node, column, event=None):
        if node.object==self.vf.dashboard.system: return
        cmd, args, kw = self.tree.columns[column].cmd
        from MolKit.molecule import Atom, Molecule
        from MolKit.protein import Residue, Chain
        vi = self.vf.GUI.VIEWER
        molName = node.object.top.name
        if isinstance(node.object,Atom):
            geom=vi.FindObjectByName('root|%s|AtomLabels'%molName)
        elif isinstance(node.object,Residue):
            geom=vi.FindObjectByName('root|%s|ResidueLabels'%molName)
        elif isinstance(node.object,Chain):
            geom=vi.FindObjectByName('root|%s|ChainLabels'%molName)
        else:
            geom=vi.FindObjectByName('root|%s|ProteinLabels'%molName)

        geom.showOwnGui()

## ##             cmd, args, kw = self.tree.columns[column].cmd
## ##             from MolKit.molecule import Atom, Molecule
## ##             from MolKit.protein import Residue, Chain
## ##             if isinstance(node.object,Atom):
## ##                 tag = 'Atom'
## ##             elif isinstance(node.object,Residue):
## ##                 tag = 'Residue'
## ##             elif isinstance(node.object,Chain):
## ##                 tag = 'Chain'
## ##             else:
## ##                 tag = 'Molecule'
## ##             cmd.update_cb(tag, force=True)
## ##             values = cmd.showForm()
## ##             if values.has_key('level'):
## ##                 del values['level']
## ##             if values.has_key('display'):
## ##                 del values['display']
## ##             cmd.lastUsedValues['default'].update(values)
    
labelColDescr = LabelColumnDescriptor(
    'label', ('labelByProperty', (), {'properties':['name']}),
    buttonColors=['white', 'cyan'], buttonShape='square',
    buttonSize=(15,15), inherited=False, title='Lab.', color='#268E23',
    pmvCmdsToHandle = ['labelByProperty'],
    pmvCmdsToLoad = [('labelByProperty', 'labelCommands', 'Pmv')])
ColumnDescriptors.append(labelColDescr)


colAtColDescr = MVColumnDescriptor(
    'color by atom types', ('colorByAtomType', (), {}),
    title='Atom', color='magenta',
    pmvCmdsToHandle = ['colorByAtomType'],
    pmvCmdsToLoad = [('colorByAtomType', 'colorCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colAtColDescr)


colMolColDescr = MVColumnDescriptor(
    'color by molecule', ('colorByMolecules', (), {}),
    title='Mol', color='#5B49BF',
    pmvCmdsToHandle = ['colorByMolecules'],
    pmvCmdsToLoad = [('colorByMolecules', 'colorCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colMolColDescr)


colChainColDescr = MVColumnDescriptor(
    'color by chains', ('colorByChains', (), {}),
    title='Chain', color='#BF7C66',
    pmvCmdsToHandle = ['colorByChains'],
    pmvCmdsToLoad = [('colorByChains', 'colorCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colChainColDescr)


colResRASColDescr = MVColumnDescriptor(
    'color by residue (RASMOL)', ('colorByResidueType', (), {}),
    title='RAS', color='purple',
    pmvCmdsToHandle = ['colorByResidueType'],
    pmvCmdsToLoad = [('colorByResidueType', 'colorCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colResRASColDescr)


colResSHAColDescr = MVColumnDescriptor(
    'color by residue (SHAPELY)', ('colorResiduesUsingShapely', (), {}),
    title='SHA', color='#333333',
    pmvCmdsToHandle = ['colorResiduesUsingShapely'],
    pmvCmdsToLoad = [('colorResiduesUsingShapely', 'colorCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colResSHAColDescr)


colDGColDescr = MVColumnDescriptor(
    'color by DG', ('colorAtomsUsingDG', (), {}),
    title='DG', color='#268E23',
    pmvCmdsToHandle = ['colorAtomsUsingDG'],
    pmvCmdsToLoad = [('colorAtomsUsingDG', 'colorCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colDGColDescr)


colInstColDescr = MVColumnDescriptor(
    'color by instance', ('colorByInstance', (), {}),
    title='Inst.', color='black',
    pmvCmdsToHandle = ['colorByInstance'],
    pmvCmdsToLoad = [('colorByInstance', 'colorCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colInstColDescr)


colSSColDescr = MVColumnDescriptor(
    'color by second. struct.', ('colorBySecondaryStructure', (), {}),
    title='Sec.\nStr.', color='magenta',
    pmvCmdsToHandle = ['colorBySecondaryStructure'],
    pmvCmdsToLoad = [('colorBySecondaryStructure',
                      'secondaryStructureCommands', 'Pmv')],
    btype='button', buttonShape='diamond', buttonSize=(18,18),
)
ColumnDescriptors.append(colInstColDescr)


## ColDescr = MVColumnDescriptor(
##     '', ('', (), {}),
##     title='', color='',
##     pmvCmdsToHandle = [''],
##     pmvCmdsToLoad = [('', 'colorCommands', 'Pmv')],
##     btype='button', buttonShape='diamond', buttonSize=(18,18),
## )
## ColumnDescriptors.append(ColDescr)


## cmds = [
##     ('color by atom types', 'Atom', 'colorByAtomType', (), {},
##      'magenta', 'colorCommands'),
##     ('color by molecule', 'Mol', 'colorByMolecules', (), {},
##      '#5B49BF', 'colorCommands'),

##     ('color by chains', 'Chain', 'colorByChains', (), {},
##      '#BF7C66', 'colorCommands'),
##     ('color by residue (RASMOL)', 'RAS',
##      'colorByResidueType', (), {}, 'purple', 'colorCommands'), 

##     ('color by residue (SHAPELY)', 'SHA',
##      'colorResiduesUsingShapely', (), {}, '#333333', 'colorCommands'),
##     ('color by DG', 'DG', 'colorAtomsUsingDG',(), {}, '#268E23',
##      'colorCommands'),
##     ('color by instance', 'Inst.', 'colorByInstance', (), {},
##      'black', 'colorCommands'),
##     ('color by second. struct.', 'Sec.\nStr.',
##      'colorBySecondaryStructure', (), {}, 'magenta',
##      'secondaryStructureCommands'),
## ]

## for name, title, cmd, args, opt, color, mod in cmds:
##     descr = MVColumnDescriptor(
##         name, (cmd, args, opt), title=title, color=color,
##         btype='button', buttonShape='diamond', buttonSize=(18,18),
##         pmvCmdsToHandle = [cmd],
##         pmvCmdsToLoad = [(cmd, mod, 'Pmv')]
##         )
##     ColumnDescriptors.append(descr)

def loadAllColunms(mv):
    # adding columns to dashboard
    mv.dashboardSuspendRedraw(True)

    mv.addDashboardCmd(visibilityColDescr, log=0)
    mv.addDashboardCmd(selectColDescr, log=0)
    mv.addDashboardCmd(displayLinesColDescr, log=0)
    mv.addDashboardCmd(displayCPKColDescr, log=0)
    mv.addDashboardCmd(displaySandBColDescr, log=0)
    mv.addDashboardCmd(displaySSColDescr, log=0)
    mv.addDashboardCmd(displayMSMSColDescr, log=0)
    mv.addDashboardCmd(labelColDescr, log=0)
    mv.addDashboardCmd(colAtColDescr, log=0)
    mv.addDashboardCmd(colMolColDescr, log=0)
    mv.addDashboardCmd(colChainColDescr, log=0)
    mv.addDashboardCmd(colResRASColDescr, log=0)
    mv.addDashboardCmd(colResSHAColDescr, log=0)
    mv.addDashboardCmd(colDGColDescr, log=0)
    mv.addDashboardCmd(colSSColDescr, log=0)
    mv.addDashboardCmd(colInstColDescr, log=0)

    mv.dashboardSuspendRedraw(False)


def moveTreeToWidget(oldtree, master):
    # save columns
    columns = oldtree.columns

    # get handle to root node
    rootnode = oldtree.root

    # get handle to tree's objectToNode dict
    objToNode = oldtree.objectToNode
    selectedNodes = oldtree.selectedNodes
    
    # destroy docked tree
    oldtree.undisplay()
    oldtree.destroy()

    # create new tree
    tree = oldtree.__class__(master, rootnode, selectionMode='multiple')

    # change all references to Tree
    oldtree.reparentNodes(tree)

    tree.selectedNodes = selectedNodes
    tree.objectToNode = objToNode
    
    # put the columns back. This needs to be done by hand
    # because addColumnDescriptor appends a chkbtval and resets nodes
    tree.columns = columns
    tree.nbCol = len(columns)
    for i,c in enumerate(columns):
        tree.createColHeader(c, i)
        c.tree = tree

    tree.pack(expand=1, fill="both")
    tree.updateTreeHeight()
    return tree
