import Tkinter
from Pmv.mvCommand import MVCommand, MVCommandGUI

# TODO
# add spline command column
# adding the columns should be commands

from Pmv.dashboard import MolFragTreeWithButtons, MolFragNodeWithButtons, \
     moveTreeToWidget
from mglutil.gui.BasicWidgets.Tk.trees.TreeWithButtons import \
     ColumnDescriptor

class FloatDashboard(MVCommand):
    """Command to move the dashboard widget into its own toplevel widget"""

    def onAddCmdToViewer(self):
        if not self.vf.hasGui: return

        self.vf.browseCommands('dashboardCommands', package='Pmv', log=0)


    def doit(self):
        # get handle to old tree
        oldtree = self.vf.dashboard.tree

        if isinstance(oldtree.master, Tkinter.Toplevel):
            return

        # create window for new tree
        master = Tkinter.Toplevel()
        #master.withdraw()
        #master.protocol('WM_DELETE_WINDOW',self.vf.dashboard.hide)
        master.protocol('WM_DELETE_WINDOW',self.vf.dockDashboard)

        tree = moveTreeToWidget(oldtree, master)
        tree.vf = self.vf
        tree.configure(hull_height=300)
        # update tree eight to force vertical scroll bar to appear if needed
        tree.updateTreeHeight()
        self.vf.dashboard.tree = tree
        tree.sets = self.vf.sets


    def destroy(self, event=None):
        self.vf.GUI.toolbarCheckbuttons['Dashboard']['Variable'].set(0)
        self.vf.dockDashboard(topCommand=0)
        


class DockDashboard(MVCommand):
    """Command to move the dashboard widget into the PMV GUI"""

    def onAddCmdToViewer(self):
        if not self.vf.hasGui: return

        self.vf.browseCommands('dashboardCommands', package='Pmv', log=0)


    def doit(self):

        # get handle to old tree
        oldtree = self.vf.dashboard.tree

        # get master
        if oldtree.master==self.vf.GUI.ROOT:
            return

        oldmaster = oldtree.master
        tree = moveTreeToWidget(oldtree, self.vf.GUI.ROOT)
        tree.pack(side='bottom', expand=0, fill='x')
        oldmaster.destroy()
        tree.vf = self.vf
        self.vf.dashboard.tree = tree
        tree.sets = self.vf.sets



class DashboardSuspendRedraw(MVCommand):
    """Command to suspend and un-suspend the tree redrawing"""

    def onAddCmdToViewer(self):
        if not self.vf.hasGui: return

        self.vf.browseCommands('dashboardCommands', package='Pmv', log=0)


    def doit(self, val):
        assert val in [True, False, 0, 1]
        self.vf.dashboard.tree.suspendRedraw = val



class ShowDashboard(MVCommand):
    """Command to show or hide the dashboard, can be added to _pmvrc"""
    def onAddCmdToViewer(self):
        if not self.vf.hasGui: return

        self.vf.browseCommands('dashboardCommands', package='Pmv', log=0)


    def doit(self, val):
        #print "ShowDashboard.doit", val
        tree = self.vf.dashboard.tree
        if val:
            self.vf.GUI.toolbarCheckbuttons['Dashboard']['Variable'].set(1)
            if isinstance(tree.master, Tkinter.Toplevel):
                self.vf.dashboard.tree.master.deiconify()
            else:
                self.vf.dashboard.tree.pack(side='bottom', expand=0, fill='x')
        else:
            self.vf.GUI.toolbarCheckbuttons['Dashboard']['Variable'].set(0)
            if isinstance(tree.master, Tkinter.Toplevel):
                self.vf.dashboard.tree.master.withdraw()
            else:
                self.vf.dashboard.tree.forget()



class AddDashboardCmd(MVCommand):
    """Command to add a command in a nwe column"""

    def onAddCmdToViewer(self):
        if not self.vf.hasGui: return

        self.vf.browseCommands('dashboardCommands', package='Pmv', log=0)


    def doit(self, descr):
        self.vf.dashboard.addColumnDescriptor(descr)



