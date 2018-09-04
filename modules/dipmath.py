#!/usr/bin/python #Linux shebang plus chmod to make executable
#------------------------------------------------------------
# FILENAME: dipmath.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
#------------------------------------------------------------
""" tools for manipulating dipmeter interpretation files
"""

import csv
import math
import sys

from boreholemath import TransformBoreHoleSurvey
from fileio import BHReaderWriter

class DipPoint(object):
    @staticmethod
    def getMatX(angle):
        return [[1.0, 0.0, 0.0], \
                [0.0, math.cos(angle), -math.sin(angle)], \
                [0.0, math.sin(angle), math.cos(angle)]]
    
    @staticmethod
    def getMatY(angle):
        return [[math.cos(angle), 0.0, math.sin(angle)], \
                [0.0, 1.0, 0.0], \
                [-math.sin(angle), 0.0, math.cos(angle)]]

    @staticmethod
    def getMatZ(angle):
        return [[math.cos(angle), -math.sin(angle), 0.0], \
                [math.sin(angle), math.cos(angle), 0.0], \
                [0.0, 0.0, 1.0]]

    def __init__(self, dip=0.0, dazim=0.0):
        #debug output
        self.verbose = 1
        #inclination angle between reference frame XY-plane and max falling dip 0 <= dip < pi
        self.dip = (math.pi + math.radians(dip)) % math.pi
        #azimuth angle projected to XY-plane, referenced to X-axis 0 <= dazim < 2*pi
        self.dazim = (math.pi * 2.0 + math.radians(dazim)) % (math.pi * 2.0)
        #define a unit vector pointing in direction of maximum falling dip
        #defaults to 1,0,0
        self.dipN = math.cos(self.dip) * math.cos(self.dazim)
        self.dipE = math.cos(self.dip) * math.sin(self.dazim)
        self.dipV = math.sin(self.dip)
    
    def updateAngles(self, newdips):
        #back-calculate angles from updated tangential vetor
        try:
            if len(newdips) != 3:
                raise Exception('Exception: Angle update failed.')
                sys.exit()
            length = math.sqrt(newdips[0]*newdips[0]+newdips[1]*newdips[1]+newdips[2]*newdips[2])
            if length>0:
                #if dip vector is too long - rescale to unit vector
                self.dipN = newdips[0] / length
                self.dipE = newdips[1] / length
                self.dipV = newdips[2] / length
            else:
                raise Exception('Exception: Dip vector is empty.')
            horiz = math.sqrt(self.dipN * self.dipN + self.dipE * self.dipE)
            self.dip = math.acos(horiz)
            self.dazim = (math.pi * 2.0 + math.atan2(self.dipE, self.dipN)) % (math.pi * 2.0)
            if self.verbose:
                #print('New tangential vector:')
                print('              X: {0:7.2f}, Y: {1:7.2f}, Z: {2:7.2f}'.format(*newdips))
                print('              Dip: {0:8.3f}, Azimuth: {1:8.3f}'.format(math.degrees(self.dip), math.degrees(self.dazim)))
        except:
            print('Exception: Angle update failed - further error')
    
    def __str__(self):
        # overloading string operator
        return 'Dip: {0:8.3f}, Azimuth: {1:8.3f}'.format(math.degrees(self.dip), math.degrees(self.dazim))
    
    def rotate(self, matrixFunc, angle):
        angrad = math.radians(angle)
        matrix = matrixFunc(angrad)
        in_vec = [self.dipN, self.dipE, self.dipV]
        res_vec = [0.0, 0.0, 0.0]
        for i in range(3):
            for j in range(3):
                res_vec[i] += matrix[i][j] * in_vec[j]
        return res_vec

    def rotateX(self, angle):
        vec = self.rotate(DipPoint.getMatX, angle)
        self.updateAngles(vec)

    def rotateY(self, angle):
        vec = self.rotate(DipPoint.getMatY, angle)
        self.updateAngles(vec)

    def rotateZ(self, angle):
        vec = self.rotate(DipPoint.getMatZ, angle)
        self.updateAngles(vec)
        
