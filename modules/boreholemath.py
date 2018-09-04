#!/usr/bin/python #Linux shebang plus chmod to make executable
#------------------------------------------------------------
# FILENAME: boreholemath.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
#------------------------------------------------------------
""" tools for manipulating borehole coordinate files
"""

import csv
import math
import sys
from re import match

from fileio import BHReaderWriter


class CartPoint(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):											# overloading string operator
        return 'X(Northing): {0:14.2f}, Y(Easting): {1:14.2f}, Z(TVD): {:10.2f}'.format(self.x, self.y, self.z)

    def __add__(self, incr):
        return CartPoint(self.x + incr.x, self.y + incr.y, self.z + incr.z)

    def scaleXY(self, scaler=.3048):
        self.x *= scaler
        self.y *= scaler

    def scale(self, scaler=1.0):
        self.x *= scaler
        self.y *= scaler
        self.z *= scaler

    def outputList(self):
        width = 14
        precision = 2
        out = [self.x, self.y, self.z]
        return [f'{i:{width}.{precision}f}' for i in out]

class CLPoint(object):
    #point class for curvelinear coordinates and associated tangential unity vector
    def __init__(self, md=0.0, incl=0.0, azim=0.0):
        #set md and angles and calculate tangential unity vector
        self.md = md
        self.incl = math.radians(incl)
        self.azim = math.radians(azim)
        self.tangN = math.sin(self.incl) * math.cos(self.azim)
        self.tangE = math.sin(self.incl) * math.sin(self.azim)
        self.tangV = math.cos(self.incl)

    def __str__(self):											# overloading string operator
        return 'MD: {0:10.2f}, Inclination: {1:8.3f}, Azimuth: {2:8.3f}'.format(self.md, math.degrees(self.incl), math.degrees(self.azim))
    
    def updateAngles(self, tangN, tangE, tangV):
        #back-calculate angles from updated tangential vetor
        self.tangN = tangN
        self.tangE = tangE
        self.tangV = tangV
        #angle handling hopefully correct
        if(abs(self.tangV) < 0.0001):
            # horizontal horehole case
            self.incl = 0.0
        else:
            # -PI < theta <=PI
            self.incl = math.atan(math.sqrt(self.tangN*self.tangN + self.tangE*self.tangE)/self.tangV)
        # 0 <= phi <2 * PI
        self.azim = (math.pi * 2.0 + math.atan2(self.tangE, self.tangN))%(math.pi * 2.0)

    def outputList(self):
        return [f'{self.md:{10}.{2}f}', f'{math.degrees(self.incl):{10}.{5}f}', f'{math.degrees(self.azim):{10}.{5}f}']


