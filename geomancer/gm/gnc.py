#!/usr/bin/env python

import ogr
import glob
import logging
from optparse import OptionParser
import os
import csv

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command",
                      help="Command to run",
                      default=None)
    parser.add_option("-d", "--data-dir", dest="datadir",
                      help="Data directory",
                      default=None)
    parser.add_option("-i", "--input-filename", dest="infile",
                      help="The name of the file for input",
                      default=None)
    parser.add_option("-o", "--output-filename", dest="outfile",
                      help="The name of the file for output",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    command = options.command.lower()
    
    logging.info('COMMAND %s' % command)

    if options.datadir == None:
        logging.info('No data directory to process. Aborting.')
        return

    os.chdir(options.datadir)
    
    if command=='gnc':
        logging.info('Loading entities from directory %s to %s.' % (options.datadir, options.outfile) )
        filecount=0
        featurecount = 0
        
        f = glob.glob("*.shp")[0]
        ds = ogr.Open (f)
        lyr = ds.GetLayerByName( f.replace('.shp','') )
        lyrdef = lyr.GetLayerDefn()
        fieldcount = lyrdef.GetFieldCount()
        header=[]
        feat = lyr[0]
        for i in range(fieldcount):
            fld = lyrdef.GetFieldDefn(i)
            name = fld.GetNameRef()
            header.append(name)
        header.append('x')
        header.append('y')
        writer = csv.DictWriter(open(options.outfile,'wb'), header, delimiter=',', quotechar='"')
        writer.writerow( dict((f,f) for f in header)) 
        for f in glob.glob("*.shp"):
            ds = ogr.Open (f)
            if ds is None:
                print "Open %s failed." % f
                return
            filecount += 1
            lyr = ds.GetLayerByName( f.replace('.shp','') )
            lyrdef = lyr.GetLayerDefn()
            fieldcount = lyrdef.GetFieldCount()
            filefeaturecount = 0 
            for feat in lyr:
                row = dict()
                geom = feat.GetGeometryRef()
                x=geom.GetPoint()[0]
                y=geom.GetPoint()[1]
                row['x']=x
                row['y']=y
                filefeaturecount += 1
                featurecount += 1
                for i in range(fieldcount):
                    fld = lyrdef.GetFieldDefn(i)
                    name = fld.GetNameRef()
                    row[name]=feat.GetField(name)
                writer.writerow(row)
            print 'FILE: %s FIELDS: %s FEATURES: %s' % (f,fieldcount,filefeaturecount)
        print 'FILES: %s FEATURES: %s' % (filecount,featurecount)
        return

if __name__ == "__main__":
    main()
