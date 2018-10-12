#!/usr/bin/python #Linux shebang plus chmod to make executable
# ------------------------------------------------------------
# FILENAME: boreholetools.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 23/09/2018
# ------------------------------------------------------------
""" boreholetools main control module
"""
import argparse
import sys
import os
# add extra path into search list for paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
# disable for production
print(sys.path)

try:
    from modules.welldatabase import WellDatabase, WellMarkerLoading
    from modules.boreholemath import TransformBoreHoleSurvey
    from modules.dipmath import DipPoint, DipMarker
except ImportError:
    print('Exception: Module not found')
    sys.exit(1)


# https://stackoverflow.com/questions/3853722/python-argparse-how-to-insert-newline-in-the-help-text
class SmartFormatter(argparse.HelpFormatter):
    """ a quick re-classing to enable RAW help descriptions"""
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def str2bool(v):
    """ a quick reader for boolean type argument strings"""
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Exception, Parser Error: Boolean value expected.')


def validintervalrange(v):
    """ a quick reader for specific float type argument strings"""
    value = float(v)
    if value >= 0.1:
        return value
    else:
        raise argparse.ArgumentTypeError('Exception, Parser Error: float out of range.')


def parse(manualargs=None):
    """ parser for defining and reading key words from command line"""
    debug = False
    terminal = 79                               # terminal width excluding EOL
    parser = argparse.ArgumentParser(formatter_class=SmartFormatter)
    # define keywords
    # general section
    parser.add_argument('--datadir', type=str, default='.\\data',
                        help='%(type)s: path to data directory (def: %(default)s)')
    parser.add_argument('--depthunit', type=str, default='ft',
                        help='%(type)s (ft, m): input and output unit for vertical length (Z) (def: %(default)s)')
    parser.add_argument('--surfaceunits', type=str, default='ft',
                        help='%(type)s (ft, m): input and output units for horizontal lengths (X,Y) (def: %(default)s)')
    parser.add_argument('--verbose', type=str2bool, default=False,
                        help='bool: verbose / debug output (def: %(default)s)')
    # well database section
    wdb = parser.add_argument_group('Keywords to generate well database')
    wdb.add_argument('--wdbfile', type=str, default='sample-wellheads.txt',
                        help='%(type)s: CSV file containing well name, well head origin, and respective filename for '
                             'directional survey (def: %(default)s)')
    wdb.add_argument('--wdbfilehd', type=int, default=1,
                        help='%(type)s: header lines to skip in well head file (def: %(default)s)')
    wdb.add_argument('--wdbfilecol', default=(1, 2, 3, 4, 5),
                        help='TUP(5 * INT): index # of rows containing WELL NAME, X, Y, KB, FILENAME'
                             '(def: %(default)s)')
    wdb.add_argument('--wdbmode', type=int, default=2,
                        help='R|%(type)s: specifies conversion mode\n'
                             'for loaded directional survey (def: %(default)s)\n'
                             ' 0: no output\n'
                             ' 1: output original survey as Cartesian X, Y, Z\n'
                             ' 2: output interpolated survey as MD, INCL, AZIM\n'
                             ' 3: output interpolated survey as Cartesian X, Y, Z\n')
    wdb.add_argument('--wdbinterval', type=validintervalrange, default=50.0,
                        help='flt >= 0.1: interpolation interval along MD in output mode 2/3 (def: %(default)s)')
    # well marker section
    mdb = parser.add_argument_group('Keywords to generate well marker database')
    mdb.add_argument('--mrkfile', type=str, default='sample-markers.txt',
                        help='%(type)s: CSV file containing well name, marker code, depth, and optional'
                             'dip orientations (def: %(default)s)')
    mdb.add_argument('--mrkfilehd', type=int, default=1,
                        help='%(type)s: header lines to skip in marker file (def: %(default)s)')
    mdb.add_argument('--mrkfilecol', default=(1, 2, 3, 4, 5),
                        help='TUP(5 * INT): index # of rows containing WELL NAME, MARKER CODE, MD [length],'
                             'DIP(opt) [deg], DAZIM(opt) [deg] (def: %(default)s)')
    # stratigraphy section
    strat = parser.add_argument_group('Keywords to load stratigraphy for marker import')
    strat.add_argument('--stratdeffile', type=str, default='sample-stratdef.txt',
                        help='R|%(type)s: fixed-format CSV file containing marker code,\n'
                             'marker name and optional data\n'
                             '(def: %(default)s)')
    strat.add_argument('--stratordfile', type=str, default='sample-stratorder.txt',
                        help='R|%(type)s: fixed-format CSV file containing white list\n'
                             'of valid markers in order of stratigraphic age\n'
                             '(def: %(default)s)')
    # parse keywords
    try:
        # for zero-length arguments show help method
        if len(sys.argv) == 1 and manualargs is None:
            parser.print_help(sys.stderr)
            raise SystemExit('Nothing to do')
        # parse arguments and throw SystemExit for bad keywords
        # in default behavior manualargs == None and parser uses sys.argv
        args = parser.parse_args(manualargs)
        # display resulting Namespace object
        if debug:
            print(terminal*'=')
            print('Parsed namespace:', args)
            print(terminal*'=')
            print('Parsed dict:', vars(args))
        # return keywords in Namespace object as a dictionary
        return vars(args)
    except SystemExit as err:
        # https://stackoverflow.com/questions/19804254/how-to-protect-the-python-interpreter-against-termination-when-a-called-module-p
        print('Warning: Catching "'+str(err)+'" System Exit')
        if SystemExit.code == 2: 
            parser.print_help()
        sys.exit(0)
        # for testing parameters
        # return None


