#!/usr/bin/python #Linux shebang plus chmod to make executable
#------------------------------------------------------------
# FILENAME: fileio.py
# VERSION: 1.0 - Python 3.6
# PURPOSE:
# AUTHOR: MVS
# LAST CHANGE: 04/09/2018
#------------------------------------------------------------
""" tools for reading/writing CSV files
"""

import csv
import sys

class BHReaderWriter(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('datadir', '..\\data')
        kwargs.setdefault('filename_in', 'sample-borehole.txt')
        kwargs.setdefault('headerlines', 1)
        kwargs.setdefault('columns_in', (0,1,2))
        kwargs.setdefault('filename_out', 'dummy.txt')
        kwargs.setdefault('header_out', ('DEFAULT',))
        kwargs.setdefault('data_out', [])
        kwargs.setdefault('verbose', False)
        self.path = kwargs['datadir']
        self.filein = kwargs['filename_in']
        self.headerlines = kwargs['headerlines']
        self.columns = kwargs['columns_in']
        self.fileout = kwargs['filename_out']
        self.headerout = kwargs['header_out']
        self.dataout = kwargs['data_out']
        self.verbose = kwargs['verbose']
    
    def readHead(self):
        filename = self.path + '\\' + self.filein
        with open(filename, 'r') as file:
            outlines = self.headerlines
            output = []
            num_lines=sum(1 for _ in file)
            print('Number of lines in file:', num_lines)
            outlines = self.headerlines
            if(self.headerlines > num_lines):
                outlines = self.headerlines
            file.seek(0)
            for _ in range(outlines):
                output.append(file.readline())
        return output
        
    def readData(self):
        filename = self.path + '\\' + self.filein
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|', skipinitialspace=True)
            #skip header
            for _ in range(self.headerlines):
                next(csvreader)
            try:
                output = []
                for row in csvreader:
                    if len(row)==0:
                        continue
                    #copy lines into array
                    outline = []
                    #print(row)
                    for col in self.columns:
                        #print(col)
                        outline.append(row[col])
                    output.append(outline)
            except ValueError:
                print('Exception: File reading error occured')
                sys.exit()
        print('Number of rows read: ', len(output))
        if self.verbose : 
            for line in output:
                print(line)
        return output

    def writeData(self):
        filename = self.path + '\\' + self.fileout
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(self.headerout)
            for item in self.dataout:
                csvwriter.writerow(item)
        print('Number of points written: ', len(self.dataout))
        

if __name__ == '__main__':                  # call test environment only if module is called standalone
    TWIDTH=79                               # terminal width excluding EOL
    print(TWIDTH*'=')
    print('module test: fileio'.ljust(TWIDTH,'-'))
    print(TWIDTH*'=')

    print('Reading and Writing files:')
    rw = BHReaderWriter(headerlines=3)
    for line in rw.readHead():
        print(line.rstrip('\r\n'))
    data = [[1, 6, 3 ,6]]
    rw = BHReaderWriter(headerlines=1, columns_in=(1,0), filename_out='TestOut_fileio.txt', data_out=data, verbose=True)
    for line in rw.readData():
        print(line)
    rw.writeData()
else:
    print('Importing ' + __name__)
