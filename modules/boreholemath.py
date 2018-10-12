#!/usr/bin/python #Linux shebang plus chmod to make executable
# ------------------------------------------------------------
# FILENAME: boreholemath.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
# ------------------------------------------------------------
# tools for manipulating borehole coordinate files


import math
import sys
from re import match

from modules import fileio


class CartPoint(object):
    """a simple point class for Cartesian coordinates"""
    def __init__(self, x=0.0, y=0.0, z=0.0):
        """
        initialize point class using three vector components

        :param x: X-component initializer
        :param y: Y-component initializer
        :param z: Z-component initializer
        """
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        """overloaded string operator"""
        return 'X(Northing): {0:14.2f}, Y(Easting): {1:14.2f}, Z(TVD): {2:10.2f}'.format(self.x, self.y, self.z)

    def __add__(self, incr):
        """overloaded addition operator in vector addition convention"""
        return CartPoint(self.x + incr.x, self.y + incr.y, self.z + incr.z)

    def scale_xy(self, scaler=.3048):
        """
        scale horizontal components of a point differently than vertical in case of mixed length unit output

        :param scaler: scaling factor defaulting to 'ft' to 'meter' constant
        """
        self.x *= scaler
        self.y *= scaler

    def scale(self, scaler=1.0):
        """
        scale all three components of a vector

        :param scaler: scaling factor defaulting to identity
        """
        self.x *= scaler
        self.y *= scaler
        self.z *= scaler

    def output_list(self):
        """
        convert three components for exporting to CSV file

        :return: three floats (X,Y,Z) formatted list of str
        """
        width = 14
        precision = 2
        out = [self.x, self.y, self.z]
        return [f'{i:{width}.{precision}f}' for i in out]


class CLPoint(object):
    """point class for curvelinear coordinates and associated tangential unit vector"""
    def __init__(self, md=0.0, incl=0.0, azim=0.0):
        """
        for given spherical coordinates set measured depth and angles and calculate a corresponding
        tangential unit vector

        :param md: measured depth of point in length units along borehole from kelly bushing (KB)
        :param incl: borehole inclination (theta) measured from vertical at point [deg]
        :param azim: borehole azimuth (phi) measured from grid North at point [deg]
        """
        self.md = md
        self.incl = math.radians(incl)
        self.azim = math.radians(azim)
        self.tangN = math.sin(self.incl) * math.cos(self.azim)
        self.tangE = math.sin(self.incl) * math.sin(self.azim)
        self.tangV = math.cos(self.incl)

    def __str__(self):
        """overloaded string operator"""
        return 'MD: {0:10.2f}, Inclination: {1:8.3f}, Azimuth: {2:8.3f}'.format(self.md, math.degrees(self.incl),
                                                                                math.degrees(self.azim))
    
    def update_angles(self, tangn, tange, tangv):
        """
        back-calculate new angles from updated tangential vector

        :param tangn: North-component of tangential vector
        :param tange: East-component of tangential vector
        :param tangv: Vertical / down-component of tangential vector
        """
        self.tangN = tangn
        self.tangE = tange
        self.tangV = tangv
        # angle handling hopefully correct
        if abs(self.tangV) < 0.0001:
            # horizontal horehole case
            self.incl = 0.0
        else:
            # -PI < theta <=PI
            self.incl = math.atan(math.sqrt(self.tangN*self.tangN + self.tangE*self.tangE)/self.tangV)
        # 0 <= phi <2 * PI
        self.azim = (math.pi * 2.0 + math.atan2(self.tangE, self.tangN)) % (math.pi * 2.0)

    def output_list(self):
        """
        convert three components for exporting to CSV file

        :return: three floats (MD[length], INCL[deg], AZIM[deg]) formatted list of str
        """
        return [f'{self.md:{10}.{2}f}', f'{math.degrees(self.incl):{10}.{5}f}', f'{math.degrees(self.azim):{10}.{5}f}']