class DipMarker(DipPoint):
    def __init__(self, md, dip, dazim, wellgeometry=0, verbose=0):
        self.md = md
        self.in_dip = math.radians(dip)
        self.in_dazim = math.radians(dazim)
        #conversion to radians in DipPoint class
        super(DipMarker, self).__init__(dip, dazim)
        self.verbose = verbose
        if self.verbose:
            print(self)
        if wellgeometry!=0:
            self.clpoint = wellgeometry.calculateCLPoint(self.md)
            if self.verbose:
                print('Dipmarker correction:')
                print('MD: {0:8.2f}, '.format(self.md) + super(DipMarker, self).__str__())
            self.reorientDip()
        

    def __str__(self):
        # overloading string operator
        return 'MD: {0:8.3f}, Dip: {1:8.3f}, Azimuth: {2:8.3f}'.format(self.md, math.degrees(self.dip), math.degrees(self.dazim))

    def outputList(self, mode=0):
        if mode==0:
            return [f'{self.md:{10}.{2}f}', f'{math.degrees(self.dip):{10}.{5}f}', f'{math.degrees(self.dazim):{10}.{5}f}']
        else:
            return [f'{self.md:{10}.{2}f}', f'{math.degrees(self.in_dip):{10}.{5}f}', f'{math.degrees(self.in_dazim):{10}.{5}f}', \
                    f'{math.degrees(self.dip):{10}.{5}f}', f'{math.degrees(self.dazim):{10}.{5}f}', \
                    f'{math.degrees(self.clpoint.incl):{10}.{5}f}', f'{math.degrees(self.clpoint.azim):{10}.{5}f}']

    def reorientDip(self):
        by_y = math.degrees(self.clpoint.incl)
        by_z = math.degrees(self.clpoint.azim)
        if self.verbose:
            print('      Borehole INCL: {0:8.3f}, Borehole AZIM: {1:8.3f}'.format(by_y, by_z))
            print('      Rotation on Y-Axis with borehole inclination: {0:8.3f}'.format(by_y))
        self.rotateY(by_y)
        if self.verbose:
            print('      Rotation on Z-Axis with borehole azimuth    : {0:8.3f}'.format(by_z))
        self.rotateZ(by_z)
        

if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: dipmath'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')

    print('Testing: Class DipPoint')
    point = DipPoint(45, 0)
    print('Input:')
    print(point)
    print('Rotation starts:')
    for ang in range(0,360,15):
        point.rotateY(15)
        #print('Rot: ', ang, ' Result:', point)
    print(TWIDTH*'=')
    print('Testing: Class DipMarker')
    #generate a borehole deviation survey / interpolation object
    wellgeometry = TransformBoreHoleSurvey(datadir='..\\data', mode=0, relativeCoords=1, verbose=0)
    #correct one marker by extracting corresponding horehole inclination/azim
    print('Apply correction on one DipMarker point:')
    #dmarker = DipMarker(5000, 45, 10, 0, verbose=1)
    dmarker = DipMarker(5000, 45, 10, wellgeometry, verbose=1)
    print(dmarker)
    #repeat the same for data read from a file
    print('Opening dipmarker file:')
    inargs = {'datadir' : '..\\data', 'filename_in':'sample-dipmarker.txt', \
                'headerlines':1, 'columns_in':(1,2,3)}
    reader = BHReaderWriter(**inargs)
    lines = reader.readData()
    result = []
    for line in lines:
        try:
            # convert data to numbers and check for depth-sorting
            line = [float(i) for i in line]
            result.append(DipMarker(*line, wellgeometry, verbose=0))
        except ValueError:
                print('Exception: Error during conversion of survey data')
                sys.exit()
        print('Before - MD: {0:8.3f}, Dip: {1:8.3f}, Azimuth: {2:8.3f}'.format(*line))
        print('After  - ' + str(result[-1]))
    print('Writing dipmarker file:')
    #mode = basic(0) or detailed(1) output
    mode = 1
    outdata = []
    for item in result:
        outdata.append(item.outputList(mode))
    if mode == 1:
        outheader = ('Well: UNKNOWN', 'MD [depthunit]', 'DIP_ORIG [deg]', 'DAZI_ORIG [deg]', 'DIP [deg]', 'DAZI [deg]', 'INCL [deg]', 'AZIM [deg]')
    else:
        outheader = ('Well: UNKNOWN', 'MD [depthunit]', 'DIP [deg]', 'DAZI [deg]')
 
    outargs = {'datadir' : '..\\data', 'filename_out' : 'out_sample-dipmarker.txt', \
            'header_out' : outheader, 'data_out' : outdata, 'verbose' : 1}
    writer = BHReaderWriter(**outargs)
    writer.writeData()
    print(TWIDTH*'=')
else:
    print('Importing ' + __name__)
    
    
