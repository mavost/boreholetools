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
    def __init__(self, md=0.0, dip=0.0, dazim=0.0, type='UNKN', strat='NONE', wellname='UNKNOWN', wellgeometry=0, verbose=0):
        super(WellMarker, self).__init__(md, dip, dazim, wellgeometry, verbose=0)
        self.verbose = verbose
        self.type = type
        self.strat = strat
        self.wellname = wellname

    def __str__(self):
        return '{0:s} Marker, Formation age: {1:s}, Depth: {2:8.3f}\n\t'.format(WellMarker.TYPE[self.type][1], WellMarker.STRAT[self.strat][1], self.md) + super(WellMarker, self).__str__()

class WellMarkerLoading(object):
    TYPE = (('UNKN', 'Unknown'), ('STRT','Stratigraphy'), ('LITH','Lithology'), ('FLT','Fault'), \
            ('TECH', 'Technical'))
    STRAT = (('NONE', 'None'),('MSL','Mean sea Level'), ('TERT','Tertiary'), ('CRET','Cretaceous'), \
            ('JUR', 'Jurassic'), ('TRIA', 'Triassic'))
    
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
        kwargs.setdefault('verbose', 0)
        
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
        self.verbose = bool(kwargs['verbose'])

        kwargs.setdefault('incl', 0)
        kwargs.setdefault('azim', 0)
        kwargs.setdefault('age', 0)
        kwargs.setdefault('type', 0)
        kwargs.setdefault('reload_strat', 0)
        if kwargs['reload_strat'] = 1:

    def __str__(self):
        return '{0:s} Marker, Formation age: {1:s}, Depth: {2:8.3f}\n\t'.format(WellMarker.TYPE[self.type][1], WellMarker.STRAT[self.strat][1], self.md) + super(WellMarker, self).__str__()
    

if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: markermath'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')

    print('Input:')
    marker = WellMarker(age=2, md=100, incl=10, azim=0)
    print(marker)
    print('Rotation starts:')
    for ang in range(15,360,15):
        marker.rotateY(-15)
        #print('Rot: ', ang, ' Result:', marker)
    print(marker)
else:
    print('Importing ' + __name__)
    
    
