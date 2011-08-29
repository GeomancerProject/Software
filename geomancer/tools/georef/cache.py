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
    
# Setup local cache
CREATE_SQL = 'create table if not exists cache (key text, value text)'
GET_SQL = 'select value from cache where key = ?'
PUT_SQL = 'insert into cache (key, value) values (?, ?)'
CONN = sqlite3.connect('gm.cache.sqlite3.db', check_same_thread=False)
CONN.cursor().execute(CREATE_SQL)

# Setup remote cache
SERVER = None
HOST = 'localhost:8080'

def _setup_local(filename):
    global CONN
    CONN = sqlite3.connect(filename, check_same_thread=False)
    CONN.cursor().execute(CREATE_SQL)

def _setup_remote(host=HOST):
    global HOST
    global SERVER
    HOST = host
    email, passwd = CredentialsPrompt('the Geomancer remote cache at %s' % HOST)
    SERVER = AppEngine(HOST, email, passwd)

def _assert_key(key):
    assert key is not None
    assert isinstance(key, str) or isinstance(key, unicode)

def _assert_value(value):
    assert value is not None

class LocalCache(object):
    """Local key/value cache where values are stored as JSON."""

    @classmethod
    def get(cls, key):
        _assert_key(key)
        hit = CONN.cursor().execute(GET_SQL, (key,)).fetchone()
        if hit:
            return simplejson.loads(hit[0])
                
    @classmethod
    def put(cls, key, value):
        _assert_key(key)
        _assert_value(value)
        CONN.cursor().execute(PUT_SQL, (key, simplejson.dumps(value)))
        CONN.commit()

class RemoteCache(object):
    """Remote cache based on App Engine for locality types and geocodes."""

    class Get(AppEngine.RPC):
        def __init__(self, key):
            self._kwargs = dict(key=key)
        def request_path(self):
            return '/cache/get'
        def payload(self):
            return None        
        def content_type(self):
            return ''    
        def timeout(self):
            return None  
        def kwargs(self):  
            return self._kwargs    

    class Put(AppEngine.RPC):
        def __init__(self, key, value):
            self._payload = urllib.urlencode(
                dict(key=key, value=simplejson.dumps(value)))
        def request_path(self):
            return '/cache/put'
        def payload(self):
            return self._payload        
        def content_type(self):
            return 'application/x-www-form-urlencoded'    
        def timeout(self):
            return None  
        def kwargs(self):  
            return {}
        
    @classmethod
    def get(cls, key):
        _assert_key(key)
        if not SERVER:
            _setup_remote()
        content = SERVER.send(RemoteCache.Get(key))
        hit = None
        if content:
            hit = simplejson.loads(content)
        return hit
    
    @classmethod
    def put(cls, key, value):
        _assert_key(key)
        _assert_value(value)
        if not SERVER:
            _setup_remote()
        logging.info('SERVER = %s' % SERVER)
        SERVER.send(RemoteCache.Put(key, value))

class Cache(object):
    """Cache for locality types and geocodes from local and remote storage."""

    @classmethod
    def config(cls, remote_host=None, local_filename=None):
        if remote_host:
            _setup_remote(remote_host)
        if local_filename:
            _setup_local(local_filename)

    @classmethod
    def get(cls, key):
        value = LocalCache.get(key)
        if value:
            logging.info('LocalCache HIT: %s=%s' % (key, value))
            return value
        logging.info('LocalCache MISS: key=%s' % key)
        value = RemoteCache.get(key)
        if value:
            logging.info('RemoteCache HIT: %s=%s' % (key, value))
            LocalCache.put(key, value)
            return value
        logging.info('RemoteCache MISS: key=%s' % key)
    
    @classmethod
    def put(cls, key, value):
        logging.info('Cache UPDATE: %s=%s' % (key, value))
        LocalCache.put(key, value)
        RemoteCache.put(key, value)
