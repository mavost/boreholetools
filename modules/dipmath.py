#!/usr/bin/python #Linux shebang plus chmod to make executable
# ------------------------------------------------------------
# FILENAME: dipmath.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
# ------------------------------------------------------------
# tools for manipulating dipmeter interpretation files


import math
import sys

from modules import boreholemath
from modules import fileio


class DipPoint(object):
    """provides dip and dip azimuth properties to a point including a corresponding
    tangential vector and its manipulation
    """
    @staticmethod
    def get_matrix_x(angle):
        """static function returns a matrix rotation by angle along X axis

        :param angle: rotation angle (radian)
        :return: 3x3 list of flt
        """
        return [[1.0, 0.0, 0.0],
                [0.0, math.cos(angle), -math.sin(angle)],
                [0.0, math.sin(angle), math.cos(angle)]]
    
    @staticmethod
    def get_matrix_y(angle):
        """static function returns a matrix rotation by angle along Y axis

        :param angle: rotation angle (radian)
        :return: 3x3 list of flt
        """
        return [[math.cos(angle), 0.0, math.sin(angle)],
                [0.0, 1.0, 0.0],
                [-math.sin(angle), 0.0, math.cos(angle)]]

    @staticmethod
    def get_matrix_z(angle):
        """static function returns a matrix rotation by angle along Z axis

        :param angle: rotation angle (radian)
        :return: 3x3 list of flt
        """
        return [[math.cos(angle), -math.sin(angle), 0.0],
                [math.sin(angle), math.cos(angle), 0.0],
                [0.0, 0.0, 1.0]]

    def __init__(self, dip=0.0, dazim=0.0):
        """
        constructor for dip / dip azimuth instance and corresponding unit vector pointing in direction
        of maximum falling dip

        :param dip: dip of geological bed from horizontal in falling direction (grad)
        :param dazim: dip azimuth of geological bed measured clockwise from grid north (grad)
        """
        # debug output
        self.verbose = True
        # inclination angle between reference frame XY-plane and max falling dip 0 <= dip < pi
        self.dip = (math.pi + math.radians(dip)) % math.pi
        # azimuth angle projected to XY-plane, referenced to X-axis 0 <= dazim < 2*pi
        self.dazim = (math.pi * 2.0 + math.radians(dazim)) % (math.pi * 2.0)
        # define a unit vector pointing in direction of maximum falling dip
        # defaults to 1,0,0
        self.dipN = math.cos(self.dip) * math.cos(self.dazim)
        self.dipE = math.cos(self.dip) * math.sin(self.dazim)
        self.dipV = math.sin(self.dip)
    
    def _rotate(self, matrix_func, angle):
        """
        helper function to actually perform a functional-based rotation of the tangential vector by given angle.
        Note, that this function does not change the instance.

        :param matrix_func: functional object - either X,Y,Z rotation matrix
        :param angle: angle of rotation (grad)
        :return:
        """
        angrad = math.radians(angle)
        matrix = matrix_func(angrad)
        in_vec = [self.dipN, self.dipE, self.dipV]
        res_vec = [0.0, 0.0, 0.0]
        for i in range(3):
            for j in range(3):
                res_vec[i] += matrix[i][j] * in_vec[j]
        return res_vec

    def _update_angles(self, newdips):
        """back-calculate dip and dip azimuth from a tangential vector changed by rotation

        :param newdips: list(3) of flt corresponding to the three-component tangential vector
        """
        try:
            if len(newdips) != 3:
                raise ValueError('Exception: Dip vector has wrong number of components: ', len(newdips))
            # calculate length of vector
            length = math.sqrt(newdips[0]*newdips[0]+newdips[1]*newdips[1]+newdips[2]*newdips[2])
            if length > 0:
                # if dip vector is too long - rescale to unit vector
                self.dipN = newdips[0] / length
                self.dipE = newdips[1] / length
                self.dipV = newdips[2] / length
            else:
                raise ValueError('Exception: Dip vector has zero length')
            horiz = math.sqrt(self.dipN * self.dipN + self.dipE * self.dipE)
            self.dip = math.acos(horiz)
            self.dazim = (math.pi * 2.0 + math.atan2(self.dipE, self.dipN)) % (math.pi * 2.0)
            if self.verbose:
                # print('New tangential vector:')
                print('              X: {0:7.2f}, Y: {1:7.2f}, Z: {2:7.2f}'.format(*newdips))
                print('              Dip: {0:8.3f}, Azimuth: {1:8.3f}'.format(math.degrees(self.dip),
                                                                              math.degrees(self.dazim)))
        except ValueError as err:
            print(err.args)
            sys.exit(1)
    
    def __str__(self):
        """overloaded string operator"""
        return 'Dip: {0:8.3f}, Azimuth: {1:8.3f}'.format(math.degrees(self.dip), math.degrees(self.dazim))
    
    def rotate_x(self, angle):
        """
        handle to perform a rotation of bed dip instance by X axis using angle and updating the dip / dip azimuth

        :param angle: angle of rotation (grad)
        """
        vec = self._rotate(DipPoint.get_matrix_x, angle)
        self._update_angles(vec)

    def rotate_y(self, angle):
        """
        handle to perform a rotation of bed dip instance by Y axis using angle and updating the dip / dip azimuth

        :param angle: angle of rotation (grad)
        """
        vec = self._rotate(DipPoint.get_matrix_y, angle)
        self._update_angles(vec)

    def rotate_z(self, angle):
        """
        handle to perform a rotation of bed dip instance by Z axis using angle and updating the dip / dip azimuth

        :param angle: angle of rotation (grad)
        """
        vec = self._rotate(DipPoint.get_matrix_z, angle)
        self._update_angles(vec)


