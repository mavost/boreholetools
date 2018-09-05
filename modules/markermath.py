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
from welldatabase import WellDatabase

class WellMarker(DipMarker):
    TYPE = {'UNKN':'Unknown', 'STRT':'Stratigraphy', 'LITH':'Lithology', 'FLT':'Fault', \
            'TECH':'Technical'}
    STRAT = {'NONE':'None','MSL':'Mean sea Level', 'TERT':'Tertiary', 'CRET':'Cretaceous', \
            'JUR':'Jurassic', 'TRIA':'Triassic'}
    STRATORDER = ('MSL', 'TERT', 'CRET', 'JUR', 'TRIA')

    def __init__(self, md=0.0, dip=0.0, dazim=0.0, type='UNKN', strat='NONE', wellname='UNKNOWN', wellgeometry=0, verbose=False):
        super(WellMarker, self).__init__(md, dip, dazim, wellgeometry, verbose=False)
        if strat != 'NONE':
            self.strat = strat
            self.type = 'STRT'
        else:
            self.type = type
            self.strat = 'NONE'
        self.verbose = verbose
        self.wellname = wellname

    def __str__(self):
        return 'Well {0:s}:\n{1:s} Marker, Formation age: {2:s}, Depth: {3:8.3f}\n\t'.format(self.wellname, WellMarker.TYPE[self.type], \
                WellMarker.STRAT[self.strat], self.md) + super(WellMarker, self).__str__()

class WellMarkerLoading(object):
    def __init__(self, **kwargs):
        ############defaults
        kwargs.setdefault('welldatabase', None)
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('filename_strat', None)
        kwargs.setdefault('filename_in', 'sample-markers.txt')
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1,2,3,4,5))
        kwargs.setdefault('filename_out', 'dummy.txt')
        kwargs.setdefault('verbose', False)
        
        ############variables
        self.welldatabase = kwargs['welldatabase']
        if self.welldatabase is None:
            self.welldatabase = WellDatabase()
            print('Warning: generating default WellDatabase')
        self.verbose = kwargs['verbose']

        if kwargs['reload_strat']:
            print('Stratigraphy reloaded')

    def __str__(self):
        return '{0:s} Marker, Formation age: {1:s}, Depth: {2:8.3f}\n\t'.format(WellMarker.TYPE[self.type][1], WellMarker.STRAT[self.strat][1], self.md) + super(WellMarker, self).__str__()
    

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
    print('Testing: Class DipMarker')
    loading = WellMarkerLoading()
else:
    print('Importing ' + __name__)
    
    
