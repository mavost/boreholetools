#!/usr/bin/python #Linux shebang plus chmod to make executable
#------------------------------------------------------------
# FILENAME: boreholetools.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
#------------------------------------------------------------
""" boreholetools main control module
"""
import csv
import math

import sys
#add extra path into search list for paths
sys.path.insert(0,'H:\\09_Work\\python-workspace\\Code\\boreholetools\\modules')
print(sys.path)

try:
    from modules.boreholemath import TransformBoreHoleSurvey
    from modules.dipmath import DipPoint, DipMarker
except:
    print('Exception: Module not found')
    sys.exit()



def main():
    transform = TransformBoreHoleSurvey(datadir='data', filename_in='sample-borehole.txt', mode=2, verbose=False)
    point = DipPoint(45, 0)
    dmarker = DipMarker(5000, 45, 10, transform)
    
  

##########################################################################
# Check to see if this file is being executed as the 'main' python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
    main()