class MinCurvPair(object):
    """

    """
    def __init__(self, pointa, pointb):
        """

        :param pointa:
        :param pointb:
        """
        self.pA = pointa
        self.pB = pointb
        self.deltaMD = self.pB.md - self.pA.md
        self.alpha = self.calc_subtended_alpha()
        self.dls = self.calc_dog_leg_severity()
        self.shapefactor = self.calc_shape_factor()
        
    def __str__(self):
            """ overloading string operator """
            return 'dMD: {0:8.2f}, Alpha: {1:10.3f},'\
                   'DLS: {2:10.5f}, S-factor: {3:10.7f}'.format(self.deltaMD, math.degrees(self.alpha),
                                                                self.dls, self.shapefactor)
    
    def calc_subtended_alpha(self):
        """

        :return:
        """
        factor_a = math.sin((self.pB.incl - self.pA.incl) / 2)
        factor_b = math.sin((self.pB.azim - self.pA.azim) / 2)
        return 2 * math.asin(math.sqrt(factor_a * factor_a + math.sin(self.pB.incl) *
                                        math.sin(self.pA.incl) * factor_b * factor_b))
        
    def calc_dog_leg_severity(self):
        """

        :return:
        """
        return math.degrees(self.alpha) * 100.0 / self.deltaMD

    def calc_shape_factor(self):
        """

        :return:
        """
        if self.alpha < 0.02:
            alpha2 = self.alpha * self.alpha
            return 1 + alpha2 / 12 * (1 + alpha2 / 10 * (1 + alpha2 / 168 * (1 + 31 * alpha2 / 18)))
        else:
            return math.tan(self.alpha / 2) / (self.alpha / 2)

    def calc_interpolation_md(self, depth):
        """

        :param depth:
        :return:
        """
        # if coincidal with first point of MinCurvPair: copy
        if abs(depth) < 0.0001:
            return self.pA
        # if coincidal with second point of MinCurvPair: copy
        elif abs(depth-self.deltaMD) < 0.0001:
            return self.pB
        # otherwise approximate (normal case)
        else:
            point = CLPoint(self.pA.md + depth, 0.0, 0.0)
            # generate angle approximation
            alphastar = depth / self.deltaMD * self.alpha
            antialphastar = (1 - depth / self.deltaMD) * self.alpha
            # generate angle coefficients (also for small angles)
            tanga = self.calc_tangential_factor(antialphastar, 1 - depth/self.deltaMD)
            tangb = self.calc_tangential_factor(alphastar, depth/self.deltaMD)
            # generate vector components (also for small angles)
            tangstarn = self.pA.tangN * tanga + self.pB.tangN * tangb
            tangstare = self.pA.tangE * tanga + self.pB.tangE * tangb
            tangstarv = self.pA.tangV * tanga + self.pB.tangV * tangb
            # update inclination / azimuth
            point.update_angles(tangstarn, tangstare, tangstarv)
            return point

    def calc_tangential_factor(self, alphastarcomp, fraction):
        """

        :param alphastarcomp:
        :param fraction:
        :return:
        """
        # check for angle approximation stability according to paper's instructions
        if self.alpha >= 0.02:
            return math.sin(alphastarcomp) / math.sin(self.alpha)
        elif abs(self.alpha) <= 0.0001:
            return fraction
        else:
            alpha2 = self.alpha * self.alpha
            fraction2 = fraction * fraction
            return fraction + alpha2 * (fraction * (1.0 / 6.0 + fraction2 / 6.0) + alpha2 * (fraction * (7.0 / 360.0
                            + fraction2 * (-1.0 / 36.0 + fraction2 / 120.0)) + alpha2 * (fraction * (31.0 / 15120.0
                            + fraction2 * (-7.0 / 2160.0 + fraction2 * (1.0 / 720.0 - fraction2 / 5040.0)))
                            + fraction * alpha2 * (127.0 / 604800.0 + fraction2 * (-31.0 / 90720.0 + fraction2
                            * (7.0 / 43200.0 + fraction2 * (-1.0 / 30240.0 + fraction2 / 362880.0)))))))


