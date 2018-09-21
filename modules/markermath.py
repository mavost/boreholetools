#!/usr/bin/python #Linux shebang plus chmod to make executable
#------------------------------------------------------------
# FILENAME: markermath.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
#------------------------------------------------------------
""" tools for manipulating well marker interpretation files
"""

import csv
import math
import sys

from dipmath import DipMarker
from fileio import BHReaderWriter
import welldatabase

class Stratigraphy(object):
    STRAT = {'NONE':'None','REF':'Reference Level', 'TERT':'Tertiary', 'CRET':'Cretaceous', \
            'JUR':'Jurassic', 'TRIA':'Triassic'}
    STRATORDER = ('REF', 'TERT', 'CRET', 'JUR', 'TRIA')

    def loadStratDefinition(datadir, stratdeffile, verbose=False):
        print('Opening stratigraphy definition file:')
        inargs = {'datadir' : datadir, 'filename_in':stratdeffile, \
                    'headerlines_in':1, 'columns_in':(1,2)}
        try: 
            Stratigraphy.STRAT = {}
            Stratigraphy.STRAT['NONE'] = 'None'
            Stratigraphy.STRAT['REF'] = 'Reference Level'
            stratdefreader = BHReaderWriter(**inargs)
            lines = stratdefreader.readData()
            for line in lines:
                if len(line) == 2:
                    Stratigraphy.STRAT[line[0]] = line[1]
            if verbose:
                print(Stratigraphy.STRAT)
        except:
            print('Exception: Error during conversion of stratigraphy definition data')
            sys.exit()
        print('Stratigraphy definition updated')

    def loadStratOrder(datadir, stratorderfile, verbose=False):
        print('Opening stratigraphy order/selection file:')
        inargs = {'datadir' : datadir, 'filename_in':stratorderfile, \
                    'headerlines_in':1, 'columns_in':(1,)}
        try: 
            stratorderreader = BHReaderWriter(**inargs)
            lines = stratorderreader.readData()
            seen = {'REF':1}
            result = ['REF']
            for line in lines:
                if len(line) == 1:
                    if line[0] in seen: continue
                    seen[line[0]] = 1
                    result.append(line[0])
            Stratigraphy.STRATORDER = result
            if verbose:
                print(Stratigraphy.STRATORDER)
        except:
            print('Exception: Error during conversion of stratigraphy order/selection data')
            sys.exit()
        print('Stratigraphy order/selection updated')

    def printStrat():
        print('Stratigraphy used in calculations:')
        try:
            for counter,item in enumerate(Stratigraphy.STRATORDER):
                print('\tBoundary {0:02d}:{1:>6.5}-{2:20.19}'.format(counter, item, Stratigraphy.STRAT[item]))
        except KeyError:
            print('Exception: Stratigraphy keys in definition and order files don\'t match')
            sys.exit()

class WellMarker(DipMarker):
    TYPE = {'UNKN':'Unknown', 'STRT':'Stratigraphy', 'LITH':'Lithology', 'FLT':'Fault', \
            'TECH':'Technical'}

    def __init__(self, type='UNKN', strat='NONE', md=0.0, dip=None, dazim=None, wellname='UNKNOWN', wellgeometry=0, verbose=False):
        if dip is not None and dazim is not None:
            super(WellMarker, self).__init__(md, dip, dazim, wellgeometry, verbose=False)
        else:   #no dip/dazim supplied -> just basic function
            super(WellMarker, self).__init__(md, None, None, wellgeometry, verbose=False)
        if strat != 'NONE':
            self.strat = strat
            self.type = 'STRT'
        else:
            self.type = type
            self.strat = 'NONE'
        self.verbose = verbose
        self.wellname = wellname

    def __str__(self):
        #print('Output:', self.type, self.strat, self.md)
        #Stratigraphy.printStrat()
        return 'Well {0:s}:\n{1:s} Marker, Formation age: {2:s}, Depth: {3:8.3f}\n\t'.format(self.wellname, WellMarker.TYPE[self.type], \
                Stratigraphy.STRAT[self.strat], self.md) + super(WellMarker, self).__str__()

    def outShort(self):
        return '\t{0:20.19s}\t'.format(Stratigraphy.STRAT[self.strat]) + super(WellMarker, self).__str__()

