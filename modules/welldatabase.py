#!/usr/bin/python #Linux shebang plus chmod to make executable
#------------------------------------------------------------
# FILENAME: welldatabase.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
#------------------------------------------------------------
""" tools for setting up well database
"""

import csv
import math
import sys
import glob

from boreholemath import TransformBoreHoleSurvey
from fileio import BHReaderWriter

class Well(object):
    DEPTHUNIT = 'ft'
    VERBOSE = 0
    def __init__(self, wellfile=0, wellname='UNKNOWN', origin=(0.0, 0.0, 0.0), verbose=0):
        self.wellname = wellname
        inargs = {'depthunit' : Well.DEPTHUNIT, 'mode' : 0, 'datadir' : '..\\data', 'filename_in' : wellfile, 'wellname' : wellname, \
                'headerlines' : 1, 'columns_in' : (1,2,3), 'verbose' : verbose, 'relativeCoords' : 0, 'origin' : origin, 'mode' : 1}
        self.geometry = TransformBoreHoleSurvey(**inargs)
        if verbose > 0:
            Well.VERBOSE = True
        self.wellorigin = origin #(N, E, KB) with KB being a positive number above reference level

    def depthToMetric(self):
        Well.DEPTHUNIT = 'm'
        if Well.VERBOSE:
            print('Depth units switched to Metric')
        
    def depthToImperial(self):
        Well.DEPTHUNIT = 'ft'
        if Well.VERBOSE:
            print('Depth units switched to Imperial')

    def __str__(self):
        return 'Well name: {0:s}, X: {1:10.1f}, Y: {2:10.1f}, KB: {3:6.1f}'.format(self.wellname, *self.wellorigin)

class WellDatabase(object):
    def __init__(self, **kwargs):
        ############defaults
        kwargs.setdefault('depthunit', 'ft')
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1,2,3))
        kwargs.setdefault('filename_out_ext', 'out_')
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('verbose', 0)

        ############variables
        self.wells = []
        self.datadir = kwargs['datadir']
        self.filename_out_ext = kwargs['filename_out_ext']
        self.mode = kwargs['mode']
        self.depth_units = kwargs['depthunit']
        self.interpolation_interval = kwargs['interval']
        self.verbose = bool(kwargs['verbose'])
        
    def addWell(self, filename, wellname, origin):
        self.wells.append(Well(filename, wellname, origin))
    

if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: welldatabase'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')
    print('Testing: Class Well')
    well = Well(verbose=1)
    print(well)
    well.depthToMetric()
    print(TWIDTH*'=')
    print('Testing: Class WellDatabase')
    print('Opening well head file:')
    inargs = {'datadir' : '..\\data', 'filename_in':'sample-wellheads.txt', \
                'headerlines':1, 'columns_in':(1,2,3,4,5)}
    reader = BHReaderWriter(**inargs)
    lines = reader.readData()
    welldb = []
    for line in lines:    
        try:
            # convert data to numbers and check for depth-sorting
            wname = line[0]
            wcoordinates = tuple([float(i) for i in line[1:4]])
            wfname = line[4]
            welldb.append(Well(wellfile=wfname, wellname=wname, origin=wcoordinates, verbose=0))
        except ValueError:
                print('Exception: Error during conversion of well head data')
                sys.exit()
        print('Input Name: {0:s}, X: {1:10.1f}, Y: {2:10.1f}, KB: {3:6.1f}'.format(wname, *wcoordinates))
        print(str(welldb[-1]))
    mylist = [f for f in glob.glob('..\\data\\out*.txt')]
    print(mylist)
    print(TWIDTH*'=')
else:
    print('Importing ' + __name__)
    
    
