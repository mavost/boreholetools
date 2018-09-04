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

class WellMarker(DipMarker):
    TYPE = (('UNKN', 'Unknown'), ('STRT','Stratigraphy'), ('LITH','Lithology'), ('FLT','Fault'), \
            ('TECH', 'Technical'))
    STRAT = (('NONE', 'None'),('MSL','Mean sea Level'), ('TERT','Tertiary'), ('CRET','Cretaceous'), \
            ('JUR', 'Jurassic'), ('TRIA', 'Triassic'))

    def __init__(self, md=0.0, dip=0.0, dazim=0.0, type=0, strat=0, wellname='UNKNOWN', wellgeometry=0, verbose=False):
        super(WellMarker, self).__init__(md, dip, dazim, wellgeometry, verbose=False)
        if strat > 0:
            self.strat = strat
            self.type = 1
        else:
            self.type = type
            self.strat = 0
        self.verbose = verbose
        self.wellname = wellname

    def __str__(self):
        return 'Well {0:s}:\n{1:s} Marker, Formation age: {2:s}, Depth: {3:8.3f}\n\t'.format(self.wellname, WellMarker.TYPE[self.type][1], \
                WellMarker.STRAT[self.strat][1], self.md) + super(WellMarker, self).__str__()

class WellMarkerLoading(object):
    def __init__(self, **kwargs):
        ############defaults
        kwargs.setdefault('welldatabase', 0)
        kwargs.setdefault('depthunit', 'ft')
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('filename_strat', 0)
        kwargs.setdefault('filename_in', 'sample-markers.txt')
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1,2,3,4,5))
        kwargs.setdefault('filename_out', 'dummy.txt')
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('verbose', False)
        
        ############variables
        self.welldatabase = kwargs['welldatabase']
        self.datadir = kwargs['datadir']
        self.filename_in = kwargs['filename_in']
        self.filename_in_lineskip = kwargs['headerlines']
        self.filename_out = kwargs['filename_out']
        #interpolate in different modes
        self.mode = kwargs['mode']
        self.depth_units = kwargs['depthunit']
        self.interpolation_interval = kwargs['interval']
        self.verbose = kwargs['verbose']

        kwargs.setdefault('incl', 0)
        kwargs.setdefault('azim', 0)
        kwargs.setdefault('age', 0)
        kwargs.setdefault('type', 0)
        kwargs.setdefault('reload_strat', False)
        if kwargs['reload_strat']:
            print('Stratigraphy reloaded')

    def __str__(self):
        return '{0:s} Marker, Formation age: {1:s}, Depth: {2:8.3f}\n\t'.format(WellMarker.TYPE[self.type][1], WellMarker.STRAT[self.strat][1], self.md) + super(WellMarker, self).__str__()
    

if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: markermath'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')

    print('Input:')
    marker = WellMarker(md=100, dip=10, dazim=0, strat=2, wellname='Dixie02')
    print(marker)
    print('Rotation starts:')
    for ang in range(15,360,15):
        marker.rotateY(-15)
        #print('Rot: ', ang, ' Result:', marker)
        print(marker)
else:
    print('Importing ' + __name__)
    
    
