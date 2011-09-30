#!/usr/bin/env python
#
# 
#
# $Header: /opt/cvs/python/packages/share1.5/AutoDockTools/Utilities24/prepare_flexdocking4.py,v 1.5 2007/10/08 18:11:40 rhuey Exp $
#
import os 

from MolKit import Read
from MolKit.protein import ProteinSet, ResidueSet
from MolKit.molecule import BondSet
from MolKit.stringSelector import CompoundStringSelector

from AutoDockTools.MoleculePreparation import AD4FlexibleDockingPreparation



if __name__ == '__main__':
    import sys
    import getopt


    def usage():
        "Print helpful, accurate usage statement to stdout."
        print "Usage: prepare_flexdocking4.py -l filename -r receptor_filename -s list_of_names_of_residues_to_move"
        print "    Description of command..."
        print "         -l     ligand_filename (.pdbqt)"
        print "         -r     receptor_filename (.pdbqt)"
        print "         -s     names of flex residues separated by underscore "
        print "                  ARG8_ILE82    or   hsg1:A:ARG8_ILE82_hsg1:B:THR4 "
        print "    Optional parameters:"
        print "        [-v]    verbose output"
        print "        [-N]    type(s) of bonds to disallow: "
        print "        [-P]    pairs of atom names bonds between which to disallow: "
        print "        [-g pdbqt_filename] (rigid output filename)"
        print "        [-x pdbqt_filename] (flexible output filename)"

    # process command arguments
    try:
        opt_list, args = getopt.getopt(sys.argv[1:], 'l:r:vs:N:P:g:x:h')
    except getopt.GetoptError, msg:
        print 'prepare_flexdocking4.py: %s' %msg
        usage()
        sys.exit(2)

    # initialize required parameters
    #-l: ligand
    ligand_filename =  None
    #-r: ligand
    receptor_filename =  None
    #-s: residues_to_move
    residues_to_move =  None
    # optional parameters
    verbose = None
    #-N: type of bonds to  disallow
    disallow = ""
    #-P: pairs of atom names bonds between which to  disallow
    disallowed_pairs = ""
    #-g  : rigid output filename
    rigid_filename = None
    #-x  : flexible output filename
    flex_filename = None

    #'l:r:vs:N:g:x:h'
    for o, a in opt_list:
        #print "o=", o, " a=", a
        if o in ('-l', '--l'):
            ligand_filename = a
            if verbose: print 'set ligand_filename to ', a
        if o in ('-r', '--r'):
            receptor_filename = a
            if verbose: print 'set receptor_filename to ', a
        if o in ('-v', '--v'):
            verbose = True
            if verbose: print 'set verbose to ', True
        if o in ('-s', '--s'):
            residues_to_move = a
            if verbose: print 'set residues_to_move to ', a
        if o in ('-N', '--N'):
            disallow = a
            if verbose: print 'set disallow to ', a
        if o in ('-P', '--P'):
            disallowed_pairs = a
            if verbose: print 'set disallowed_pairs to ', a
        if o in ('-g', '--g'):
            rigid_filename = a
            if verbose: print 'set rigid_filename to ', a
        if o in ('-x', '--'):
            flex_filename = a
            if verbose: print 'set flex_filename to ', a
        if o in ('-h', '--'):
            usage()
            sys.exit()


    if not  ligand_filename:
        print 'prepare_flexdocking4: ligand filename must be specified!\n'
        usage()
        sys.exit()

    if not  receptor_filename:
        print 'prepare_flexdocking4: receptor filename must be specified!\n'
        usage()
        sys.exit()

    if not  residues_to_move:
        print 'prepare_flexdocking4: residues to move must be specified!\n'
        usage()
        sys.exit()


    l = Read(ligand_filename)[0]
    l.buildBondsByDistance()
    if verbose: print 'read ', ligand_filename
    r = Read(receptor_filename)[0]
    r.buildBondsByDistance()
    if verbose: print 'read ', receptor_filename

    all_res = ResidueSet()
    res_names = residues_to_move.split('_')
    for n in res_names:
        if n.find(':')==-1:
            res = r.chains.residues.get(lambda x: x.name==n)
            all_res += res
            if verbose: print "get: adding ", res.name, " to ", all_res
        else:
            res, msg = CompoundStringSelector().select(ProteinSet([r]), n)
            all_res += res
            if verbose: print "css: adding ", res.name, " to ", all_res
    if verbose:
        print "all_res=", all_res.full_name(), 'all_res.__class__=', all_res.__class__
    #?check for duplicates
    d = {}
    for res in all_res: d[res] = 1
    all_res = d.keys()
    all_res = ResidueSet(all_res)

    #inactivate specified bonds
    #disallowed_Pairs "CA_CB:CB_CG:C_CA"
    all_bnds = BondSet()
    bnd_pairs = disallowed_pairs.split(':')
    for pair in bnd_pairs:
        names = pair.split('_')
        bnds = all_res.atoms.bonds[0].get(lambda x: x.atom1.name in names and x.atom2.name in names)
        all_bnds += bnds
   
    fdp = AD4FlexibleDockingPreparation(r, l, residues=all_res, rigid_filename=rigid_filename, 
                                            flex_filename=flex_filename,
                                            non_rotatable_bonds=all_bnds)


# To execute this command type:
# prepare_flexdocking4.py -l filename -r receptor_filename -s list_of_names_of_residues_to_move"




