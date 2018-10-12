#!/usr/bin/python #Linux shebang plus chmod to make executable
# ------------------------------------------------------------
# FILENAME: markermath.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
# ------------------------------------------------------------
# tools for manipulating well marker interpretation files


import sys

from modules import dipmath
from modules import fileio


class Stratigraphy(object):
    """

    """
    STRAT = {'NONE': 'None', 'REF': 'Reference Level', 'TERT': 'Tertiary', 'CRET': 'Cretaceous',
             'JUR': 'Jurassic', 'TRIA': 'Triassic'}
    STRATORDER = ('REF', 'TERT', 'CRET', 'JUR', 'TRIA')

    @staticmethod
    def print_strat():
        """

        """
        print('Stratigraphy used in calculations:')
        try:
            for counter, item in enumerate(Stratigraphy.STRATORDER):
                print('\tBoundary {0:02d}:{1:>6.5}-{2:20.19}'.format(counter, item, Stratigraphy.STRAT[item]))
        except KeyError:
            print('Exception: Stratigraphy keys in definition and order files don\'t match')
            sys.exit()

    @staticmethod
    def load_strat_definition(datadir, stratdeffile, verbose=False):
        """

        :param datadir:
        :param stratdeffile:
        :param verbose:
        """
        print('Opening stratigraphy definition file:')
        stratargs = {'datadir': datadir, 'filename_in': stratdeffile,
                     'headerlines_in': 1, 'columns_in': (1, 2)}
        try: 
            Stratigraphy.STRAT = dict()
            Stratigraphy.STRAT['NONE'] = 'None'
            Stratigraphy.STRAT['REF'] = 'Reference Level'
            stratdefreader = fileio.BHReaderWriter(**stratargs)
            lines = stratdefreader.read_data()
            for line in lines:
                if len(line) == 2:
                    Stratigraphy.STRAT[line[0]] = line[1]
            if verbose:
                print(Stratigraphy.STRAT)
        except FileNotFoundError:
            print('Exception: File not found during loading of stratigraphy definition data')
            sys.exit(1)
        print('Stratigraphy definition updated')

    @staticmethod
    def load_strat_order(datadir, stratorder_file, verbose=False):
        """

        :param datadir:
        :param stratorder_file:
        :param verbose:
        """
        print('Opening stratigraphy order/selection file:')
        stratargs = {'datadir': datadir, 'filename_in': stratorder_file,
                     'headerlines_in': 1, 'columns_in': (1,)}
        try: 
            stratorderreader = fileio.BHReaderWriter(**stratargs)
            lines = stratorderreader.read_data()
            seen = {'REF': 1}
            result = ['REF']
            for line in lines:
                if len(line) == 1:
                    if line[0] in seen:
                        continue
                    seen[line[0]] = 1
                    result.append(line[0])
            Stratigraphy.STRATORDER = result
            if verbose:
                print(Stratigraphy.STRATORDER)
        except FileNotFoundError:
            print('Exception: File not found during loading of stratigraphy order data')
            sys.exit(1)
        print('Stratigraphy order/selection updated')


class WellMarker(dipmath.DipMarker):
    """

    """
    TYPE = {'UNKN': 'Unknown', 'STRT': 'Stratigraphy', 'LITH': 'Lithology', 'FLT': 'Fault',
            'TECH': 'Technical'}

    def __init__(self, wmtype='UNKN', strat='NONE', md=0.0, dip=None, dazim=None, wellname='UNKNOWN', wellgeometry=None,
                 verbose=False):
        """

        :param wmtype:
        :param strat:
        :param md:
        :param dip:
        :param dazim:
        :param wellname:
        :param wellgeometry:
        :param verbose:
        """
        if dip is not None and dazim is not None:
            super(WellMarker, self).__init__(md, dip, dazim, wellgeometry, verbose=False)
        else:   # no dip/dazim supplied -> just basic function
            super(WellMarker, self).__init__(md, None, None, wellgeometry, verbose=False)
        if strat != 'NONE':
            self.strat = strat
            self.wmtype = 'STRT'
        else:
            self.wmtype = wmtype
            self.strat = 'NONE'
        self.verbose = verbose
        self.wellname = wellname

    def __str__(self):
        """ overloading string operator """
        # print('Output:', self.type, self.strat, self.md)
        # Stratigraphy.print_strat()
        return 'Well {0:s}:\n{1:s} Marker, Formation age: {2:s}, Depth: {3:8.3f}\n\t'.\
                   format(self.wellname, WellMarker.TYPE[self.wmtype],
                          Stratigraphy.STRAT[self.strat], self.md) + super(WellMarker, self).__str__()

    def out_short(self):
        """ short whoami operator """
        return '\t{0:20.19s}\t'.format(Stratigraphy.STRAT[self.strat]) + super(WellMarker, self).__str__()


if __name__ == '__main__':                    # call test environment only if module is called standalone
    TWIDTH = 79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: markermath'.ljust(TWIDTH, '-'))
    print(TWIDTH*'=')
    print('Testing: Class DipMarker')
    print('Input:')
    marker = WellMarker(md=100, dip=10, dazim=0, strat='TERT', wellname='Dixie02')
    print(marker)
    print('Rotation starts:')
    for ang in range(15, 360, 15):
        marker.rotate_y(-15)
        # print('Rot: ', ang, ' Result:', marker)
        print(marker)
else:
    print('Importing ' + __name__)
