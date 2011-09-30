########################################################################
#
# Date: April 2006 Authors: Guillaume Vareille, Michel Sanner
#
#    vareille@scripps.edu
#    sanner@scripps.edu
#
#       The Scripps Research Institute (TSRI)
#       Molecular Graphics Lab
#       La Jolla, CA 92037, USA
#
# Copyright: Guillaume Vareille, Michel Sanner and TSRI
#
#########################################################################
#
# $Header$
#
# $Id$
#

import types

from ViewerFramework.VFCommand import CommandGUI

from Pmv.mvCommand import MVCommand
from DejaVu.colorMap import ColorMap
from mglutil.util.callback import CallBackFunction

class EditColorPaletteByAtomType(MVCommand):

    def onAddCmdToViewer(self):
        if not self.vf.commands.has_key('colorByAtomType'):
            self.vf.loadCommand('colorCommands', 'colorByAtomType', 'Pmv', topCommand = 0)


    def __call__(self, ramp, labels, **kw):
        """
None <- editPaletteByAtomType(self, colorDict, **kw)
"""
        #print "__call__"
        apply(self.doitWrapper, (ramp, labels), kw)


    def guiCallback(self):
        #print "guiCallback"
        lFunc = CallBackFunction(self.guiApply_cb)
        self.vf.colorByAtomType.palette.addCallback(lFunc)
        self.vf.colorByAtomType.palette.showColormapSettings_cb()


    def guiApply_cb(self, colorPalette):
        #print "guiApply_cb"
        apply(self.doitWrapper, (colorPalette.ramp, colorPalette.labels), )


    def doit(self, ramp, labels):
        #print "doit"
        ColorMap.configure(self.vf.colorByAtomType.palette, ramp=ramp, labels=labels)


EditColorPaletteByAtomTypeGUI = CommandGUI()
EditColorPaletteByAtomTypeGUI.addMenuCommand('menuRoot', 
                                             'Edit', 
                                             'Edit Color By Atom Type Palette',
                                             cascadeName='color palettes')

commandList = [
    {'name':'editColorPaletteByAtomType', 
     'cmd':EditColorPaletteByAtomType(), 
     'gui':EditColorPaletteByAtomTypeGUI },
    ]


def initModule(viewer):
    for dict in commandList:
        viewer.addCommand( dict['cmd'], dict['name'], dict['gui'])