class Dashboard(MVCommand):

    """Display a widget showing a tree representation of the molecules in the Viewer and check buttons allowing to carry out command on parts of molecules directly.
    Certain commands such as coloring or displaying lines, CPK and S&B are implmented as mutually exclusive (i.e. like radio buttons.
"""

    def hide(self):
        self.vf.showDashboard(False)


    def show(self):
        self.vf.showDashboard(True)


    def addColumnDescriptor(self, colDescr):
        # adds self.vf to colDescr
        assert isinstance(colDescr,ColumnDescriptor)

        colDescr.vf = self.vf
        
        self.tree.addColumnDescriptor(colDescr)


    def onAddCmdToViewer(self):
        vf = self.vf
        
        if not vf.hasGui: return

        vf.browseCommands('dashboardCommands', package='Pmv', log=0)
        #self.hasMSMS = True
        #try:
        #    import mslib
        #    vf.browseCommands('msmsCommands', package='Pmv', log=0)
        #except:
        #    self.hasMSMS = False

        from ViewerFramework.VF import DeleteAtomsEvent, AddAtomsEvent
        vf.registerListener(DeleteAtomsEvent, self.handleDeleteEvents)
        vf.registerListener(AddAtomsEvent, self.handleAddEvents)

        # build the tree
        #master = Tkinter.Toplevel()
        #master.withdraw()
        #master.protocol('WM_DELETE_WINDOW',self.hide)

        from MolKit.molecule import MolecularSystem
        self.system = syst = MolecularSystem ('PMV Molecules')
        rootnode = MolFragNodeWithButtons(syst, None)
        tree = MolFragTreeWithButtons(self.vf.GUI.ROOT, rootnode, self.vf,
                                      selectionMode='multiple')
        rootnode.expand()
        tree.pack(side='bottom', expand=0, fill='x')
        self.tree = tree
        self.tree.sets = vf.sets


    def guiCallback(self):
        if self.vf.GUI.toolbarCheckbuttons['Dashboard']['Variable'].get():
            #self.show()
            self.vf.floatDashboard()
        else:
            #self.hide()
            self.vf.dockDashboard()
            

    def onAddObjectToViewer(self, obj):
        """
Add the new molecule to the tree
        """
        # we have to save .top and .parent else they become syst
        # and it brakes Pmv
        top = obj.top
        parent = obj.parent
        self.system.adopt(obj)
        # restore .top and .parent
        obj.top = top
        obj.parent = parent

        rootNode = self.tree.root
        length = len(self.system.children)
        if length==1:
            rootNode.refresh()
            
        rootNode.refreshChildren()

        if length==1:
            rootNode.expand()

        # make scroll bar appear if needed
        self.tree.updateTreeHeight()
        

    def onRemoveObjectFromViewer(self, obj):    
        #if obj in self.system:
        #    self.system.delete(obj)
        if obj in self.system.molecules:
            self.system.remove(obj)
        self.tree.root.refreshChildren()


    def handleDeleteEvents(self, event):
        """Function to update tree when molecular fragments are deleted.
"""
        # we get here BEFORE The atoms are actually deleted
        # so we collapse the tree to force its reconstruction AFTER
        # the atoms have actualyl been deleted.
        
        self.tree.root.refreshChildren()
        return
    
## this code does not rebuild the tree properly because the deleted objects
## are still there
##         tree = self.tree
##         for obj in event.objects:
##             try:
##                 parentNode = tree.objectToNode[obj.parent]
##                 if len(obj.parent.children)==0:
##                     parentNode.refresh()
##                 else:
##                     parentNode.refreshChildren(redraw=False)
##             except KeyError:
##                 pass
##         tree.redraw()
 

    def handleAddEvents(self, event):
        """Function to update tree when molecular fragments are added.
"""
        tree = self.tree
        for obj in event.objects:
            try:
                parentNode = tree.objectToNode[obj.parent]
                if len(obj.parent.children)==1:
                    parentNode.refresh()
                parentNode.refreshChildren(redraw=False)
            except KeyError:
                pass
        tree.redraw()
            
                
    def onCmdRun(self, command, *args, **kw):
        #import traceback
        #print '#############################################################'
        #traceback.print_stack()
        #print 'OnRun', command, args, kw
        # called when a Pmv command is run

        # find the column for this command
        for i,col in enumerate(self.tree.columns):
            if command.name in col.pmvCmdsToHandle:
                try:
                    col.onPmvCmd(command, *((i,)+args), **kw)
                except AttributeError:
                    pass
        return

##         tree = self.tree
##         column = None
##         for i,col in enumerate(tree.columns):
##             cmd, arg, opt = col.cmd
##             if cmd==command:
##                 column=i
##                 break

##         if column is None:
##             return # the command is not one in the dashboard

##         if col.commandType=='button':
##             return  # only check buttons not managed upon PMV command

##         molFrag = args[0]
##         negate = kw['negate']
##         if column<6:#command==self.vf.displayLines:
##             for o in molFrag:
##                 try:
##                     node = self.tree.objectToNode[o]
##                     if node.chkbtval[column]==negate:
##                         #only call if button needs to be checked
##                         node.set(column, negate==False)
##                 except KeyError:
##                     #print 'Failed to find object in tree', o
##                     pass
                    
                
Dashboard_GUI = MVCommandGUI()
from moleculeViewer import ICONPATH
Dashboard_GUI.addToolBar('Dashboard', icon1='dashboard.png', 
                         icon_dir=ICONPATH,
                         balloonhelp='Float Dashboard Widget', index=9)
            
commandList = [
    {'name':'dashboard', 'cmd':Dashboard(), 'gui':Dashboard_GUI},
    #{'name':'showDashboard', 'cmd':ShowDashboard(), 'gui':None},
    {'name':'floatDashboard', 'cmd':FloatDashboard(), 'gui':None},
    {'name':'dockDashboard', 'cmd':DockDashboard(), 'gui':None},
    {'name':'addDashboardCmd', 'cmd':AddDashboardCmd(), 'gui':None},
    {'name':'dashboardSuspendRedraw', 'cmd':DashboardSuspendRedraw(),
     'gui':None},
]

def initModule(viewer):
    for dict in commandList:
        viewer.addCommand(dict['cmd'], dict['name'], dict['gui'])
