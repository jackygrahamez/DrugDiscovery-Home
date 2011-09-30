from mglutil.gui.InputForm.Tk.gui import InputFormDescr, InputForm, \
CallBackFunction
from mglutil.gui.BasicWidgets.Tk.thumbwheel import ThumbWheel
from mglutil.gui.BasicWidgets.Tk.customizedWidgets import LoadButton, \
SaveButton, SliderWidget, ExtendedSliderWidget
from mglutil.util.callback import CallBackFunction
import Pmw, Tkinter
import types
from Pmv.mvCommand import MVCommand
from ViewerFramework.VFCommand import CommandGUI
from MolKit.molecule import Atom, Molecule
from Pmv.computeIsovalue import computeIsovalue

class coarseMolSurface(MVCommand):
    """Command to compute a coarse molecular surface.
    Selected atoms are first blurred as gaussians into a grid.
    The grid is then isocontoured at a user specified value.
    An indexed polygon geometry is added to the viewer. """
    
    
    def __init__(self, func=None):
        MVCommand.__init__(self)
        self.cms_network = None
        self.ifd = None
        self.resolutions={"very smooth":-0.1, "medium smooth": -0.3, "smooth": -0.5}
        self.resolution_type = "medium smooth"
        self.surf_resolution = self.resolutions[self.resolution_type] 
        self.isovalue=1
        self.isovalue_type = "fast approximation"
        self.precise_isovalues = {}
        self.custom_isovalue_flag = 0
        self.custom_resolution_flag = 0
        self.surfName = None
        self.surfNameList = []
        self.mol_surfNames = {}
        self.molName = None
        self.selection = None
        self.atomSet = None
        self.bindGeom = True
        self.bindFlag = Tkinter.BooleanVar()
        self.bindFlag.set(self.bindGeom)
        self.perMol = True
        self.immediate = False
        self.network_nodes = {"gridSize":[2, 'Dial'],
                              "resolution":[3,'UT Blur'],
                              "isovalue": [4, 'UT-Isocontour'],
                              "surfName": [5, self.surfName]}
        self.gridSize = (32, 32, 32)
        self.buildFormFlag = False
        self.newSelection =False
        self.padding = 0.0
        self.surface = None
        self.checkComponentsFlag = Tkinter.BooleanVar()
        self.checkComponentsFlag.set(False)
        

        
    def onAddCmdToViewer(self):
        if not self.vf.commands.has_key('vision'):
            self.vf.browseCommands('visionCommands',log=False)
        if self.vf.vision.ed is None:
            self.vf.vision(log=False)
        self.vf.browseCommands('displayCommands', commands=('DisplayBoundGeom',), log=0, package='Pmv')
        
    def loadNetwork(self):
        self.cms_network = self.vf.vision.ed.getNetworkByName("CoarseMolSurface")
        if self.cms_network:
            self.cms_network = self.cms_network[0]
        else:
            from mglutil.util.packageFilePath import findFilePath
            network_path = findFilePath("CoarseMolSurface_net.py", "Pmv.VisionInterface")
            self.vf.vision.ed.loadNetwork(network_path, takefocus=False)
            self.cms_network = self.vf.vision.ed.getNetworkByName("CoarseMolSurface")[0]
        res = self.resolutions[self.resolution_type]
        self.cms_network.getNodeByName('UT Blur')[0].inputPorts[5].widget.set(res, run=0)
        isoval = self.isovalue = self.piecewiseLinearInterpOnIsovalue(res)
        self.cms_network.getNodeByName('UT-Isocontour')[0].inputPorts[1].widget.set(isoval,run=0 )
        self.cms_network.getNodeByName('UT-Isocontour')[0].inputPorts[2].widget.set(0, run = 0)
        self.cms_network.nodes[4].inputPortByName['name'].widget.set("coarseMolSurface", run = 0)
        self.cms_network.nodes[7].getInputPortByName("onegeom").widget.set(1)
        self.cms_network.getNodeByName("Dial")[0].run()
        self.cms_network.freeze()

