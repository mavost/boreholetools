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
import markermath

class Well(object):
    #define static variables and helper functions to force consistent length handling across well data
    DEPTHUNIT = 'ft'
    SURFUNIT = 'ft'
    VERBOSE = False

    def depthToMetric():
        Well.DEPTHUNIT = 'm'
        if Well.VERBOSE:
            print('Depth units switched to Metric')
        
    def depthToImperial():
        Well.DEPTHUNIT = 'ft'
        if Well.VERBOSE:
            print('Depth units switched to Imperial')

    def surfToMetric():
        Well.SURFUNIT = 'm'
        if Well.VERBOSE:
            print('Surface units switched to Metric')
        
    def surfToImperial():
        Well.SURFUNIT = 'ft'
        if Well.VERBOSE:
            print('Surface units switched to Imperial')

    def switchVerbose():
        if Well.VERBOSE:
            Well.VERBOSE = False
        else:
            Well.VERBOSE = True

    def __init__(self, **kwargs):
        print(kwargs)
        ############defaults
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('filename_in', 'sample-borehole.txt')
        kwargs.setdefault('wellname', 'UNKNOWN')
        kwargs.setdefault('origin', (0.0, 0.0, 0.0))
        #default values for deviation file shape
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1,2,3))
        #default values for survey handling
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('interval', 50)
        
        ############variables
        self.wellname = kwargs['wellname']
        #(N(X), E(Y), KB) with KB being a positive number above reference level
        self.wellorigin = kwargs['origin']
        #Well.DEPTHUNIT, Well.SURFUNIT, Well.VERBOSE set by helper function
        
        devinargs = {'depthunit':Well.DEPTHUNIT, 'surfaceunits':Well.SURFUNIT, 'verbose':Well.VERBOSE, \
                'datadir':kwargs['datadir'], 'filename_in':kwargs['filename_in'], 'wellname':self.wellname, 'origin':self.wellorigin, \
                'headerlines_in':kwargs['headerlines_in'], 'columns_in':kwargs['columns_in'], \
                'relativeCoords':False, 'mode':kwargs['mode'], 'interval':kwargs['interval']}
        self.geometry = TransformBoreHoleSurvey(**devinargs)
        self.markers = {} #keys are formation codes - do we need to allow for multiple entries in one key? 
                          #-> not for geometry purpose (else use subscripted key TERT_A /TERT_B)
        #self.markers = [] #alternatively list

    def __str__(self):
        return 'Well name: {0:s}, X: {1:10.1f}, Y: {2:10.1f}, KB: {3:6.1f}'.format(self.wellname, *self.wellorigin)

class WellDatabase(object):
    def __init__(self, **kwargs):
        print(kwargs)
        ############defaults
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('verbose', False)
        kwargs.setdefault('depthunit', 'ft')
        kwargs.setdefault('surfaceunits', 'ft')
        kwargs.setdefault('filename_in','sample-wellheads.txt')
        #default values for header file shape
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1,2,3,4,5))
        #default values for survey handling
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('interval', 50)

        ############variables
        self.wells = {} #dictionary
        self.verbose = kwargs['verbose']
        if self.verbose:
            Well.switchVerbose()
            print('Opening well head file:')
        welldbinargs = {'datadir':kwargs['datadir'], 'filename_in':kwargs['filename_in'], \
                        'headerlines_in':kwargs['headerlines_in'], 'columns_in':kwargs['columns_in']}
        headreader = BHReaderWriter(**welldbinargs)
        lines = headreader.readData()
        if kwargs['depthunit'] == 'm':
            Well.depthToMetric()
        if kwargs['surfaceunits'] == 'm':
            Well.surfToMetric()
        for line in lines:    
            try:
                # convert data to numbers and check for depth-sorting
                wname = line[0]
                wcoordinates = tuple([float(i) for i in line[1:4]])
                wfname = line[4]
                wellinargs = {'datadir':kwargs['datadir'], 'wellname':wname, 'origin':wcoordinates, \
                              'filename_in':wfname, 'mode':kwargs['mode'], 'interval':kwargs['interval']}
                if wname not in self.wells:
                    self.wells[wname]=Well(**wellinargs)
                else:
                    print('Warning: Double occurence of name in well head file, keeping first instance')
            except ValueError:
                    print('Exception: Error during conversion of well head data')
                    sys.exit()
            print('Input Name: {0:s}, X: {1:10.1f}, Y: {2:10.1f}, KB: {3:6.1f}'.format(wname, *wcoordinates))
            print(str(self.wells[wname]))

    def getWellsSorted(self):
        return dict(sorted(self.wells.items(), key=lambda x: x[0]))

    def __str__(self):
        return 'Number of wells loaded: {0:4d}'.format(len(self.wells))

            
if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: welldatabase'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')
    print('Testing: Class Well')
    well = Well(datadir='..\\data', verbose=True)
    print(well)
    Well.depthToMetric()
    print(TWIDTH*'=')
    print('Testing: Class WellDatabase')
    print('Opening well head file and creating well database:')
    try:
        inargs = {'datadir':'..\\data', 'filename_in':'sample-wellheads.txt', \
                  'mode':3, 'verbose':False}
        welldb = WellDatabase(**inargs)
        print(welldb)
    except:
        print('Exception: Something went wrong during building of well database')
        sys.exit()
    print(TWIDTH*'=')
    print('Testing: glob module')
    mylist = [f for f in glob.glob('..\\data\\out*.txt')]
    print(mylist)
    print(TWIDTH*'=')
else:
    print('Importing ' + __name__)
    
    
