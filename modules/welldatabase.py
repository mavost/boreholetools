#!/usr/bin/python #Linux shebang plus chmod to make executable
# ------------------------------------------------------------
# FILENAME: welldatabase.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
# ------------------------------------------------------------
# tools for setting up well database

import sys
import glob

from modules import boreholemath
from modules import fileio
from modules import markermath


class Well(object):
    """
    Well object holds shared horizontal and vertical length units and individual well properties:
     WELL NAME, ORIGIN, GEOMETRY (DEVIATION SURVEY), WELL MARKERS
    """

    DEPTHUNIT = 'ft'
    SURFUNIT = 'ft'
    """define static variables and helper functions to force consistent length handling across well data"""

    @staticmethod
    def depth_to_metric():
        """
        static function to set depth to metric length unit (meters)
        """
        Well.DEPTHUNIT = 'm'
        if Well.VERBOSE:
            print('Depth units switched to Metric')
        
    @staticmethod
    def depth_to_imperial():
        """
        static function to set depth to imperial length unit (feet)
        """
        Well.DEPTHUNIT = 'ft'
        if Well.VERBOSE:
            print('Depth units switched to Imperial')

    @staticmethod
    def surf_to_metric():
        """
        static function to set surface units to metric length units (meters)
        """
        Well.SURFUNIT = 'm'
        if Well.VERBOSE:
            print('Surface units switched to Metric')
        
    @staticmethod
    def surf_to_imperial():
        """
        static function to set surface units to imperial length units (feet)
        """
        Well.SURFUNIT = 'ft'
        if Well.VERBOSE:
            print('Surface units switched to Imperial')

    VERBOSE = False
    """define static variable for verbosity"""

    @staticmethod
    def switch_verbose():
        """
        static function to switch on/off verbose output to console
        """
        if Well.VERBOSE:
            Well.VERBOSE = False
        else:
            Well.VERBOSE = True

    def __init__(self, **kwargs):
        r"""
        constructor initializes all parameters to generate a well object containing
            WELL NAME, ORIGIN, GEOMETRY (DEVIATION SURVEY)



        .. note:: WELL MARKERS attribute is empty until :class:`WellMarkerLoading` is instantiated

        :param \**kwargs: key/value list required to set up a well instance

        :Keyword Arguments:
            * *datadir* (``string``) --
              path to data directory
            * *filename_in* (``string``) --
              deviation survey file
            * *wellname* (``string``) --
              unique well name
            * *origin* ((``float``, ``float``, ``float``)) --
              Cartesian location of well head (KB), Default ``(0.0, 0.0, 0.0)``
            * *headerlines_in* (``int``) --
              number of header lines in deviation survey file
            * *columns_in* ((``int``, ``int``, ``int``)) --
              default values for relevant data columns in deviation file (MD, INCL, AZIM), Default ``(1, 2, 3)``
            * key/values handed to :class:`modules.boreholemath.TransformBoreHoleSurvey` during GEOMETRY loading

                - *mode* (``int``) --
                  deviation file reading / conversion / interpolation mode, Default ``0``: no output
                - *interval* (``float``) --
                  interpolation interval along MD, Default ``50.0``

        """
        if Well.VERBOSE:
            print(kwargs)
        # ###########defaults
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('filename_in', 'sample-borehole.txt')     # deviation survey file
        kwargs.setdefault('wellname', 'UNKNOWN')
        kwargs.setdefault('origin', (0.0, 0.0, 0.0))                # Cartesian location of well head (KB)
        # default values for deviation file shape
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1, 2, 3))
        # default values for survey handling
        kwargs.setdefault('mode', 0)                                # no output default
        kwargs.setdefault('interval', 50)
        
        # ###########variables
        self.wellname = kwargs['wellname']
        # (N(X), E(Y), KB) with KB being a positive number above reference level
        self.wellorigin = kwargs['origin']
        # Well.DEPTHUNIT, Well.SURFUNIT, Well.VERBOSE set by helper function
        
        devinargs = {'depthunit': Well.DEPTHUNIT, 'surfaceunits': Well.SURFUNIT, 'verbose': Well.VERBOSE,
                     'datadir': kwargs['datadir'], 'filename_in': kwargs['filename_in'],
                     'wellname': self.wellname, 'origin': self.wellorigin, 'headerlines_in': kwargs['headerlines_in'],
                     'columns_in': kwargs['columns_in'], 'relativeCoords': False, 'mode': kwargs['mode'],
                     'interval': kwargs['interval']}
        self.geometry = boreholemath.TransformBoreHoleSurvey(**devinargs)
        self.markers = dict()
        # keys are formation codes - do we need to allow for multiple entries in one key?
        #                      -> not for geometry purpose (else use subscripted key TERT_A /TERT_B)
        # self.markers = [] #alternatively list

    def __str__(self):
        """overloaded string operator"""
        return 'Well name: {0:s}, X: {1:10.1f}, Y: {2:10.1f}, KB: {3:6.1f}'.format(self.wellname, *self.wellorigin)


