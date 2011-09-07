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

"""This module provides exporting options for georef."""

from authorization.oauth import OAuth
from sql.sqlbuilder import SQL
import ftclient
from fileimport.fileimporter import CSVImporter


class GoogleFusionTablesApi(object):
    def __init__(self, consumer_key, consumer_secret):
        #url, token, secret = OAuth().generateAuthorizationURL(consumer_key, consumer_secret, consumer_key)
        #print "Visit this URL in a browser: ", url
        #raw_input("Hit enter after authorization")  
        #token, secret = OAuth().authorize(consumer_key, consumer_secret, token, secret)
        self.oauth_client = ftclient.OAuthFTClient(consumer_key, consumer_secret)

    def export(self, filename, tablename=None, datatypes=None):
        """Creates a new Fusion Table from a filename and returns the table id."""    
        return int(CSVImporter(self.oauth_client).importFile(filename, tablename, datatypes))


