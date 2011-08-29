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

"""This module provides a cache for locality types and geocodes."""

# Geomancer modules
from utils import AppEngine, CredentialsPrompt

# Standard Python modules
import logging
import simplejson
import sqlite3
import sys
import urllib

class LocalCache(object):
    """Local cache based on SQLite for locality types and geocodes."""

    def __init__(self, filename=None):
        if not filename:
            filename = 'gm.cache.sqlite3.db'
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        c = self.conn.cursor()
        c.execute('create table if not exists geocodes' +
                  '(address text, ' +
                  'response text)')    
        c.execute('create table if not exists loctypes' +
                  '(locname text, ' +
                  'loctype text, ' +
                  'scores text)') # scores is a JSON string
        c.close()

    def get_loctype(self, locname):
        """Returns a dictionary with keys loctype, locname, and scores."""
        sql = 'select loctype, scores from loctypes where locname = ?'
        result = self.conn.cursor().execute(sql, (locname.lower(),)).fetchone()
        if result:
            return dict(
                locname=locname, 
                loctype=result[0], 
                scores=simplejson.loads(result[1]))

    def put_loctype(self, hit):
        """Puts a locality type for a locality."""
        sql = 'insert into loctypes (locname, loctype, scores) values (?, ?, ?)'
        values = (hit['locname'].lower(), 
                  hit['loctype'], 
                  simplejson.dumps(hit['scores']))
        self.conn.cursor().execute(sql, values)
        self.conn.commit()

class RemoteCache(object):
    """Remote cache based on App Engine for locality types and geocodes."""

    class GetLoctype(AppEngine.RPC):

        def __init__(self, locname):
            self._kwargs = dict(locname=locname)

        def request_path(self):
            return '/cache/get_loctype'

        def payload(self):
            return None
        
        def content_type(self):
            return ''
    
        def timeout(self):
            return None
  
        def kwargs(self):  
            return self._kwargs

    class PutLoctype(AppEngine.RPC):

        def __init__(self, hit):
            locname = hit['locname']
            loctype = hit['loctype']
            scores = hit['scores']
            json = simplejson.dumps(
                dict( 
                    locname=locname,
                    loctype=loctype,
                    scores=scores))
            self._payload = urllib.urlencode(
                dict(
                    locname=locname,
                    loctype=loctype,
                    json=json))

        def request_path(self):
            return '/cache/put_loctype'

        def payload(self):
            return self._payload
        
        def content_type(self):
            return 'application/x-www-form-urlencoded'
    
        def timeout(self):
            return None
  
        def kwargs(self):  
            return {}

    def __init__(self, host, email, passwd):
        self.server = AppEngine(host, email, passwd)  

    def get_loctype(self, locname):
        content = self.server.send(RemoteCache.GetLoctype(locname))
        hit = None
        if content:
            hit = simplejson.loads(content)
        return hit

    def put_loctype(self, hit):
        self.server.send(RemoteCache.PutLoctype(hit))

class Cache(object):
    """Cache for locality types and geocodes from local and remote storage."""

    def __init__(self, host, creds=None, filename=None):
        self.host = host
        self.local = LocalCache(filename=filename)
        if creds:
            self.remote = RemoteCache(host, creds[0], creds[1])
        else:
            self.remote = None
    
    def get_loctype(self, locname):
        # Check local cache
        hit = self.local.get_loctype(locname)
        if not hit:
            logging.info('Local cache MISS - %s' % locname)
            # Check remote cache
            if not self.remote:
                self._setup_remote()
            hit = self.remote.get_loctype(locname)
            if hit:
                logging.info('Remote cache HIT - %s' % locname)
                # Update local cache
                self.local.put_loctype(hit)
            else:
                logging.info('Remote cache MISS - %s' % locname)
        else:
            logging.info('Local cache HIT - %s' % locname)
        return hit

    def put_loctype(self, hit):  
        logging.info('Cache update - %s=%s' % (hit['locname'], hit['loctype']))
        self.local.put_loctype(hit)
        if not self.remote:
            self._setup_remote()
        self.remote.put_loctype(hit)

    def _setup_remote(self):
        email, passwd = CredentialsPrompt('the Geomancer remote cache at %s' % self.host)
        self.remote = RemoteCache(self.host, email, passwd)
        