class DipMarker(DipPoint):
    """

    """
    def __init__(self, md, dip=None, dazim=None, wellgeometry_in=None, verbose=False):
        """

        :param md:
        :param dip:
        :param dazim:
        :param wellgeometry_in:
        :param verbose:
        """
        self.md = md
        if dip is not None and dazim is not None:
            self.in_dip = math.radians(dip)
            self.in_dazim = math.radians(dazim)
            # conversion to radians in DipPoint class
            super(DipMarker, self).__init__(dip, dazim)
        else:
            # initialize as zero
            self.in_dip = 0.0
            self.in_dazim = 0.0
            super(DipMarker, self).__init__(0.0, 0.0)
        self.verbose = verbose
        if self.verbose:
            print(self)
        if wellgeometry_in is not None and dip is not None and dazim is not None:
            self.clpoint = wellgeometry_in.calculate_cl_point(self.md)
            if self.verbose:
                print('Dipmarker correction:')
                print('MD: {0:8.2f}, '.format(self.md) + super(DipMarker, self).__str__())
            self.reorient_dip()

    def __str__(self):
        """ overloading string operator """
        return 'MD: {0:8.3f}, Dip: {1:8.3f}, Azimuth: {2:8.3f}'.format(self.md, math.degrees(self.dip),
                                                                       math.degrees(self.dazim))

    def output_list(self, mymode=0):
        """

        :param mymode:
        :return:
        """
        if mymode == 0:
            return [f'{self.md:{10}.{2}f}', f'{math.degrees(self.dip):{10}.{5}f}',
                    f'{math.degrees(self.dazim):{10}.{5}f}']
        else:
            return [f'{self.md:{10}.{2}f}', f'{math.degrees(self.in_dip):{10}.{5}f}',
                    f'{math.degrees(self.in_dazim):{10}.{5}f}',
                    f'{math.degrees(self.dip):{10}.{5}f}', f'{math.degrees(self.dazim):{10}.{5}f}',
                    f'{math.degrees(self.clpoint.incl):{10}.{5}f}', f'{math.degrees(self.clpoint.azim):{10}.{5}f}']

    def reorient_dip(self):
        """

        """
        by_y = math.degrees(self.clpoint.incl)
        by_z = math.degrees(self.clpoint.azim)
        if self.verbose:
            print('      Borehole INCL: {0:8.3f}, Borehole AZIM: {1:8.3f}'.format(by_y, by_z))
            print('      Rotation on Y-Axis with borehole inclination: {0:8.3f}'.format(by_y))
        self.rotate_y(by_y)
        if self.verbose:
            print('      Rotation on Z-Axis with borehole azimuth    : {0:8.3f}'.format(by_z))
        self.rotate_z(by_z)
        

if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH = 79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: dipmath'.ljust(TWIDTH, '-'))
    print(TWIDTH*'=')

    print('Testing: Class DipPoint')
    point = DipPoint(45, 0)
    print('Input:')
    print(point)
    print('Rotation starts:')
    for ang in range(0, 360, 15):
        point.rotate_y(15)
        # print('Rot: ', ang, ' Result:', point)
    print(TWIDTH*'=')
    print('Testing: Class DipMarker')
    # generate a borehole deviation survey / interpolation object
    wellgeometry = boreholemath.TransformBoreHoleSurvey(datadir='..\\data', mode=0, relativeCoords=True, verbose=False)
    # correct one marker by extracting corresponding horehole inclination/azim
    print('Apply correction on one DipMarker point:')
    dmarker = DipMarker(5000, 45, 10, wellgeometry, verbose=True)
    print(dmarker)
    # repeat the same for data read from a file
    print('Opening dipmarker file:')
    inargs = {'datadir': '..\\data', 'filename_in': 'sample-dipmarker.txt',
              'headerlines_in': 1, 'columns_in': (1, 2, 3)}
    reader = fileio.BHReaderWriter(**inargs)
    lines = reader.read_data()
    result = []
    for line in lines:
        try:
            # convert data to numbers and check for depth-sorting
            line = [float(i) for i in line]
            result.append(DipMarker(*line, wellgeometry, verbose=False))
        except ValueError:
                print('Exception: Error during conversion of survey data')
                sys.exit()
        print('Before - MD: {0:8.3f}, Dip: {1:8.3f}, Azimuth: {2:8.3f}'.format(*line))
        print('After  - ' + str(result[-1]))
    print('Writing dipmarker file:')
    # mode = basic(0) or detailed(1) output
    mode = 1
    outdata = []
    for item in result:
        outdata.append(item.output_list(mode))
    if mode == 1:
        outheader = ('Well: UNKNOWN', 'MD [depthunit]', 'DIP_ORIG [deg]',
                     'DAZI_ORIG [deg]', 'DIP [deg]', 'DAZI [deg]', 'INCL [deg]', 'AZIM [deg]')
    else:
        outheader = ('Well: UNKNOWN', 'MD [depthunit]', 'DIP [deg]', 'DAZI [deg]')
 
    outargs = {'datadir': '..\\data', 'filename_out': 'out_sample-dipmarker.txt',
               'header_out': outheader, 'data_out': outdata, 'verbose': True}
    writer = fileio.BHReaderWriter(**outargs)
    writer.write_data()
    print(TWIDTH*'=')
else:
    print('Importing ' + __name__)
