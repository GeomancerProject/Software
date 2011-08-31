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

from core import *
from bb import Point, BoundingBox
import logging

test_response_ca = {
   "results" : [
      {
         "address_components" : [
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
         "formatted_address" : "California, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 42.00951690,
                  "lng" : -114.1312110
               },
               "southwest" : {
                  "lat" : 32.5288320,
                  "lng" : -124.4820030
               }
            },
            "location" : {
               "lat" : 36.7782610,
               "lng" : -119.41793240
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 41.21563630,
                  "lng" : -111.22213140
               },
               "southwest" : {
                  "lat" : 32.06836610,
                  "lng" : -127.61373340
               }
            }
         },
         "types" : [ "administrative_area_level_1", "political" ]
      }
   ],
   "status" : "OK"
}

test_response_alameda = {
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "Alameda",
               "short_name" : "Alameda",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Alameda",
               "short_name" : "Alameda",
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
         "formatted_address" : "Alameda, CA, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 37.80062789999999,
                  "lng" : -122.2237790
               },
               "southwest" : {
                  "lat" : 37.707630,
                  "lng" : -122.3402810
               }
            },
            "location" : {
               "lat" : 37.76520650,
               "lng" : -122.24163550
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 37.80048090,
                  "lng" : -122.17760580
               },
               "southwest" : {
                  "lat" : 37.72991530,
                  "lng" : -122.30566520
               }
            }
         },
         "types" : [ "locality", "political" ]
      }
   ],
   "status" : "OK"
}

test_response_berkeley = {
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Alameda",
               "short_name" : "Alameda",
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
         "formatted_address" : "Berkeley, CA, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 37.90582390,
                  "lng" : -122.2341790
               },
               "southwest" : {
                  "lat" : 37.8357270,
                  "lng" : -122.3677810
               }
            },
            "location" : {
               "lat" : 37.87159260,
               "lng" : -122.2727470
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 37.90681610,
                  "lng" : -122.20871730
               },
               "southwest" : {
                  "lat" : 37.83635220,
                  "lng" : -122.33677670
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Ocean",
               "short_name" : "Ocean",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "New Jersey",
               "short_name" : "NJ",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Berkeley, NJ, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.07674290
               },
               "southwest" : {
                  "lat" : 39.756830,
                  "lng" : -74.3292630
               }
            },
            "location" : {
               "lat" : 39.89719960,
               "lng" : -74.18271190
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.07674290
               },
               "southwest" : {
                  "lat" : 39.756830,
                  "lng" : -74.3292630
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Holiday City-Berkeley",
               "short_name" : "Holiday City-Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Ocean",
               "short_name" : "Ocean",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "New Jersey",
               "short_name" : "NJ",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Holiday City-Berkeley, NJ, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.2403250
               },
               "southwest" : {
                  "lat" : 39.9415410,
                  "lng" : -74.3224790
               }
            },
            "location" : {
               "lat" : 39.96457970,
               "lng" : -74.27075090
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.2403250
               },
               "southwest" : {
                  "lat" : 39.9415410,
                  "lng" : -74.3224790
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Proviso",
               "short_name" : "Proviso",
               "types" : [ "administrative_area_level_3", "political" ]
            },
            {
               "long_name" : "Cook",
               "short_name" : "Cook",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "Illinois",
               "short_name" : "IL",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Berkeley, IL, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 41.899830,
                  "lng" : -87.89541290
               },
               "southwest" : {
                  "lat" : 41.87309590,
                  "lng" : -87.92061090
               }
            },
            "location" : {
               "lat" : 41.88891940,
               "lng" : -87.90339560
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 41.899830,
                  "lng" : -87.89541290
               },
               "southwest" : {
                  "lat" : 41.87309590,
                  "lng" : -87.92061090
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Norwood",
               "short_name" : "Norwood",
               "types" : [ "administrative_area_level_3", "political" ]
            },
            {
               "long_name" : "St Louis",
               "short_name" : "St Louis",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "Missouri",
               "short_name" : "MO",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            },
            {
               "long_name" : "63145",
               "short_name" : "63145",
               "types" : [ "postal_code" ]
            }
         ],
         "formatted_address" : "Berkeley, MO 63145, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 38.773750,
                  "lng" : -90.3105690
               },
               "southwest" : {
                  "lat" : 38.7197740,
                  "lng" : -90.3533350
               }
            },
            "location" : {
               "lat" : 38.75449520,
               "lng" : -90.33122560
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 38.773750,
                  "lng" : -90.3105690
               },
               "southwest" : {
                  "lat" : 38.7197740,
                  "lng" : -90.3533350
               }
            }
         },
         "types" : [ "locality", "political" ]
      }
   ],
   "status" : "OK"
}