def getstatickeywords():
    """ for clarity and non-script usage define defaults for all valid keywords"""
    statargs = dict()
    # general section
    # STR: path to data directory
    statargs['datadir'] = '.\\data'
    # STR('ft', 'm'): input and output unit for vertical length (Z)
    statargs['depthunit'] = 'ft'
    # STR('ft', 'm'): input and output units for horizontal lengths (X,Y)
    statargs['surfaceunits'] = 'ft'
    # BOOL: verbose / debug output
    statargs['verbose'] = False
    # well database section
    # STR: CSV file containing well name, well head origin, and respective filename for directional survey
    statargs['wdbfile'] = 'sample-wellheads.txt'
    # INT: header lines to skip in well head file
    statargs['wdbfilehd'] = 1
    # TUP(5 * INT): indeces of rows containing WELL NAME, X, Y, KB, FILENAME
    statargs['wdbfilecol'] = (1, 2, 3, 4, 5)
    # INT: specifies output mode for directional survey file
    #      0: no output
    #      1: output original survey as Cartesian X, Y, Z
    #      2: output interpolated survey as MD, INCL, AZIM
    #      3: output interpolated survey as Cartesian X, Y, Z
    statargs['wdbmode'] = 2
    # FLOAT: interpolation interval along MD w.r.t. output mode >=.01
    statargs['wdbinterval'] = 50.0
    # well marker section
    # STR: CSV file containing well name, marker code, depth, and optional dip orientations
    statargs['mrkfile'] = 'sample-markers.txt'
    # INT: header lines to skip in marker file
    statargs['mrkfilehd'] = 1
    # TUP(5 * INT): indeces of rows containing WELL NAME, MARKER CODE, MD [length], DIP(opt) [deg], DAZIM(opt) [deg]
    statargs['mrkfilecol'] = (1, 2, 3, 4, 5)
    # stratigraphy section
    # STR: fixed-format CSV file containing marker code, marker name and optional data
    statargs['stratdeffile'] = 'sample-stratdef.txt'
    # STR: fixed-format CSV file containing white list of valid markers in order of stratigraphic age
    statargs['stratordfile'] = 'sample-stratorder.txt'
    return statargs