##     def checkDependencies(self):
##         """check availability of mdules the command depends on"""
##         from UTpackages.UTisocontour import isocontour
##         from UTpackages.UTblur import blur
##         from mslib import MSMS
##         from QSlimLib import qslimlib

    def onAddObjectToViewer(self, obj):
        pass
    
    def guiCallback(self):
        selection = self.vf.getSelection()
        if not selection:
            return
        if not self.cms_network:
            self.loadNetwork()
        self.buildFormFlag = 1
        self.cms_network.unfreeze()
        val = self.showForm( modal = 0, blocking=0, force = 1)
        if not self.custom_isovalue_flag:
            self.disableThumbWheel(self.ifd.entryByName['customIsovalue']['widget'])
        if not self.custom_resolution_flag:
            self.disableThumbWheel(self.ifd.entryByName['customResolution']['widget'])
        if self.ifd:
            bindmol = self.ifd.entryByName['bindToMolecule']
            if len(selection.top.uniq()) > 1:
                # selected more than one molecule ->
                # disable "Bind to molecule" chekbutton
            
                bindmol['widget'].configure(state='disabled')
                bindmol['wcfg']['state']='disabled'
            else:
                if bindmol['wcfg']['state']=='disabled':
                    bindmol['widget'].configure(state='normal')
                    bindmol['wcfg']['state']='normal'
        self.buildFormFlag = 0


    def buildFormDescr(self, formName="default"):
        
        if formName == 'default':
            ifd = self.ifd = InputFormDescr(title ="Compute Coarse Molecular Surface")
            #defaultValues = self.getLastUsedValues()
            #print "default values:", defaultValues
            if self.surfName:
                surfName = self.surfName
            else:
                surfName = "CoarseMolSurface"
            self.immediate = False
            ifd.append({'widgetType':Tkinter.Checkbutton,
                        'tooltip':"""enables immediate update of the selected\n input parameter""",
                        'name': 'mode',
                        'defaultValue': self.immediate,
                        'wcfg':{'text':'Immediate',
                                'command':self.mode_cb,
                                'variable':Tkinter.BooleanVar()},
                        'gridcfg':{'sticky':'w','columnspan':2 }
                        })
            
            ifd.append({'widgetType':Pmw.ComboBox,
                        'name':'surfName',
                        'required':1,
                        'tooltip': "Type-in a new name or chose one \nfrom the list below,\n '_' are not accepted.",
                        'wcfg':{'labelpos':'n',
                                'label_text':'Select/type surface name: ',
                                'entryfield_validate':self.entryValidate,
                                'entryfield_value':surfName,
                                'scrolledlist_items':self.surfNameList,
                                'fliparrow':1,
                                'selectioncommand': self.select_surfname
                                },
                        'gridcfg':{'sticky':'we', 'columnspan':2},
                        
                        })
            
            ifd.append({'name':'perMol',
                        'tooltip':"""When checked, surfaces will be computed using all atoms\n  of each selected molecule.\nIf unchecked, the unselected atoms are ignored during the
calculation.""",
                        'widgetType':Tkinter.Checkbutton,
                        'defaultValue': self.perMol,
                        'wcfg':{'text':'Per Molecule',
                                'variable':Tkinter.BooleanVar(),
                                'command':self.perMol_cb},
                        'gridcfg':{'sticky':'w','columnspan':2}
                        })

            ifd.append({'widgetType':Pmw.EntryField,
                        'name':'gridsize',
                        'tooltip':'Type-in the grid size',
                        'wcfg':{'labelpos':'w',
                                'label_text':'Grid size: ',
                                'entry_width':8,
                                'value': self.gridSize[0],
                                'validate':{'validator': 'numeric',},
                                'command':self.set_gridsize},
                        'gridcfg':{'column':0, 'columnspan':2, 'sticky':'w'}
                        })
            ifd.append({
                        'widgetType':ThumbWheel,
                        'name':'padding',
                        'tooltip':
                        """size of the padding around the molecule """,
                        'gridcfg':{'sticky':'w','column':0,  'columnspan':2},
                        'wcfg':{'value':self.padding,
                                'oneTurn':10, 'min':0.0, 'lockMin':True,
                                'type':'float', 'precision':1,
                                'continuous':False,
                                'wheelPad':1,'width':90,'height':15,
                                'callback': self.set_padding,
                                'labCfg':{'text':'padding:'},
                                }
                        })
            ifd.append({'name':'resolutionGroup',
                        'widgetType':Pmw.Group,
                        'container':{'resolutionGroup':"w.interior()"},
                        
                        'wcfg':{'tag_text':"Surface resolution:", 'ring_borderwidth':3,},
                        'gridcfg':{'sticky':'we', 'columnspan':2}})

            ifd.append({'name':'resolution_type',
                        'widgetType':Pmw.RadioSelect,
                         'parent':'resolutionGroup',
                        'tooltip':
                        """ very smooth, medium smooth and smooth correspond to the blobbyness\n value (used in the gaussian blurring) of -0.1, -0.3, and -0.5 respectively""",
                        'listtext':['very smooth', 'medium smooth', 'smooth', 'custom'],
                        'defaultValue':self.resolution_type,
                        'wcfg':{'orient':'vertical','labelpos':'n',
                                'labelpos':None,
                                #'label_text':'Surface resolution: ',
                                'command':self.set_resolution,
                                #'hull_relief':'ridge',
                                #'hull_borderwidth':2,
                                'padx':0,
                                'buttontype':'radiobutton'},
                        'gridcfg':{'sticky': 'nw','column':0,  'columnspan':2}
                        })
            
            ifd.append({'name':'customResolution',
                        'parent':'resolutionGroup',
                        'widgetType':ThumbWheel,
                        'tooltip':
                        """Set custom resolution value""",
                        'gridcfg':{'sticky':'w','column':0,  'columnspan':2},
                        'wcfg':{'value':self.surf_resolution,'oneTurn':2, 
                                'type':'float',
                                'increment':0.1,
                                'precision':1,
                                'continuous':False,
                                "max":-0.009,
                                'wheelPad':2,'width':145,'height':18,
                                'showLabel':self.custom_resolution_flag, 'lockShowLabel':1,
                                'callback': self.set_custom_resolution
                                #'labCfg':{'text':'Surface Resolution:'},
                                }
                        })
           
            
            ifd.append({'name':'isovalueGroup',
                        'widgetType':Pmw.Group,
                        'container':{'isovalueGroup':"w.interior()"},
                        'wcfg':{'tag_text':"Isocontour values:",'ring_borderwidth':3},
                        'gridcfg':{'sticky':'we', 'columnspan':2}})
            ifd.append({'name':'isovalue_type',
                        'widgetType':Pmw.RadioSelect,
                        'parent': 'isovalueGroup',
                        'tooltip': "select isovalue option",
                        'listtext':['fast approximation',
                                        'precise value', 'custom'],
                        'defaultValue':self.isovalue_type,
                        'wcfg':{'orient':'vertical','labelpos':'n',
                                #'label_text':'Isocontour values:',
                                'labelpos':None,
                                'command':self.set_isovalue,
                                #'hull_relief':'ridge',
                                #'hull_borderwidth':2,
                                'padx':0,
                                'buttontype':'radiobutton'},
                        'gridcfg':{'sticky': 'nw','column':0,  'columnspan':2}
                        })
            ifd.append({'name':'customIsovalue',
                        'widgetType':ThumbWheel,
                        'parent': 'isovalueGroup',
                        'tooltip':
                        """Set custom isovalue""",
                        'gridcfg':{'sticky':'w','column':0,  'columnspan':2},
                        'wcfg':{'value':self.isovalue,'oneTurn':2, 
                                'type':'float',
                                'increment':0.1,
                                'precision':1,
                                'continuous':False,
                                'wheelPad':2,'width':145,'height':18,
                                'showLabel':self.custom_isovalue_flag, 'lockShowLabel':1,
                                'callback': self.set_custom_isovalue,
                                }
                        })


            ifd.append({'widgetType':Tkinter.Checkbutton,
                    'tooltip':"""Select/deselect this button to bind/unbind\nsurface to molecule""",
                        'name': 'bindToMolecule',
                        'wcfg':{'text':'Bind Surface to molecule',
                                'command':self.bind_cb,
                                'variable':self.bindFlag,
                                'state':'normal'},
                        'gridcfg':{'sticky':'w', 'pady': 10,'columnspan':2 }
                    })
            
            ifd.append({'widgetType':Tkinter.Checkbutton,
                    'tooltip':"""enable/disable checking for surface components.\nIf two or more componens are found - the largest\nis chosen for output""",
                        'name': 'checkComponents',
                        'wcfg':{'text':'Check surface components',
                                'command': self.connectedComponent_cb,
                                'variable':self.checkComponentsFlag,
                                'state':'normal'},
                        'gridcfg':{'sticky':'w', 'pady': 10,'columnspan':2 }
                    })
            
            ifd.append({'name':'compute',
                        'widgetType':Tkinter.Button,
                        'wcfg':{'text':'Compute',
                                'state': 'normal',
                                'command':self.compute},
                        'gridcfg':{'sticky':'wne','column':0}
                        })
                        
            ifd.append({'name':'dismiss',
                        'widgetType':Tkinter.Button,
                        'wcfg':{'text':'Dismiss',
                                'command':self.dismiss},
                        'gridcfg':{'sticky':'wne','row': -1, 'column':1}
                        })

            return ifd



    def doit(self, **kw):
        """list of keywords: nodes, surfName, perMol, gridZise, isovalue,
        resolution, bindGeom, immediate, padding.
        """
        #print "in doit kw:", kw
        perMol = kw.get("perMol", None)
        nodes_to_run = []
        if perMol == None:
            perMol = self.perMol
        nodes = kw.get("nodes", None)
        immediate = kw.get("immediate", None)
        if immediate is None:
            immediate = self.immediate
        if nodes:
            if perMol:
                atomSet = nodes.top.uniq()
            else:
                atomSet = nodes
            if atomSet != self.atomSet:
                self.atomSet = atomSet
                self.newSelection = True
                molecules = nodes.top.uniq()
                for mol in molecules:
                    mol.defaultRadii()
                selection_node = self.cms_network.getNodeByName("Get Selection")[0]
                if selection_node.frozen:
                    selection_node.toggleFrozen_cb() #unfreeze
                selection_node.outputPorts[0].data = atomSet
                selection_node.toggleFrozen_cb() #freeze
                if immediate:
                    self.cms_network.getNodeByName("UT Blur")[0].schedule_cb()
        surfName = kw.get("surfName")
        if surfName:
            if surfName not in self.surfNameList:
                self.surfNameList.append(surfName)
            if surfName != self.surfName:
                self.surfName = surfName
                # the Indexed Polygons node's name changes when it is set to
                #  a new geometry name. 
                self.network_nodes["surfName"][1] = surfName
                nodes_to_run.append("surfName")
                # Indexed Polygons node:
                self.cms_network.nodes[4].inputPortByName['name'].widget.set(surfName, run = 0)
                if immediate:
                    #run the network
                    #self.cms_network.run()
                    self.cms_network.getNodeByName("UT Blur")[0].schedule_cb()
                    
        gs = kw.get("gridSize", None)
        if gs:
            gridSize = (gs, gs, gs)
            if gridSize != self.gridSize:
                self.gridSize = gridSize
                nodes_to_run.append("gridSize")
                if immediate:
                    if self.newSelection:
                        #set the node value and run the network
                        self.cms_network.getNodeByName('Dial')[0].inputPorts[0].widget.set(gs, run=0)
                        #self.cms_network.run()
                        self.cms_network.getNodeByName("UT Blur")[0].schedule_cb()
                    else: # run the node 
                        self.cms_network.getNodeByName('Dial')[0].inputPorts[0].widget.set(gs, run=0)
                        self.cms_network.getNodeByName('Dial')[0].schedule_cb()
                else: # set the node value
                    self.cms_network.getNodeByName('Dial')[0].inputPorts[0].widget.set(gs, run=0)

        pd = kw.get("padding", None)
        if pd is not None:
            if pd != self.padding:
                self.padding = pd
                nodes_to_run.append("resolution")
                if immediate:
                    #if self.newSelection:
                        #set the node value and run the network
                        #self.cms_network.getNodeByName("UT Blur")[0].inputPorts[4].widget.set(pd, run=0)
                        #self.cms_network.run()
                        
                    #else: # run the node
                    self.cms_network.getNodeByName("UT Blur")[0].inputPorts[4].widget.set(pd, run=0)
                    self.cms_network.getNodeByName("UT Blur")[0].schedule_cb()
                else: # set the node value
                    self.cms_network.getNodeByName("UT Blur")[0].inputPorts[4].widget.set(pd, run=0)                
        resolution = kw.get("resolution", None)
        isotype = kw.get("isovalue", None)
        if resolution:
            if resolution != self.surf_resolution:
                self.surf_resolution = resolution
                nodes_to_run.append("resolution")
                if not isotype:
                    #check if we need to recompute isovalue:
                    if self.isovalue_type != "custom":
                        if self.isovalue_type == 'fast approximation':
                            isovalue = self.piecewiseLinearInterpOnIsovalue(resolution)
                        else:
                            isovalue = self.get_precise_isovalue(resolution)
                            
                        if isovalue is not None:
                            self.isovalue = isovalue
                            self.cms_network.getNodeByName('UT-Isocontour')[0].inputPorts[1].widget.set(isovalue, run = 0)
                        else:
                            print "Setting isocontour value to custom"
                            self.set_isovalue("custom")
                            self.isovalue_type = "custom"
                
                if immediate:
                    #if self.newSelection :
                        # set the node value and run the network
                    #    self.cms_network.getNodeByName('UT Blur')[0].inputPorts[5].widget.\
                    #                                       set(resolution, run = 0)
                    #    self.cms_network.run()
                    #else:
                        # run the node

                    self.cms_network.getNodeByName('UT Blur')[0].inputPorts[5].widget.\
                                                   set(resolution, run = 0)
                    self.cms_network.getNodeByName('UT Blur')[0].schedule_cb()
                    
                else: # not immediate
                    # set the node value
                    self.cms_network.getNodeByName('UT Blur')[0].inputPorts[5].widget.\
                                                   set(resolution, run = 0)
        if isotype:
            if type(isotype) == types.StringType:
                self.isovalue_type = isotype
                if isotype == 'fast approximation':
                    isovalue = self.piecewiseLinearInterpOnIsovalue(self.surf_resolution)
                else:
                    #check if we need to recompute precise isovalue:
                    isovalue = self.get_precise_isovalue(self.surf_resolution)
            else:
                self.isovalue_type = "custom"
                isovalue = isotype
            if isovalue is not None:
                if isovalue != self.isovalue:
                    nodes_to_run.append("isovalue")
                    self.isovalue = isovalue
                    self.cms_network.getNodeByName('UT-Isocontour')[0].inputPorts[1].widget.set(isovalue, run = 0)
                    if immediate:
                        self.cms_network.getNodeByName("UT Blur")[0].schedule_cb()
                        
            else:
                print "Setting isocontour value to custom"
                self.set_isovalue("custom")
                self.isovalue_type = "custom"

        if not immediate:
            #run the network
            if "gridSize" in nodes_to_run:
                self.cms_network.getNodeByName('Dial')[0].schedule_cb()
            else:
                self.cms_network.getNodeByName("UT Blur")[0].schedule_cb()
        # find out if we need to bind/unbind the geometry to the molecule
        bindGeom = kw.get("bindGeom", None)
        if bindGeom == None:
            bindGeom = self.bindGeom
        bindcmd = self.vf.bindGeomToMolecularFragment
        surf = self.vf.GUI.VIEWER.GUI.objectByName(self.surfName)
        if surf is None:
            print "CoarseMolSurface WARNING: surface %s is not created" % self.surfName
            return
        if self.vf.userpref['sharpColorBoundariesForMsms']['value'] == 'blur':
            surf.Set(inheritSharpColorBoundaries=False, sharpColorBoundaries=False,)

        if bindGeom :
            #if self.newSelection or len(nodes_to_run):
            if len(self.atomSet.top.uniq()) > 1:
                msg =  "More than one molecule selected -can not bind the geometry"
                self.vf.warningMsg(msg)
            else:
                bindcmd(surf, self.atomSet, log=0)
        else:
            if hasattr(surf, 'mol'):
                # we will probably never get here because the 'IndexedPolygons' geometry node returns a new geometry object when it runs, so we loose 'mol' attribute
                mol = surf.mol
                if mol.geomContainer.geoms.has_key(self.surfName):
                    if surf.parent != mol.geomContainer.masterGeom:
                        oldname = mol.geomContainer.masterGeom.fullName+ '|' + self.surfName
                    else:
                        oldname = surf.fullName
                        #reparent the surface to root:
                        self.vf.GUI.VIEWER.ReparentObject(surf, self.vf.GUI.VIEWER.rootObject)
                        surf.fullName = surf.parent.fullName+'|'+self.surfName
                    # unbind
                    if bindcmd.data.has_key(oldname):
                        bindcmd.data[oldname].clear()
                        bindcmd.data.pop(oldname)
                del(surf.mol)
            else:
                if self.surface:
                    if self.surface.name == surf.name:
                        # remove old data info
                        if bindcmd.data.has_key(self.surface.fullName):
                            bindcmd.data[self.surface.fullName].clear()
                            bindcmd.data.pop(self.surface.fullName)
        self.surface = surf