class WellMarkerLoading(object):
    """

    """

    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        # ###########defaults
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('verbose', False)
        kwargs.setdefault('welldatabase', None)
        kwargs.setdefault('filename_in', 'sample-markers.txt')
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1, 2, 3, 4, 5))
        kwargs.setdefault('filename_strat_def', None)
        kwargs.setdefault('filename_strat_order', None)

        # ###########variables
        self.welldb = kwargs['welldatabase']
        self.datadir = kwargs['datadir']
        if self.welldb is None:
            self.welldb = WellDatabase(datadir=self.datadir)
            print('Warning: generating default WellDatabase')
            print(self.welldb)
        self.verbose = kwargs['verbose']

        # ###########update stratigraphy before loading marker file
        if kwargs['filename_strat_def']:
            markermath.Stratigraphy.load_strat_definition(self.datadir, kwargs['filename_strat_def'], self.verbose)
        # ###########select markers in stratigraphy relevant for calculations
        if kwargs['filename_strat_order']:
            markermath.Stratigraphy.load_strat_order(self.datadir, kwargs['filename_strat_order'], self.verbose)
            markermath.Stratigraphy.print_strat()
        # ###########load markers and match the ones mentioned in STRATORDER to the well database
        self.load_strat_markers(kwargs['filename_in'], kwargs['headerlines_in'], kwargs['columns_in'])

    def load_strat_markers(self, markerfile, headerlines=1, columns=(1, 2, 3, 4, 5)):
        """

        :param markerfile:
        :param headerlines:
        :param columns:
        """
        print('Opening marker file:')
        mfargs = {'datadir': self.datadir, 'filename_in': markerfile,
                  'headerlines_in': headerlines, 'columns_in': columns}
        if (len(columns)) not in (3, 5):
            print('Error: Column specification in marker file requires three or five rows to be supplied\n\tformat:\
                    WELL NAME, MARKER CODE, DEPTH MD [length], DIP(opt) [deg], DAZIM(opt) [deg]')
            sys.exit()
        try:
            # build dictionary of relevant markers
            validmarkers = dict()
            for item in markermath.Stratigraphy.STRATORDER:
                validmarkers[item] = 1
            # read marker table
            markerreader = fileio.BHReaderWriter(**mfargs)
            lines = markerreader.read_data()
            for line in lines:
                # find corresponding well
                print(line)
                wellin = line[0]
                markerin = line[1]
                if len(line) in (3, 5):
                    if len(line) == 3:
                        wmargs = {'wellname': wellin, 'wmtype': 'STRAT', 'strat': markerin, 'md': float(line[2])}
                    elif line[3] == '' or line[4] == '':
                        wmargs = {'wellname': wellin, 'wmtype': 'STRAT', 'strat': markerin, 'md': float(line[2])}
                    else:
                        wmargs = {'wellname': wellin, 'wmtype': 'STRAT', 'strat': markerin, 'md': float(line[2]),
                                  'dip': float(line[3]), 'dazim': float(line[4])}
                    if self.verbose:
                        print('Line: {0:s}'.format(str(line)))
                        print('Inargs: {0:s}'.format(str(wmargs)))
                    if wellin in self.welldb.wells and markerin in validmarkers:
                        # add marker to well
                        wmargs['wellgeometry'] = self.welldb.wells[wellin].geometry
                        # array solution
                        # self.welldb.wells[wellin].markers.append(WellMarker(**wmargs))
                        # dict solution
                        self.welldb.wells[wellin].markers[markerin] = markermath.WellMarker(**wmargs)
                        if self.verbose:
                            print('Class Well: Adding stratigraphy well marker to {0} using arguments:'.format(wellin))
                            print(wmargs)
                else:
                    print('Stratigraphy marker {0} in well {1} discarded'.format(markerin, wellin))
        except TypeError:
            print('Exception: Type error during conversion of marker file')
            sys.exit(1)
        except ValueError:
            print('Exception: Value error during conversion of marker file')
            sys.exit(1)
        print('Well markers successfully loaded to well database')
        if self.verbose:
            self.print_strat_markers()

    def print_strat_markers(self):
        """

        """
        for item in dict(sorted(self.welldb.wells.items(), key=lambda x: x[0])):
            current = self.welldb.wells[item]
            print(current)
            try:
                for counter, markertab in enumerate(markermath.Stratigraphy.STRATORDER):
                    if markertab in current.markers:
                        print('{0:02d}:{1}'.format(counter, current.markers[markertab].out_short()))
                    else:
                        print('{0:02d}:{1}'.format(counter, 'None'))
                print('----')
            except KeyError:
                print('Exception: printStratMarkers output error')
                sys.exit()


