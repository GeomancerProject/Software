#!/usr/bin/env python

# Copyright 2011 The Regents of the University of California 
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

__author__ = "Aaron Steele (eightysteele@gmail.com)"
__copyright__ = "Copyright 2011 The Regents of the University of California"
__contributors__ = ["John Wieczorek (gtuco.btuco@gmail.com)"]

# Standard Python modules
import simplejson
import urllib

class GoogleGeocodingApi(object):
    @classmethod
    def geocode(cls, address):
        params = urllib.urlencode(dict(address=address, sensor='true'))
        url = 'http://maps.googleapis.com/maps/api/geocode/json?%s' % params
        return simplejson.loads(urllib.urlopen(url).read())