class TransformBoreHoleSurvey(object):
    """

    """
    def __init__(self, **kwargs):
        """
        sets class parameters based on external keywords and / or robust defaults

        :param kwargs: unpacked keyword dictionary
        """
        kwargs.setdefault('wellname', 'UNKNOWN')
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('filename_in', 'sample-borehole.txt')
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1, 2, 3))
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('depthunit', 'ft')
        kwargs.setdefault('surfaceunit', 'ft')
        kwargs.setdefault('interval', 50.0)
        kwargs.setdefault('relativeCoords', True)
        kwargs.setdefault('origin', (0.0, 0.0, 0.0))
        kwargs.setdefault('verbose', False)
        # ###########Variables
        self.wellname = kwargs['wellname']
        self.datadir = kwargs['datadir']
        # catching an empty input survey filename
        if kwargs['filename_in'] == 'sample-borehole.txt':
            print('Warning: Using default deviation survey')
        self.filename_in = kwargs['filename_in']
        # interpolate in different modes
        self.mode = kwargs['mode']
        if kwargs['depthunit'] in ('ft', 'm'):
            self.depthunit = kwargs['depthunit']
        else:
            print('Warning: Using default vertical unit [ft]')
            self.depthunit = 'ft'
        if kwargs['surfaceunit'] in ('ft', 'm'):
            self.surfunit = kwargs['surfaceunit']
        else:
            print('Warning: Using default surface unit [ft]')
            self.surfunit = 'ft'
        self.interpolation_interval = kwargs['interval']
        self.verbose = kwargs['verbose']
        
        # MD/INCL/AZIM columns in input file
        try:
            # generate reader object and check file for existence
            self.reader = fileio.BHReaderWriter(**kwargs)
            self.reader.read_head()
        except FileNotFoundError:
                print('Exception: Deviation survey file not found - using default deviation survey')
                kwargs['filename_in'] = 'sample-borehole.txt'
                self.reader = fileio.BHReaderWriter(**kwargs)
        
        # for blank wells try parsing well name from deviation file header
        if self.wellname == 'UNKNOWN':
            # join the original list of strings back together and match by regular expression
            lines = self.reader.read_head()
            for line in lines:
                res_match = match(r"(?i)well:\s*(\S*?),", line)
                if res_match:
                    self.wellname = res_match.group(1)
                    print('Reading well name from file successful: {0:s}'.format(self.wellname))
            
        # output absolute or relative Cartesian coordinates
        if not kwargs['relativeCoords']:
            self.relativeCoords = False
            self.origin = kwargs['origin']
            if len(self.origin) != 3:
                raise ValueError('Exception: Borehole origin in wrong format - needs to be (X(N), Y(E), Z(TVD))')
        else:
            self.relativeCoords = True
            self.origin = (0.0, 0.0, 0.0)

        # ###########Main
        self.survey_points = []
        self.curve_pairs = []
        self.interpolation_points = []
        self.cartesian_points = []
        
        # load, convert, setup data for calculations
        lines = self.reader.read_data()
        try:
            first = float(lines[0][0]) 
            # check first depth value to be non-negative
            if first < 0.0:
                raise ValueError('Exception: first MD value is negative')
            # check first depth value to be at KB or add surface point
            elif first >= 0.0001:
                self.survey_points.append(CLPoint(0.0, 0.0, 0.0))
                print('Warning: Adding surface point to survey data')
        except ValueError as err:
            print('Exception: Error during conversion of survey data\n', err.args)
            sys.exit(1)
        prev = -1
        for line in lines:
            try:
                # convert data to numbers and check for depth-sorting
                line = [float(i) for i in line]
                md = line[0]
                if md < prev:
                    raise ValueError('Exception: MD values are not ascending')
                prev = md
                self.survey_points.append(CLPoint(*line))
            except ValueError as err:
                print('Exception: Error during conversion of survey data\n', err.args)
                sys.exit(1)
        self.setup_min_curv_pairs(self.survey_points)

        # calculate and optionally output
        self.generate_output(self.mode)
        
    def generate_output(self, mode=0):
        """

        :param mode:
        """
        if 0 < mode < 4:
            # generate Cartesian coordinate file from original curvelinear coordinate file
            pointlist = []
            outheader = ''
            wellnote = 'Well: ' + self.wellname
            filename_out = 'out_' + self.wellname
            if mode == 1:
                self.cartesian_points = []
                self.build_cartesian_points()
                filename_out += '_borehole_cart_orig.txt'
                if self.relativeCoords:
                    outheader = (wellnote, 'dX(N) ['+self.surfunit+']', 'dY(E) ['+self.surfunit+']',
                                 'dZ(TVD) ['+self.depthunit+']')
                else:
                    outheader = (wellnote, 'X(N) ['+self.surfunit+']', 'Y(E) ['+self.surfunit+']',
                                 'Z(TVD) ['+self.depthunit+']')
                pointlist = self.cartesian_points