class MinCurvPair(object):
    def __init__(self, point_A, point_B):
        self.pA = point_A
        self.pB = point_B
        self.deltaMD = self.pB.md - self.pA.md
        self.alpha = self.calcSubtendedAlpha()
        self.dls = self.calcDogLegSeverity()
        self.shapefactor = self.calcShapeFactor()
        
    def __str__(self):											# overloading string operator
            return 'dMD: {0:8.2f}, Alpha: {1:10.3f}, DLS: {2:10.5f}, S-factor: {3:10.7f}'.format(self.deltaMD, math.degrees(self.alpha), self.dls, self.shapefactor)
    
    def calcSubtendedAlpha(self):
        factor_a = math.sin((self.pB.incl - self.pA.incl) / 2)
        factor_b = math.sin((self.pB.azim - self.pA.azim) / 2)
        return 2 * math.asin( math.sqrt(factor_a * factor_a + math.sin(self.pB.incl) * math.sin(self.pA.incl) * factor_b * factor_b))
        
    def calcDogLegSeverity(self):
        return math.degrees(self.alpha) * 100.0 / self.deltaMD

    def calcShapeFactor(self):
        if self.alpha < 0.02:
            alpha2 = self.alpha * self.alpha
            return 1 + alpha2 / 12 * (1 + alpha2 / 10 * (1 + alpha2 / 168 * (1 + 31 * alpha2 / 18)))
        else:
            return math.tan(self.alpha / 2) / (self.alpha / 2)

    def calcInterpolationMD(self, depth):
        #if coincidal with first point of MinCurvPair: copy
        if abs(depth)<0.0001:
            return self.pA
        #if coincidal with second point of MinCurvPair: copy
        elif abs(depth-self.deltaMD)<0.0001:
            return self.pB
        #otherwise approximate (normal case)
        else:
            point = CLPoint(self.pA.md + depth, 0.0, 0.0)
            #generate angle approximation
            alphastar = depth / self.deltaMD * self.alpha
            antialphastar = (1 - depth / self.deltaMD) * self.alpha
            #generate angle coefficients (also for small angles)
            tangA = self.calcTangentialFactor(antialphastar, 1 - depth/self.deltaMD)
            tangB = self.calcTangentialFactor(alphastar, depth/self.deltaMD)
            #generate vector components (also for small angles)
            tangNstar = self.pA.tangN * tangA + self.pB.tangN * tangB
            tangEstar = self.pA.tangE * tangA + self.pB.tangE * tangB
            tangVstar = self.pA.tangV * tangA + self.pB.tangV * tangB
            #update inclination / azimuth
            point.updateAngles(tangNstar, tangEstar, tangVstar)
            return point

    def calcTangentialFactor(self, alphastarcomp, fraction):
        #check for angle approximation stability according to paper's instructions
        if self.alpha >= 0.02:
            return math.sin(alphastarcomp) / math.sin(self.alpha)
        elif abs(self.alpha) <= 0.0001:
            return fraction
        else:
            alpha2 = self.alpha * self.alpha
            fraction2 = fraction * fraction
            return fraction + alpha2 * (fraction * (1.0 / 6.0 + fraction2 / 6.0) + alpha2 * (fraction * (7.0 / 360.0 + fraction2 * (-1.0 / 36.0 + fraction2 / 120.0)) + \
                    alpha2 * (fraction * (31.0 / 15120.0 + fraction2 * (-7.0 / 2160.0 + fraction2 * (1.0 / 720.0 - fraction2 / 5040.0))) + \
                    fraction * alpha2 * (127.0 / 604800.0 + fraction2 * (-31.0 / 90720.0 + fraction2 * (7.0 / 43200.0 + fraction2 * (-1.0 / 30240.0 + fraction2 / 362880.0)))))))


        
