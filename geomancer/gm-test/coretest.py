#!/usr/bin/env python

# Copyright 2011 Regents of the University of California
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "John Wieczorek (gtuco.btuco@gmail.com)"
__copyright__ = "Copyright 2011 The Regents of the University of California"
__contributors__ = ["Aaron Steele (eightysteele@gmail.com)"]

import sys

# Hack to get ../gm on sys.paht
sys.path.append('../')

from gm.core import *
from gm import constants

import math
import logging
import os
import unittest
import simplejson

class TestGeomancer(unittest.TestCase):
    
    def test_distanceunits(self):
        distunits = constants.DistanceUnits.all()
        for unit in distunits:
            logging.info(unit)

    def test_headings(self):
        headings = constants.Headings.all()
        for heading in headings:
            logging.info(heading)

    def test_datums(self):
        datums = constants.Datums.all()
        for datum in datums:
            logging.info(datum)

    def test_georef(self):
        geocode = simplejson.loads("""{
       "results" : [
          {
             "address_components" : [
                {
                   "long_name" : "Mountain View",
                   "short_name" : "Mountain View",
                   "types" : [ "locality", "political" ]
                },
                {
                   "long_name" : "San Jose",
                   "short_name" : "San Jose",
                   "types" : [ "administrative_area_level_3", "political" ]
                },
                {
                   "long_name" : "Santa Clara",
                   "short_name" : "Santa Clara",
                   "types" : [ "administrative_area_level_2", "political" ]
                },
                {
                   "long_name" : "California",
                   "short_name" : "CA",
                   "types" : [ "administrative_area_level_1", "political" ]
                },
                {
                   "long_name" : "United States",
                   "short_name" : "US",
                   "types" : [ "country", "political" ]
                }
             ],
             "formatted_address" : "Mountain View, CA, USA",
             "geometry" : {
                "bounds" : {
                   "northeast" : {
                      "lat" : 37.4698870,
                      "lng" : -122.0446720
                   },
                   "southwest" : {
                      "lat" : 37.35654100000001,
                      "lng" : -122.1178620
                   }
                },
                "location" : {
                   "lat" : 37.38605170,
                   "lng" : -122.08385110
                },
                "location_type" : "APPROXIMATE",
                "viewport" : {
                   "northeast" : {
                      "lat" : 37.42150620,
                      "lng" : -122.01982140
                   },
                   "southwest" : {
                      "lat" : 37.35058040,
                      "lng" : -122.14788080
                   }
                }
             },
             "types" : [ "locality", "political" ]
          }
       ],
       "status" : "OK"
    }""")
        logging.info(georef_feature(geocode))

    def test_point2wgs84(self):
        agd66point = Point(144.966666667, -37.8)
        wgs84point = point2wgs84(agd66point, Datums.AGD84)
        logging.info(wgs84point)
        logging.info(Datums.AGD84)
    #    144.96797984155188, -37.798491994062296
    #    144.96798640000000, -37.798480400000000

    def test_distanceprecision(self):
        d = '110'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
    
        
        d = '0'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
    
        d = '1'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '2'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '5'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '9'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '11'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '12'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '19'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '20'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '21'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '49'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '50'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '51'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '99'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '100'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '101'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '109'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '110'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '111'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '149'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '150'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '151'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '199'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '200'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '201'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '210'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '999'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '1000'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
    
        
        d = '10.000'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.001'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.00'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.01'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.0'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.1'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.9'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.125'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.25'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.3333'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.5'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.625'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.75'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.5'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.66667'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        
    def test_georeference_feature(self):
        geocode = get_example_geocode()
        georef = georef_feature(geocode)
        logging.info('Georeference: %s'%(georef))
    
    def test_point_from_dist_at_bearing(self):
        point = Point(0,0)
        distance = 1000000
        bearing = 45 
        endpoint = get_point_from_distance_at_bearing(point, distance, bearing)
        logging.info("%s meters at bearing %s from %s, %s: %s"%(distance, bearing, point.lng, point.lat, endpoint) )
        
    def test_haversine_distance(self):
        point = Point(0,0)
        distance = 1000000
        bearing = 45 
        endpoint = get_point_from_distance_at_bearing(point, distance, bearing)
        hdist = haversine_distance(point, endpoint)
        logging.info("%s meters"%(hdist) )
        diff = math.fabs(distance - hdist) 
        if diff >= 0.5:
            logging.info("FAIL: test_haversine_distance(): difference = %s meters"%(diff) )
        else:
            logging.info("PASS: test_haversine_distance(): difference = %s meters"%(diff) )        

def get_example_geocode():
    """Returns an Google Geocoding JSON response for "Mountain View"."""
    geocode = simplejson.loads("""{
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "Mountain View",
               "short_name" : "Mountain View",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "San Jose",
               "short_name" : "San Jose",
               "types" : [ "administrative_area_level_3", "political" ]
            },
            {
               "long_name" : "Santa Clara",
               "short_name" : "Santa Clara",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "California",
               "short_name" : "CA",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Mountain View, CA, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 37.4698870,
                  "lng" : -122.0446720
               },
               "southwest" : {
                  "lat" : 37.35654100000001,
                  "lng" : -122.1178620
               }
            },
            "location" : {
               "lat" : 37.38605170,
               "lng" : -122.08385110
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 37.42150620,
                  "lng" : -122.01982140
               },
               "southwest" : {
                  "lat" : 37.35058040,
                  "lng" : -122.14788080
               }
            }
         },
         "types" : [ "locality", "political" ]
      }
   ],
   "status" : "OK"
}""")
    return geocode

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