class WellDatabase(object):
    """
    WellDatabase object factory template creates well instances based on a user supplied well spreadsheet
    and corresponding supporting files
    """
    def __init__(self, **kwargs):
        """
        sets class parameters based on external keywords and / or robust defaults

        :param kwargs: unpacked keyword dictionary
        """
        print(kwargs)
        # ###########defaults
        kwargs.setdefault('datadir', 'data')
        kwargs.setdefault('verbose', False)
        kwargs.setdefault('depthunit', 'ft')
        kwargs.setdefault('surfaceunits', 'ft')
        kwargs.setdefault('filename_in', 'sample-wellheads.txt')     # default well head file
        # default values for header file shape
        kwargs.setdefault('headerlines_in', 1)
        kwargs.setdefault('columns_in', (1, 2, 3, 4, 5))
        # default values for survey handling
        kwargs.setdefault('mode', 0)
        kwargs.setdefault('interval', 50)

        # ###########variables
        self.wells = dict()
        self.verbose = kwargs['verbose']
        if self.verbose:
            Well.switch_verbose()
            print('Opening well head file:')
        # create dictionary based on kwargs and load well head spreadsheet
        welldbinargs = {'datadir': kwargs['datadir'], 'filename_in': kwargs['filename_in'],
                        'headerlines_in': kwargs['headerlines_in'], 'columns_in': kwargs['columns_in']}
        headreader = fileio.BHReaderWriter(**welldbinargs)
        lines = headreader.read_data()
        if kwargs['depthunit'] == 'm':
            Well.depth_to_metric()
        if kwargs['surfaceunits'] == 'm':
            Well.surf_to_metric()
        for line in lines:    
            try:
                # convert spreadsheet data to proper type and check for depth-sorting
                wname = line[0]         # str: WELLNAME
                # 3 x flt: ORIGIN X, Y, Z(KB)
                wcoordinates = tuple([float(i) for i in line[1:4]])
                wfname = line[4]        # str: DEVIATION FILENAME
                # create dictionary based on info in well head file
                wellinargs = {'datadir': kwargs['datadir'], 'wellname': wname, 'origin': wcoordinates,
                              'filename_in': wfname, 'mode': kwargs['mode'], 'interval': kwargs['interval']}
                # do not allow duplicates and instantiate new well
                if wname not in self.wells:
                    self.wells[wname] = Well(**wellinargs)
                else:
                    print('Warning: Double occurrence of name in well head file, keeping first instance')
            except ValueError:
                    print('Exception: Error during conversion of well head data')
                    sys.exit(1)
            if self.verbose:
                print('Input Name: {0:s}, X: {1:10.1f}, Y: {2:10.1f}, KB: {3:6.1f}'.format(wname, *wcoordinates))
                print(str(self.wells[wname]))

    def get_wells_sorted(self):
        """
        helper function to return a key-sorted (WELL NAME) dictionary for reporting

        :return: dictionary of well instances keyed by WELL NAME
        """
        return dict(sorted(self.wells.items(), key=lambda x: x[0]))

    def __str__(self):
        """overloaded string operator"""
        return 'Number of wells loaded: {0:4d}'.format(len(self.wells))

            
if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH = 79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: welldatabase'.ljust(TWIDTH, '-'))
    print(TWIDTH*'=')
    print('Testing: Class Well')
    well = Well(datadir='..\\data', verbose=True)
    print(well)
    Well.depth_to_metric()
    print(TWIDTH*'=')
    print('Testing: Class WellDatabase')
    print(TWIDTH*'=')
    print('Opening well head file and creating well database:')
    try:
        inargs = {'datadir': '..\\data', 'filename_in': 'sample-wellheads.txt',
                  'mode': 3, 'verbose': False}
        welldb = WellDatabase(**inargs)
        print(welldb)
    except ValueError:
        print('Exception: Something went wrong with the parameters of the well database')
        sys.exit(1)
    except FileNotFoundError:
        print('Exception: File not found during building of well database')
        sys.exit(1)
    print(TWIDTH*'=')
    print('Testing: Class WellMarker')
    inargs = {'datadir': '..\\data', 'filename_strat_def': 'sample-stratdef.txt',
              'filename_strat_order': 'sample-stratorder.txt', 'verbose': True}
    loading = WellMarkerLoading(**inargs)
    loading.print_strat_markers()
    print(TWIDTH*'=')
    print('Testing: glob module')
    print(TWIDTH*'=')
    mylist = [f for f in glob.glob('..\\data\\out*.txt')]
    print(mylist)
    print(TWIDTH*'=')
else:
    print('Importing ' + __name__)