def buildwelldb(kwargs):
    """ pop and prepare parameter dict and build well db"""
    debug = False
    general = ['datadir', 'depthunit', 'surfaceunits', 'verbose']
    specific = {'filename_in': 'wdbfile', 'headerlines_in': 'wdbfilehd', 'columns_in': 'wdbfilecol',
                'mode': 'wdbmode', 'interval': 'wdbinterval'}
    wdbargs = dict()
    try:
        for item in general:
            wdbargs[item] = kwargs[item]
        for key, value in specific.items():
            if debug:
                print('key:', key, ', value:', value, ', KWarg:', kwargs[value])
            wdbargs[key] = kwargs.pop(value)
    except KeyError:
        print('Exception: Key not found during remapping...')
        print(kwargs, wdbargs)
    if debug:
        print('Remapped args:\n', wdbargs)
    return WellDatabase(**wdbargs)


def buildmarkerdb(welldb, kwargs):
    """ pop and prepare parameter dict and build marker db

    :param welldb:
    :param kwargs:
    :return: WellMarkerLoading object
    """
    debug = False
    general = ['datadir', 'verbose']
    specific = {'filename_in': 'mrkfile', 'headerlines_in': 'mrkfilehd', 'columns_in': 'mrkfilecol',
                'filename_strat_def': 'stratdeffile', 'filename_strat_order': 'stratordfile'}
    mdbargs = {}
    try:
        # todo
        mdbargs['welldatabase'] = welldb
        for item in general:
            mdbargs[item] = kwargs[item]
        for key, value in specific.items():
            if debug:
                print('key:', key, ', value:', value, ', KWarg:', kwargs[value])
            mdbargs[key] = kwargs.pop(value)
    except KeyError:
        print('Exception: Key not found during remapping...')
        print(kwargs, mdbargs)
    if debug:
        print('Remapped args:\n', mdbargs)
    return WellMarkerLoading(**mdbargs)


def main():
    """
    main function is a wrapper for parsing keywords and executing main functions
    """
    terminal = 79                               # terminal width excluding EOL
    debug = False
    testing = False
    kwargs = None

    # parse keywords from command line
    # quick test manual arguments to simulate command line
    # kwargs = parse(['--mode', '1', '--verbose', '1'])
    # normal parsing of arguments, btw. program fails with unknown/bad parameters
    #try:
    #    kwargs = parse()
    # parser will throw sys.exit() internally and externally,
    # we stop execution, then - 'finally' not needed at this stage
    #except SystemExit:
    #    os._exit(1)
    # in production the following block ist disabled
    # in order to only allow access by command line and file data
    if kwargs is None:
        print('Warning: Parser completely failed - using internal defaults')
        kwargs = getstatickeywords()
    print(terminal*'=')
    if debug:
        print('Args before generating WDB:\n', kwargs)
        print(terminal*'=')
    welldb = buildwelldb(kwargs)
    if debug:
        print(welldb)
        print(terminal*'=')
        print('Args before generating MDB:\n', kwargs)
        print(terminal*'=')
    markerdb = buildmarkerdb(welldb, kwargs)
    if debug:
        markerdb.print_strat_markers()
        print(terminal*'=')
        print('Args after generating MDB:\n', kwargs)
        print(terminal*'=')
    if testing:
        print(terminal*'=')
        print('boreholetools testing'.ljust(terminal, '-'))
        print(terminal*'=')
        welldb = WellDatabase(**kwargs)
        transform = TransformBoreHoleSurvey(datadir='data', filename_in='sample-borehole.txt', mode=2, verbose=False)
        point = DipPoint(45, 0)
        dmarker = DipMarker(5000, 45, 10, transform)
    print(terminal*'=')
    print('run completed without errors...')
    print(terminal*'=')
    return 0


##########################################################################
# Check to see if this file is being executed as the 'main' python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if __name__ == '__main__':
    main()