#        if perMol:
#            #print "nodes", nodes
#            if not nodes:
#                nodes = self.vf.getSelection()
#            boundgeom = False
#            for mol in self.atomSet.top.uniq():
#                if surf.parent == mol.geomContainer.masterGeom:
#                    boundgeom = True
#                    break
#            if boundgeom:
#                try:
#                    self.vf.DisplayBoundGeom(nodes, negate=False, 
#                                             geomNames=[surf.fullName,],
#                                             only=True, log=1, nbVert=1)
#                except:
#                    pass
        
        self.newSelection = False

        # highlight selection
        selMols, selAtms = self.vf.getNodesByMolecule(self.vf.selection, Atom)
        lMolSelectedAtmsDict = dict( zip( selMols, selAtms) )
        if hasattr(surf, 'mol') and lMolSelectedAtmsDict.has_key(surf.mol):
            lSelectedAtoms = lMolSelectedAtmsDict[surf.mol]
            if len(lSelectedAtoms) > 0:
                lAtomVerticesDict = bindcmd.data[surf.fullName]['atomVertices']
                highlight = [0] * len(surf.vertexSet.vertices)
                for lSelectedAtom in lSelectedAtoms:
                    lVertexIndices = lAtomVerticesDict.get(lSelectedAtom, [])
                    for lVertexIndex in lVertexIndices:
                        highlight[lVertexIndex] = 1
                surf.Set(highlight=highlight)
                if perMol:
                    surf.removeFacesWithoutHighlightedVertices()


    def __call__(self, **kw):
        """None <- mv.coarseMolSurface(**kw)\n
        list of available keywords:
        nodes    -- atomic fragment; \n
        surfName -- string - name of created surface; \n
        perMol   -- True or False; if True, a surface is computed for each 
                    molecule having at least one node in the current selection,
                    else the surface is computed for the current selection;\n
        gridZise -- integer; Size of computed grid will be: gridSize x gridSize x gridSize;\n
        isovalue -- can be one of the following: 'fast approximation', 'precise value' or
                      a numeric value specifying the isovalue;\n
        resolution -- resolution of the blurred surface - a negative value; \n
        bindGeom   -- True or False; if True - the surface is bound to the selected molecule.
        """
        if not self.cms_network:
            self.loadNetwork()
        nodes = kw.get("nodes")
        if nodes:
            kw["nodes"] = self.vf.expandNodes(nodes)
        apply(self.doitWrapper, (), kw)

    # Callbacks

                
    def perMol_cb(self, event=None):
        """calback of perMol check button of the input form"""
        ebn = self.ifd.entryByName
        perMol = self.perMol = ebn['perMol']['wcfg']['variable'].get()
        self.perMol = perMol
        ebn = self.ifd.entryByName
        immediate = ebn['mode']['wcfg']['variable'].get()
        if immediate:
            self.doitWrapper(nodes = self.vf.getSelection(), perMol = perMol,immediate=True)
        
        
    def mode_cb (self, event=None):
        """callback of the input form's immediate mode check button""" 
        ebn = self.ifd.entryByName
        immediate = ebn['mode']['wcfg']['variable'].get()
        computeButton = ebn['compute']['widget']
        if immediate:
            computeButton.configure(state='disabled')
            ebn['compute']['wcfg']['state']='disabled'
        else:
            computeButton.configure(state='normal')
            ebn['compute']['wcfg']['state']='normal'
        self.immediate = immediate

    def select_surfname(self, surfName):
        """callback of surface name ComboBox """
        if surfName:
            if surfName in self.surfNameList:
                surf = self.vf.GUI.VIEWER.GUI.objectByName(surfName)
                if surf:
                    for mol in self.atomSet.top.uniq():
                        if surf.parent == mol.geomContainer.masterGeom:
                            # the surfName geometry is bound to mol - make sure to check the
                            # 'bindToMolecule' checkbutton
                            self.bindFlag.set(True)
                            break
            immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
            if immediate:
                selection = self.vf.getSelection()
                self.doitWrapper(nodes=selection, surfName = surfName, immediate = immediate, bindGeom = self.bindFlag.get())
            
    def set_gridsize(self):
        """callback of the 'grid size' entry field"""
        val = self.ifd.entryByName['gridsize']['widget'].get()
        if val:
            immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
            if immediate:
                selection = self.vf.getSelection()
                #check if self.surfName corresponds to the name typed in the entryform:
                surfName = self.ifd.entryByName['surfName']['widget'].get()
                if surfName != self.surfName:
                    self.doitWrapper(nodes=selection, surfName = surfName, immediate =False)#do not run the network yet
                    
                self.doitWrapper(nodes=selection, immediate = True, gridSize = int(val), bindGeom = self.bindFlag.get())
        
    def set_resolution(self, val):
        """callback of the input form's resolution radio buttons"""
        #print "in set_resolution val = ", val
        if self.buildFormFlag:
            return
        self.resolution_type = val
        if val == "custom":
            self.custom_resolution_flag = 1
            self.enableThumbWheel(self.ifd.form.descr.entryByName['customResolution']['widget'],
                                  val = self.surf_resolution)
        else:
            self.custom_resolution_flag = 0
            self.disableThumbWheel(self.ifd.form.descr.entryByName['customResolution']['widget'])
            surf_resolution = self.resolutions[val]
            cb = self.ifd.entryByName['isovalue_type']['widget']
            if surf_resolution < -3.0  or surf_resolution > -0.1:
                # resolution is out of range of values for isovalue fast approximation -
                # need to disable the check button:
                cb.component('fast approximation').configure(state='disabled')
                if cb.getvalue() == "fast approximation":
                    self.set_isovalue("custom")
            else:
                if cb.component('fast approximation').cget('state') == 'disabled':
                    cb.component('fast approximation').configure(state = "normal")
            immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
            if immediate:
                selection = self.vf.getSelection()
                #check if self.surfName corresponds to the name typed in the entryform:
                surfName = self.ifd.entryByName['surfName']['widget'].get()
                if surfName != self.surfName:
                    self.doitWrapper(nodes=selection,surfName = surfName, immediate =False)#do not run the network yet
                self.doitWrapper(nodes=selection, resolution = surf_resolution, immediate = True, bindGeom = self.bindFlag.get())

    def set_isovalue(self, val):
        """ callback of the input form's isovalue radio buttons """
        #print "in set_isovalue val = ", val
        if self.buildFormFlag:
            return
        if val == "custom":
            self.isovalue_type = "custom"
            self.custom_isovalue_flag = 1
            if self.ifd:
                self.enableThumbWheel(self.ifd.entryByName['customIsovalue']['widget'],
                                      val = self.isovalue)
        else:
            self.custom_isovalue_flag = 0
            self.disableThumbWheel(self.ifd.entryByName['customIsovalue']['widget'])
            immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
            if immediate:
                #check if self.surfName corresponds to the name typed in the entryform:
                surfName = self.ifd.entryByName['surfName']['widget'].get()
                selection = self.vf.getSelection()
                if surfName != self.surfName:
                    self.doitWrapper(nodes=selection,surfName = surfName, immediate =False)#do not run the network yet
                self.doitWrapper(nodes=selection, isovalue=val, immediate = True, bindGeom = self.bindFlag.get())
            

    def set_padding(self, val):
        """callback of the thumbwheel widget for setting padding around the molecule."""
        print "calls set_padding"
        immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
        if immediate:
           #check if self.surfName corresponds to the name typed in the entryform:
            surfName = self.ifd.entryByName['surfName']['widget'].get()
            selection = self.vf.getSelection()
            if surfName != self.surfName:
                self.doitWrapper(nodes=selection,surfName = surfName, immediate =False)#do not run the network yet
            self.doitWrapper(nodes=selection,padding=val, immediate = True, bindGeom = self.bindFlag.get() ) 

            
    def set_custom_isovalue(self, val):
        """callback of the thumbwheel widget used for setting custom isovalue """
        #print "in set_custom_isovalue val = ", val
        immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
        if immediate:
            #check if self.surfName corresponds to the name typed in the entryform:
            surfName = self.ifd.entryByName['surfName']['widget'].get()
            selection = self.vf.getSelection()
            if surfName != self.surfName:
                self.doitWrapper(nodes=selection,surfName = surfName, immediate =False)#do not run the network yet
            self.doitWrapper(nodes=selection,isovalue=val, immediate = True, bindGeom = self.bindFlag.get() )

    def set_custom_resolution(self, val):
        """callback of the thumbwheel widget used for setting custom resolution"""
        #print "in set_custom_resolution val = ", val
        cb = self.ifd.entryByName['isovalue_type']['widget'].component('fast approximation')
        if val < -3.0  or val > -0.1:
            # resolution is out of range of values for isovalue fast approximation -
            # need to disable the check button:
            cb.configure(state='disabled')
            if self.ifd.entryByName['isovalue_type']['widget'].getvalue() == "fast approximation":
                self.set_isovalue("custom")
                self.isovalue_type = "custom"
        else:
            if cb.cget('state') == 'disabled':
                cb.configure(state = "normal")
        immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
        if immediate:
            #check if self.surfName corresponds to the name typed in the entryform:
            surfName = self.ifd.entryByName['surfName']['widget'].get()
            selection = self.vf.getSelection()
            if surfName != self.surfName:
                self.doitWrapper(nodes=selection,surfName = surfName, immediate =False)#do not run the network yet
            self.doitWrapper(nodes=selection,resolution = val, immediate = True, bindGeom = self.bindFlag.get())
                
    def dismiss (self, event = None):
        """Withdraws the input form"""
        
        self.cmdForms['default'].withdraw()

    def bind_cb(self):
        """callback of the 'bind surface to molecule' check button """
        #immediate = self.ifd.entryByName['mode']['wcfg']['variable'].get()
        self.bindGeom = self.bindFlag.get()