#               for row in self.cartesian_points:
#                  print(row)
            # generate interpolation points and output curvelinear coordinate file
            elif mode == 2:
                self.interpolation_points = []
                self.setup_cl_points()
                self.interpolate_cl_points()
                filename_out += '_borehole_curve_inter.txt'
                outheader = (wellnote, 'MD ['+self.depthunit+']', 'INCL [deg]', 'AZIM [deg]')
                pointlist = self.interpolation_points
            
            # generate and output Cartesian coordinate file from interpolated data
            elif mode == 3:
                self.interpolation_points = []
                self.setup_cl_points()
                self.interpolate_cl_points()
                self.curve_pairs = []
                self.setup_min_curv_pairs(self.interpolation_points)
                self.cartesian_points = []
                self.build_cartesian_points()
                filename_out += '_borehole_cart_inter.txt'
                if self.relativeCoords:
                    outheader = (wellnote, 'dX(N) ['+self.surfunit+']', 'dY(E) ['+self.surfunit+']',
                                 'dZ(TVD) ['+self.depthunit+']')
                else:
                    outheader = (wellnote, 'X(N) ['+self.surfunit+']', 'Y(E) ['+self.surfunit+']',
                                 'Z(TVD) ['+self.depthunit+']')
                pointlist = self.cartesian_points
