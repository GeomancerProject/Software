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

import logging

def parse(loc, loctype):
    parts={}
    if loctype.lower()=='foh':
        offsetval=None
        offsetindex=0
        offsetunit=None
        offsetunitindex=0
        heading=None
        interpreted_loc=None
        status=''
        tokens = [x.strip() for x in loc.split()]
        i=-1
        rest=[]
        for token in tokens:
            i+=1
            if offsetval is None and is_number(token):
                # TODO: fails for tokens that are distances as words (five).
                #       and tokens that consist of mixed numbers (5 1/2)
                offsetval=token
                offsetindex=i
                continue
            if offsetval is not None and offsetunit is None and get_unit(token):
                # TODO: fails for tokens that consist of more than one word (nautical miles).
                offsetunitinfo = get_unit(token)
                offsetunit = offsetunitinfo.name
                offsetunitindex=i
                continue
            if heading is None and offsetunitindex==i-1 and get_heading(token):
                headinginfo = get_heading(token)
                heading = headinginfo.name
                continue
            rest.append([i,token])

        if offsetval is None:
            logging.info('No offset found in %s' % loc)
            status='%s, no offset' % status
        if offsetunit is None:
            logging.info('No distance unit found in %s' % loc)
            status='%s, no units' % status
        if heading is None:
            logging.info('No heading found in %s' % loc)
            status='%s, no heading' % status
        if len(rest)==0:
            logging.info('No feature found in %s' % loc)
            status='%s, no feature' % status

        # Try to construct a Feature from the remainder
        features=set()
        feature=''
        for f in rest:
            feature = ' %s %s' % (feature,f[1])
        feature=feature.strip()
        features.add(feature)
        status=status.lstrip(', ')
        if len(status)==0:
            status='complete'
            interpreted_loc='%s %s %s %s' % (offsetval, offsetunit, heading, feature)
        parts = {
            'verbatim_loc': loc,
            'locality_type': loctype,
            'offset_value': offsetval,
            'offset_unit': offsetunit,
            'heading': heading,
            'features': features,
            'interpreted_loc': interpreted_loc,
            'status': status
            }                
    return parts

def main():
    print parse('5mi N Berkeley', 'foh')

if __name__ == '__main__':
    main()