#def parse_loc(loc, loctype):
#    parts={}
#    status=''
#    if loctype.lower()=='f':
#        if len(loc)==0:
#            logging.info('No feature found in %s' % loc)
#            status='No feature'
#
#        # Try to construct a Feature from the remainder
#        features=set()
#        feature=loc.strip()
#        features.add(feature)
#        if len(status)==0:
#            status='complete'
#            interpreted_loc=feature
#        parts = {
#            'verbatim_loc': loc,
#            'locality_type': loctype,
#            'features': features,
#            'interpreted_loc': interpreted_loc,
#            'status': status
#            }                
#        
#    if loctype.lower()=='foh':
#        offsetval=None
#        offsetindex=0
#        offsetunit=None
#        offsetunitindex=0
#        heading=None
#        interpreted_loc=None
#        status=''
#        tokens = [x.strip() for x in loc.split()]
#        i=-1
#        rest=[]
#        for token in tokens:
#            i+=1
#            if offsetval is None and is_number(token):
#                # TODO: fails for tokens that are distances as words (five).
#                #       and tokens that consist of mixed numbers (5 1/2)
#                offsetval=token
#                offsetindex=i
#                continue
#            if offsetval is not None and offsetunit is None and get_unit(token):
#                # TODO: fails for tokens that consist of more than one word (nautical miles).
#                offsetunitinfo = get_unit(token)
#                offsetunit = offsetunitinfo.name
#                offsetunitindex=i
#                continue
#            if heading is None and offsetunitindex==i-1 and get_heading(token):
#                headinginfo = get_heading(token)
#                heading = headinginfo.name
#                continue
#            rest.append([i,token])
#
#        if offsetval is None:
#            logging.info('No offset found in %s' % loc)
#            status='%s, no offset' % status
#        if offsetunit is None:
#            logging.info('No distance unit found in %s' % loc)
#            status='%s, no units' % status
#        if heading is None:
#            logging.info('No heading found in %s' % loc)
#            status='%s, no heading' % status
#        if len(rest)==0:
#            logging.info('No feature found in %s' % loc)
#            status='%s, no feature' % status
#
#        # Try to construct a Feature from the remainder
#        features=set()
#        feature=''
#        for f in rest:
#            feature = ' %s %s' % (feature,f[1])
#        feature=feature.strip()
#        features.add(feature)
#        status=status.lstrip(', ')
#        if len(status)==0:
#            status='complete'
#            interpreted_loc='%s %s %s %s' % (offsetval, offsetunit, heading, feature)
#        parts = {
#            'verbatim_loc': loc,
#            'locality_type': loctype,
#            'offset_value': offsetval,
#            'offset_unit': offsetunit,
#            'heading': heading,
#            'features': features,
#            'interpreted_loc': interpreted_loc,
#            'status': status
#            }                
#    return parts
def main():
    geoms_ca=GeocodeResultParser.get_feature_geoms('CA',test_response_ca)
    bb_ca=GeometryParser.get_bb(geoms_ca[0])
    
    geoms_alameda=GeocodeResultParser.get_feature_geoms('Alameda', test_response_alameda)
    bb_alameda=GeometryParser.get_bb(geoms_alameda[0])
    
    intersection = bb_ca.intersection(bb_alameda)
    
    geoms_berkeley=GeocodeResultParser.get_feature_geoms('Berkeley', test_response_berkeley)
    bb_berkeley=GeometryParser.get_bb(geoms_berkeley[0])

    intersection = intersection.intersection(bb_berkeley)

    print parse('5 mi N Berkeley', 'foh')

if __name__ == '__main__':
    main()