##         if immediate:
##             #check if self.surfName corresponds to the name typed in the entryform:
##             surfName = self.ifd.entryByName['surfName']['widget'].get()
##             if surfName != self.surfName:
##                 self.doitWrapper(surfName = surfName, immediate =False)#do not run the network yet
##             self.doitWrapper(immediate = True, bindMol = self.bindFlag.get())




    def connectedComponent_cb (self, event = None):
        """Callback to connect/disconnect the connected components node """
        network = self.cms_network
        # ConnectedComponents node:
        node = network.nodes[7]
        # IndexedPolygons node:
        indpol = network.nodes[4]
        # PMV Viewer node:
        pmvviewer = network.getNodeByName('Pmv Viewer')[0]
        if self.checkComponentsFlag.get():
            # delete connections between IndexedPolygons and PmvViewer nodes  
            node.getInputPortByName("onegeom").widget.set(1)
            outConnections = indpol.getOutConnections()
            network.deleteConnections(outConnections, 0)
            #create connections between 'IndexedPolygons', 'ConnectedComponents'
            # and 'Pmv Viewer' nodes
            network.connectNodes(indpol, node)
            network.connectNodes(node, pmvviewer, "allGeometries", "geometries")
        else:
            # delete connections between 'IndexedPolygons', 'ConnectedComponents'
            # and 'Pmv Viewer' nodes
            outConnections1 = node.getOutConnections()
            if len(outConnections1):
                outConnections2 =  indpol.getOutConnections()
                network.deleteConnections(outConnections1, 0)
                network.deleteConnections(outConnections2, 0)
            network.connectNodes(indpol, pmvviewer)


    def get_precise_isovalue(self, resolution):
        """Computes precise isovalue using methods from computeIsovalue.py """
        mols = []
        for mol in  self.atomSet.top.uniq():
            mols.append(mol.name)
                    
        ri = self.precise_isovalues.get(tuple(mols))
        res_str = "%.2f"%resolution
        if ri:
            isovalue = ri.get(res_str)
            if not isovalue:
                isovalue = computeIsovalue(self.atomSet, resolution, self.gridSize)
                if isovalue is not None:
                    self.precise_isovalues[tuple(mols)][res_str] = isovalue
        else:
            self.precise_isovalues[tuple(mols)]={}
            isovalue = computeIsovalue(self.atomSet, resolution, self.gridSize)
            if isovalue is not None:
                self.precise_isovalues[tuple(mols)][res_str] = isovalue
        return isovalue
            
    def entryValidate(self, text):
        """
        Method to validate the name of the msms surface. This name
        will be used by other command to build Pmw widget so it can't
        contain an '_'.
        """
        if '_' in text:
            return Pmw.ERROR
        else:
            return Pmw.OK

    def compute(self, event = None):
        """callback of 'Compute' button of the input form """
        kw = {}
        surfName = self.ifd.entryByName['surfName']['widget'].get()
        if surfName != self.surfName:
            kw['surfName']=surfName

        restype = self.ifd.entryByName['resolution_type']['widget'].getvalue()
        if restype == "custom":
            resolution = self.ifd.entryByName['customResolution']['widget'].get()
        else:
            resolution = self.resolutions[restype]
        kw['resolution'] = resolution
        isovalue = self.ifd.entryByName['isovalue_type']['widget'].getvalue()
        if isovalue == "custom":
            isovalue = self.ifd.entryByName['customIsovalue']['widget'].get()
        kw['isovalue'] = isovalue
        perMol = self.ifd.entryByName['perMol']['wcfg']['variable'].get()
        kw['perMol'] = perMol
        kw['immediate'] = False
        gs= self.ifd.entryByName['gridsize']['widget'].get()
        if gs:
            kw['gridSize'] = int(gs)
        kw['bindGeom'] = self.bindFlag.get()
        kw['nodes'] = self.vf.getSelection()
        kw['padding'] = self.ifd.entryByName['padding']['widget'].get()
        apply(self.doitWrapper, (), kw)
        self.dismiss()


    def disableThumbWheel(self, tw):
        """disables a thumbwheel widgets used to specify custom resolution/isovalue"""
        def foo(val):
            pass
        tw.configure(showLabel=0)
        tw.canvas.bind("<ButtonPress-1>", foo)
	tw.canvas.bind("<ButtonRelease-1>", foo)
	tw.canvas.bind("<B1-Motion>", foo)
        tw.canvas.bind("<Button-3>", foo)
        
        
    def enableThumbWheel(self, tw, val =None):
        """enables a thumbwheel widgets used to specify custom resolution/isovalue"""
        tw.canvas.bind("<ButtonPress-1>", tw.mouseDown)
	tw.canvas.bind("<ButtonRelease-1>", tw.mouseUp)
	tw.canvas.bind("<B1-Motion>", tw.mouseMove)
        tw.canvas.bind("<Button-3>", tw.toggleOptPanel)
        tw.configure(showLabel=1)
        if val:
            tw.set(val, update=0)

    def piecewiseLinearInterpOnIsovalue(self, x):
        """Piecewise linear interpretation on isovalue that is a function
        blobbyness.
        """
        import sys
        X = [-3.0, -2.5, -2.0, -1.5, -1.3, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1]
        Y = [0.6565, 0.8000, 1.0018, 1.3345, 1.5703, 1.8554, 2.2705, 2.9382, 4.1485, 7.1852, 26.5335]
        if x<X[0] or x>X[-1]:
            print "WARNING: Fast approximation :blobbyness is out of range [-3.0, -0.1]"
            return None
        i = 0
        while x > X[i]:
            i +=1
        x1 = X[i-1]
        x2 = X[i]
        dx = x2-x1
        y1 = Y[i-1]
        y2 = Y[i]
        dy = y2-y1
        return y1 + ((x-x1)/dx)*dy


coarseMolSurfaceGUI = CommandGUI()
coarseMolSurfaceGUI.addMenuCommand('menuRoot','Compute', 'Coarse Molecular Surface')
commandList  = [{'name':'coarseMolSurface','cmd':coarseMolSurface(),'gui':coarseMolSurfaceGUI},]

def initModule(viewer):
    for com in commandList:
        viewer.addCommand(com['cmd'],com['name'],com['gui'])