#               for row in self.cartesian_points:
#                   print(row)
            outdata = []
            for item in pointlist:
                outdata.append(item.output_list())
            outargs = {'datadir': self.datadir, 'filename_out': filename_out,
                       'header_out': outheader, 'data_out': outdata, 'verbose': self.verbose}
            writer = fileio.BHReaderWriter(**outargs)
            writer.write_data()
        else:
            print('No output file generated')

    def setup_min_curv_pairs(self, clpoints):
        """
        build list of curve pairs and calculate min. curvature parameters

        :param clpoints:
        """
        for pairs in zip(clpoints[0:-1], clpoints[1:]):
            # print(pairs[0],'\n',pairs[1],'\n')
            self.curve_pairs.append(MinCurvPair(pairs[0], pairs[1]))
        if self.verbose:
            print('Number of MinCurv pairs generated: ', len(self.curve_pairs))
            for pair in self.curve_pairs:
                print(pair)

    def build_cartesian_points(self):
        """

        """
        current = CartPoint(self.origin[0], self.origin[1], -self.origin[2])
        self.cartesian_points.append(current)
        if self.depthunit == self.surfunit:
            scaler = 1.0
        elif self.depthunit == 'ft':
            scaler = .3048
        # unlikely case
        else:
            scaler = 1/.3048
        for curvepair in self.curve_pairs:
            delta = self.calculate_cartesian_deltas(curvepair)
            delta.scale_xy(scaler)
            current += delta
            self.cartesian_points.append(current)

    def calculate_cartesian_deltas(self, pair):
        """

        :param pair:
        :return:
        """
        dx = math.sin(pair.pA.incl) * math.cos(pair.pA.azim) + math.sin(pair.pB.incl) * math.cos(pair.pB.azim)
        dy = math.sin(pair.pA.incl) * math.sin(pair.pA.azim) + math.sin(pair.pB.incl) * math.sin(pair.pB.azim)
        dz = math.cos(pair.pA.incl) + math.cos(pair.pB.incl)
        deltas = CartPoint(dx, dy, dz)
        scaler = pair.deltaMD * pair.shapefactor / 2.0
        deltas.scale(scaler)
        if self.verbose:
            print(deltas)
        return deltas

    def setup_cl_points(self):
        """

        """
        # build list of interpolation points and fill with MD values
        min_depth = self.survey_points[0].md
        max_depth = self.survey_points[-1].md
        # integer division - number of flagpoles
        points = int((max_depth - min_depth) // self.interpolation_interval) + 1
        for point in range(points):
            self.interpolation_points.append(CLPoint(min_depth + self.interpolation_interval * point, 0.0, 0.0))
        # check for sampling interval without overlap or add last survey point
        residual = (max_depth - min_depth) % self.interpolation_interval
        if residual > 0.001:
            self.interpolation_points.append(CLPoint(max_depth, 0.0, 0.0))
        if self.verbose:
            print('MinDepth: ', min_depth)
            print('MaxDepth: ', max_depth)
            print('Interval:', self.interpolation_interval)
            print('Evenly-Spaced Points: ', points)
            print('Residual: ', residual)
            print('Number of interpolation points: ', len(self.interpolation_points))
    
    def interpolate_cl_points(self):
        """

        """
        dataiter = iter(self.curve_pairs)
        # point iterator to first MinCurvPair
        curvepair = next(dataiter)
        # loop over all interpolation points
        for index, ipoint in enumerate(self.interpolation_points):
            # move to MinCurvPair containing the interpolation point
            while ipoint.md > curvepair.pB.md: 
                curvepair = next(dataiter)
            idepth = ipoint.md-curvepair.pA.md
            self.interpolation_points[index] = curvepair.calc_interpolation_md(idepth)
            if self.verbose:
                print('Interval {0:8.2f} to {1:8.2f} used to interpolate point {2:8.2f}'.format(curvepair.pA.md,
                                                                                                curvepair.pB.md,
                                                                                                ipoint.md))
        if self.verbose:
            print('RESULT:\n')
            for point in self.interpolation_points:
                print(point)

    def calculate_cl_point(self, mdepth):
        """

        :param mdepth:
        :return:
        """
        minimum = self.curve_pairs[0].pA.md
        maximum = self.curve_pairs[-1].pB.md
        if mdepth < minimum:
            mdepth = minimum
            print('Warning: Depth extrapolation beyond well data was shortened')
        if mdepth > maximum:
            mdepth = maximum
            print('Warning: Depth extrapolation beyond well data was shortened')
        dataiter = iter(self.curve_pairs)
        # point iterator to first MinCurvPair
        curvepair = next(dataiter)
        # move to MinCurvPair containing the interpolation point
        while mdepth > curvepair.pB.md:
            curvepair = next(dataiter)
        idepth = mdepth-curvepair.pA.md
        point = curvepair.calc_interpolation_md(idepth)
        if self.verbose:
                print('Interval {0:8.2f} to {1:8.2f} used to interpolate point {2:8.2f}'.format(curvepair.pA.md,
                                                                                                curvepair.pB.md,
                                                                                                mdepth))
                print(point)
        return point
                

if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH = 79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: boreholemath'.ljust(TWIDTH, '-'))
    print(TWIDTH*'=')
    transform = TransformBoreHoleSurvey(datadir='..\\data', mode=1, relativeCoords=False, wellname='test01',
                                        origin=(-100, -200, 100), verbose=False)
    transform.generate_output(mode=2)
    transform.generate_output(mode=3)
    # print(transform.calculate_cl_point(-102))
    transform = TransformBoreHoleSurvey(datadir='..\\data', filename_in='sample-fieldtest.dev', mode=1,
                                        columns_in=(0, 1, 2), relativeCoords=False, wellname='fieldtest',
                                        verbose=False, depthunit='ft', surfaceunit='ft')
else:
    print('Importing ' + __name__)