class TransformBoreHoleSurvey(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('wellname', 'UNKNOWN')
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('filename_in', 'sample-borehole.txt')
        kwargs.setdefault('headerlines', 1)
        kwargs.setdefault('columns_in', (1,2,3))
        kwargs.setdefault('filename_out', 'dummy.txt')
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('depthunit', 'ft')
        kwargs.setdefault('interval', 50.0)
        kwargs.setdefault('relativeCoords', 1)
        kwargs.setdefault('origin', (1000.0, 2000.0, 3000.0))
        kwargs.setdefault('verbose', False)
        


        ############Variables
        self.wellname = kwargs['wellname']
        self.datadir = kwargs['datadir']
        #catching an empty input survey filename
        if kwargs['filename_in'] == None:
            print('Warning: Using default deviation survey')
            kwargs['filename_in'] = 'sample-borehole.txt'
        self.filename_in = kwargs['filename_in']
        self.filename_out = kwargs['filename_out']
        #interpolate in different modes
        self.mode = kwargs['mode']
        self.depth_units = kwargs['depthunit']
        self.interpolation_interval = kwargs['interval']
        self.verbose = kwargs['verbose']
        
        # MD/INCL/AZIM columns in input file
        try:
            # generate reader object and check file for existence
            self.reader = BHReaderWriter(**kwargs)
            self.reader.readHead()
        except FileNotFoundError:
                print('Exception: Deviation survey file not found - using default deviation survey')
                kwargs['filename_in'] = 'sample-borehole.txt'
                self.reader = BHReaderWriter(**kwargs)
        
        #for blank wells try parsing well name from deviation file header
        if(self.wellname == 'UNKNOWN'):
            #join the original list of strings back together and match by regular expression
            lines = self.reader.readHead()
            for line in lines:
                res_match = match(r"(?i)well:\s*(\S*?),", line)
                if(res_match):
                    self.wellname = res_match.group(1)
                    print('Reading well name from file successful: {0:s}'.format(self.wellname))
            
        #output absolute or relative Cartesian coordinates
        if kwargs['relativeCoords'] != 1:
            self.relativeCoords = False
            self.origin = kwargs['origin']
            if len(self.origin) != 3:
                raise('Exception: Borehole origin in wrong format - needs to be (X(N), Y(E), Z(TVD))')
                sys.exit()
        else:
            self.relativeCoords = True
            self.origin = (0.0, 0.0, 0.0)

        ############Main
        self.survey_points = []
        self.curve_pairs = []
        self.interpolation_points = []
        self.cartesian_points =[]
        
        #load, convert, setup data for calculations
        lines = self.reader.readData()
        try:
            first = float(lines[0][0]) 
            # check first depth value to be non-negative
            if first < 0.0:
                raise Exception('Exception: first MD value is negative')
            # check first depth value to be at KB or add surface point
            elif first >=0.0001:
                self.survey_points.append(CLPoint(0.0,0.0,0.0))
                print('Warning: Adding surface point to survey data')
        except ValueError:
            print('Exception: Error during conversion of survey data')
            sys.exit()
        except Exception:
            print(Exception)
            sys.exit()
        prev = -1
        for line in lines:
            try:
                # convert data to numbers and check for depth-sorting
                line = [float(i) for i in line]
                md = line[0]
                if md < prev:
                    raise Exception('Exception: MD values are not ascending')
                prev = md
                self.survey_points.append(CLPoint(*line))
            except ValueError:
                print('Exception: Error during conversion of survey data')
                sys.exit()
            except Exception:
                print(Exception)
                sys.exit()
        self.setupMinCurvPairs(self.survey_points)

        #calculate and optionally output
        self.generateOutput(self.mode)
        

    def generateOutput(self, mode=0):
        if 0 < mode < 4:
            #generate Cartesian coordinate file from original curvelinear coordinate file
            wellnote = 'Well: ' + self.wellname
            self.filename_out = self.wellname 
            if mode == 1:
                self.cartesian_points =[]
                self.buildCartesianPoints()
                self.filename_out+='_out_borehole_cart_orig.txt'
                if(self.relativeCoords):
                    outheader = (wellnote, 'dX(N) [m]', 'dY(E) [m]', 'dZ(TVD) ['+self.depth_units+']')
                else:
                    outheader = (wellnote, 'X(N) [m]', 'Y(E) [m]', 'Z(TVD) ['+self.depth_units+']')
                pointlist = self.cartesian_points
#               for row in self.cartesian_points:
#                  print(row)
            #generate interpolation points and output curvelinear coordinate file
            elif mode == 2:
                self.interpolation_points = []
                self.setupCLPoints()
                self.interpolateCLPoints()
                self.filename_out+='_out_borehole_curve_inter.txt'
                outheader = (wellnote, 'MD ['+self.depth_units+']', 'INCL [deg]', 'AZIM [deg]')
                pointlist = self.interpolation_points
            
            #generate and output Cartesian coordinate file from interpolated data
            elif mode == 3:
                self.interpolation_points = []
                self.setupCLPoints()
                self.interpolateCLPoints()
                self.curve_pairs = []
                self.setupMinCurvPairs(self.interpolation_points)
                self.cartesian_points =[]
                self.buildCartesianPoints()
                self.filename_out+='_out_borehole_cart_inter.txt'
                if(self.relativeCoords):
                    outheader = (wellnote, 'dX(N) [m]', 'dY(E) [m]', 'dZ(TVD) ['+self.depth_units+']')
                else:
                    outheader = (wellnote, 'X(N) [m]', 'Y(E) [m]', 'Z(TVD) ['+self.depth_units+']')
                pointlist = self.cartesian_points
#               for row in self.cartesian_points:
#                   print(row)
            outdata = []
            for item in pointlist:
                outdata.append(item.outputList())
            outargs={'datadir' : self.datadir, 'filename_out' : self.filename_out, \
                'header_out' : outheader, 'data_out' : outdata, 'verbose' : self.verbose}
            writer = BHReaderWriter(**outargs)
            writer.writeData()
        else:
            print('No output file generated')

    def setupMinCurvPairs(self, clpoints):
        #build list of curve pairs and calculate min. curvature parameters
        for pairs in zip(clpoints[0:-1], clpoints[1:]):
            #print(pairs[0],'\n',pairs[1],'\n')
            self.curve_pairs.append(MinCurvPair(pairs[0], pairs[1]))
        if self.verbose : 
            print('Number of MinCurv pairs generated: ', len(self.curve_pairs))
            for pair in self.curve_pairs:
                print(pair)

    def buildCartesianPoints(self):
        current = CartPoint(self.origin[0], self.origin[1], -self.origin[2])
        self.cartesian_points.append(current)
        if self.depth_units == 'ft':
            for curvepair in self.curve_pairs:
                delta = self.calculateCartesianDeltas(curvepair)
                delta.scaleXY()
                current += delta
                self.cartesian_points.append(current)
        else:
            for curvepair in self.curve_pairs:
                delta = self.calculateCartesianDeltas(curvepair)
                current += delta
                self.cartesian_points.append(current)

    def calculateCartesianDeltas(self, pair):
        dx = math.sin(pair.pA.incl) * math.cos(pair.pA.azim) + math.sin(pair.pB.incl) * math.cos(pair.pB.azim)
        dy = math.sin(pair.pA.incl) * math.sin(pair.pA.azim) +math.sin(pair.pB.incl) * math.sin(pair.pB.azim)
        dz = math.cos(pair.pA.incl) + math.cos(pair.pB.incl)
        deltas = CartPoint(dx, dy, dz)
        scaler = pair.deltaMD * pair.shapefactor / 2.0
        deltas.scale(scaler)
        return deltas

    def setupCLPoints(self):
        #build list of interpolation points and fill with MD values
        min_depth = self.survey_points[0].md
        max_depth = self.survey_points[-1].md
        #integer division - number of flagpoles
        points = int((max_depth - min_depth) // self.interpolation_interval) + 1
        for point in range(points):
            self.interpolation_points.append(CLPoint(min_depth + self.interpolation_interval * point, 0.0, 0.0))
        #check for sampling interval without overlap or add last survey point
        residual = (max_depth - min_depth) % self.interpolation_interval
        if residual > 0.001:
            self.interpolation_points.append(CLPoint(max_depth, 0.0, 0.0))
        if self.verbose : 
            print('MinDepth: ', min_depth)
            print('MaxDepth: ', max_depth)
            print('Interval:', self.interpolation_interval)
            print('Evenly-Spaced Points: ', points)
            print('Residual: ', residual)
            print('Number of interpolation points: ', len(self.interpolation_points))
    
    def interpolateCLPoints(self):
        dataiter = iter(self.curve_pairs)
        #point iterator to first MinCurvPair 
        curvepair = next(dataiter)
        #loop over all interpolation points
        for index, ipoint in enumerate(self.interpolation_points):
            #move to MinCurvPair containing the interpolation point
            while ipoint.md > curvepair.pB.md: 
                curvepair = next(dataiter)
            idepth = ipoint.md-curvepair.pA.md
            self.interpolation_points[index] = curvepair.calcInterpolationMD(idepth)
            if self.verbose :
                print('Interval {0:8.2f} to {1:8.2f} used to interpolate point {2:8.2f}'.format(curvepair.pA.md, curvepair.pB.md, ipoint.md))
        if self.verbose : 
            print('RESULT:\n')
            for point in self.interpolation_points:
                print(point)

    def calculateCLPoint(self, mdepth):
        min = self.curve_pairs[0].pA.md
        max = self.curve_pairs[-1].pB.md
        if mdepth < min:
            mdepth = min
            print('Warning: Depth extrapolation beyond well data was shortened')
        if mdepth > max:
            mdepth = max
            print('Warning: Depth extrapolation beyond well data was shortened')
        dataiter = iter(self.curve_pairs)
        #point iterator to first MinCurvPair 
        curvepair = next(dataiter)
        #move to MinCurvPair containing the interpolation point
        while mdepth > curvepair.pB.md:
            curvepair = next(dataiter)
        idepth = mdepth-curvepair.pA.md
        point = CLPoint(mdepth, 0.0, 0.0)
        point = curvepair.calcInterpolationMD(idepth)
        if self.verbose :
                print('Interval {0:8.2f} to {1:8.2f} used to interpolate point {2:8.2f}'.format(curvepair.pA.md, curvepair.pB.md, mdepth))
                print(point)
        return point
                
        


if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: boreholemath'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')
    transform = TransformBoreHoleSurvey(datadir='..\\data', mode=1, relativeCoords=0, origin=(-100, -200, 100), verbose=False)
    transform.generateOutput(mode=2)
    transform.generateOutput(mode=3)
    #print(transform.calculateCLPoint(-102))
else:
    print('Importing ' + __name__)