#move to welldatabase
class WellMarkerLoading(object): 
    def __init__(self, **kwargs):
        ############defaults
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('verbose', False)
        kwargs.setdefault('welldatabase', None)
        kwargs.setdefault('filename_in', 'sample-markers.txt')
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1,2,3,4,5))
        kwargs.setdefault('filename_strat_def', None)
        kwargs.setdefault('filename_strat_order', None)
        
        ############variables
        self.welldb = kwargs['welldatabase']
        self.datadir = kwargs['datadir']
        if self.welldb is None:
            self.welldb = welldatabase.WellDatabase(datadir = self.datadir)
            print('Warning: generating default WellDatabase')
            print(self.welldb)
        self.verbose = kwargs['verbose']
        
        ############update stratigraphy before loading marker file
        if kwargs['filename_strat_def']:
            Stratigraphy.loadStratDefinition(self.datadir, kwargs['filename_strat_def'], self.verbose)
        ############select markers in stratigraphy relevant for calculations
        if kwargs['filename_strat_order']:
            Stratigraphy.loadStratOrder(self.datadir, kwargs['filename_strat_order'], self.verbose)
        Stratigraphy.printStrat()
        ############load markers and match the ones mentioned in STRATORDER to the well database
        self.loadStratMarkers(kwargs['filename_in'], kwargs['headerlines_in'], kwargs['columns_in'])
        

    def loadStratMarkers(self, markerfile, headerlines=1, columns=(1,2,3,4,5)):
        print('Opening marker file:')
        inargs = {'datadir':self.datadir, 'filename_in':markerfile, \
                    'headerlines_in':headerlines, 'columns_in':columns}
        if(len(columns)) not in (3,5):
            print('Error: Column specification in marker file requires three or five rows to be supplied\n\tformat: WELL NAME, MARKER CODE, DEPTH MD [length], DIP(opt) [deg], DAZIM(opt) [deg]')
            sys.exit()
        try:
            #build dictionary of relevant markers
            validmarkers = {}
            for item in Stratigraphy.STRATORDER:
                validmarkers[item] = 1
            #read marker table
            markerreader = BHReaderWriter(**inargs)
            lines = markerreader.readData()
            for line in lines:
            #find corresponding well
                print(line)
                if len(line) in (3,5):
                    wellin = line[0]
                    markerin = line[1]
                    if len(line) == 3:
                        inargs = {'wellname':wellin, 'type':'STRAT', 'strat':markerin, 'md':float(line[2])}
                    elif line[3] == '' or line[4] == '':
                        inargs = {'wellname':wellin, 'type':'STRAT', 'strat':markerin, 'md':float(line[2])}
                    else:
                        inargs = {'wellname':wellin, 'type':'STRAT', 'strat':markerin, 'md':float(line[2]), 'dip':float(line[3]), 'dazim':float(line[4])}
                if self.verbose:
                    print('Line: {0:s}'.format(str(line)))
                    print('Inargs: {0:s}'.format(str(inargs)))
                if wellin in self.welldb.wells and markerin in validmarkers:
                    #add marker to well
                    inargs['wellgeometry'] = self.welldb.wells[wellin].geometry
                    #self.welldb.wells[wellin].markers.append(WellMarker(**inargs)) #array solution
                    self.welldb.wells[wellin].markers[markerin] = WellMarker(**inargs) #dict solution
                    if self.verbose:
                        print('Class Well: Adding stratigraphy well marker to {0} using arguments:'.format(wellin)) 
                        print(inargs)
                else:
                    print('Stratigraphy marker {0} in well {1} discarded'.format(markerin, wellin))
        except:
            print('Exception: Error during conversion of marker file')
            sys.exit()
        print('Well markers successfully loaded to well database')
        if self.verbose:
            self.printStratMarkers()

    def printStratMarkers(self):
            for well in dict(sorted(self.welldb.wells.items(), key=lambda x: x[0])):
                current = self.welldb.wells[well]
                print(current)
                try:
                    for counter,markertab in enumerate(Stratigraphy.STRATORDER):
                        if markertab in current.markers:
                            print('{0:02d}:{1}'.format(counter, current.markers[markertab].outShort()))
                        else:
                            print('{0:02d}:{1}'.format(counter, 'None'))
                    print('----')
                except KeyError:
                    print('Exception: printStratMarkers output error')
                    sys.exit()


if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: markermath'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')
    print('Testing: Class DipMarker')
    print('Input:')
    marker = WellMarker(md=100, dip=10, dazim=0, strat='TERT', wellname='Dixie02')
    print(marker)
    print('Rotation starts:')
    for ang in range(15,360,15):
        marker.rotateY(-15)
        #print('Rot: ', ang, ' Result:', marker)
        print(marker)
    print(TWIDTH*'=')
    print('Testing: Class WellMarker')
    inargs = {'datadir':'..\\data', 'filename_strat_def':'sample-stratdef.txt', 'filename_strat_order':'sample-stratorder.txt',\
              'verbose':True}
    loading = WellMarkerLoading(**inargs)
    loading.printStratMarkers()
    
else:
    print('Importing ' + __name__)
    
    
