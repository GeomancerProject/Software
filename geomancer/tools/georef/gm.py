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

# Just for testing
import setup_env
setup_env.fix_sys_path()

import cgi
import logging
from optparse import OptionParser
import simplejson
import sqlite3
import sys
import urllib
import urllib2
import yaml
import apiclient.errors
import gflags
import httplib2
import pprint
from abc import ABCMeta, abstractmethod, abstractproperty
from google.appengine.tools.appengine_rpc import HttpRpcServer

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

def _getoptions():
    ''' Parses command line options and returns them.'''
    parser = OptionParser()
    parser.add_option('-a', '--address', 
                      type='string', 
                      dest='address',
                      metavar='STRING', 
                      help='Address to geocode.')    
    parser.add_option('--config_file', 
                      type='string', 
                      dest='config_file',
                      metavar='FILE', 
                      help='YAML config file.')    
    parser.add_option('--filename', 
                      type='string', 
                      dest='filename',
                      metavar='FILE', 
                      help='CSV file with data to bulkload.')                          
    parser.add_option('--url', 
                      type='string', 
                      dest='url',
                      help='URL endpoint to /remote_api to bulkload to.')                          
    return parser.parse_args()[0]

class AppEngine(object):

    class RPC(object):
        """Abstract class for remote procedure calls."""

        __metaclass__ = ABCMeta

        @abstractmethod
        def request_path(self):
            """The path to send the request to, eg /api/appversion/create."""
            pass

        @abstractmethod
        def payload(self):
            """The body of the request, or None to send an empty request"""
            pass

        @abstractmethod
        def content_type(self):
            """The Content-Type header to use."""
            pass

        @abstractmethod
        def timeout(self):
            """Timeout in seconds; default None i.e. no timeout. Note: for large
            requests on OS X, the timeout doesn't work right."""
            pass

        @abstractmethod
        def kwargs(self):
            """Any keyword arguments."""
            pass

    def send(self, rpc):
        return self.server.Send(
            rpc.request_path(),
            rpc.payload(),
            rpc.content_type(),
            rpc.timeout(),
            **rpc.kwargs())

    def __init__(self, host, email, passwd):
        """Initializes the server with user credentials and app details."""
        logging.info('Host %s' % host)
        self.server = HttpRpcServer(
            host,
            lambda:(email, passwd),
            None,
            'geo-mancer',
            debug_data=True,
            secure=False)

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

    def __init__(self, host, email, passwd, filename=None):
        self.local = LocalCache(filename=filename)
        self.remote = RemoteCache(host, email, passwd)
    
    def get_loctype(self, locname):
        # Check local cache
        hit = self.local.get_loctype(locname)
        if not hit:
            logging.info('Local cache MISS - %s' % locname)
            # Check remote cache
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
        self.remote.put_loctype(hit)

class PredictionApi(object):

    def __init__(self, config, cache):
        self.config = config
        self.cache = cache
        self._set_flow()

    def get_type(self, query):
        storage = Storage('prediction.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            self._set_flow()
            credntials = run(self.FLOW, storage)
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build("prediction", "v1.3", http=http)
        try:
            train = service.training()
            body = {'input': {'csvInstance': [query]}}
            prediction = train.predict(body=body, data=self.config['model']).execute()
            json_content = prediction
            scores = []
            if json_content.has_key('outputLabel'):
                predict = json_content['outputLabel']
                scores = self._format_results(json_content['outputMulti'])
            else:
                predict = json_content['outputValue']
            logging.info('Predicted %s for %s' % (predict, query))
            return [predict, scores]
        except AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                   "the application to re-authorize")

    def _set_flow(self):
        self.FLOW = OAuth2WebServerFlow(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            scope='https://www.googleapis.com/auth/prediction',
            user_agent='geomancer/1.0')

    def _format_results(self, jsonscores):
        scores = {}
        for pair in jsonscores:
            for key, value in pair.iteritems():
                if key == 'label':
                    label = value
                elif key == 'score':
                    score = value
            scores[label] = score
        return scores


START = 'start'
PARSE = 'parse'
GEOCODE = 'geocode'
CALCULATE = 'calculate'
DONE = 'done'
FAIL = 'fail'

PREDICT_START = 'predict_start'
PREDICT_DONE = 'predict_done'
PREDICT_FAIL = 'predict_fail'

PREDICT_SQLITE_HIT = 'predict_sqlite_hit'
PREDICT_SQLITE_MISS = 'predict_sqlite_miss'
PREDICT_GEOMANCER_HIT = 'predict_geomancer_hit'
PREDICT_GEOMANCER_MISS = 'predict_geomancer_miss'
PREDICT_GOOGLE_HIT = 'predict_google_hit'
PREDICT_GOOGLE_MISS = 'predict_google_miss'

        
class Geomancer(object):

    """Class for georeferencing addresses."""
    
    def __init__(self, cache, predictor):
        self.cache = cache
        self.predictor = predictor

    def predict(self, localities):
        """Predicts locality type for each locality in a list."""
        for loc in localities:
            # Check cache for loctype
            hit = self.cache.get_loctype(loc.name)
            if not hit:
                # Get predicted loctype and update chace
                loctype, scores = self.predictor.get_type(loc.name)
                hit = dict(locname=loc.name, loctype=loctype, scores=scores)
                self.cache.put_loctype(hit)
            # Set loctype
            loc.type = hit['loctype']

        return localities

    def georeferece(self, location):
        """Georeferences a location."""
        localities = Locality.create_muti(location)
        logging.info('Georeferencing %s - %s' % (location, [x.name for x in localities]))
        localities_with_type = self.predict(localities)
        if len(localities_with_type) == 0:
            # Prediction fail
            logging.info('Unable to georeference %s (locality types unknown)' % location)
            return None
        for loc in localities_with_type:
            logging.info('"%s" -> %s' % (loc.name, loc.type))
        #localities_parsed = self.parse(localities_with_type)

class Locality(object):
    """Class representing a sub-locality."""
    
    @classmethod
    def create_muti(cls, location):
        """Return list of Locality objects by splitting location on ',' and ';'."""
        return [Locality(name.strip()) for name in set(reduce(            
                    lambda x,y: x+y, 
                    [x.split(';') for x in location.split(',')]))]

    def __init__(self, name):
        self.name = name
        self.type = None
        self.parts = {}
        self.features = set()
    
    def __repr__(self):
        return str(self.__dict__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    cache = Cache('localhost:8080', 'user@example.com', 'secret')
    config = yaml.load(open(options.config_file, 'r'))        
    predictor = PredictionApi(config, cache)
    geomancer = Geomancer(cache, predictor)
    results = geomancer.georeferece(options.address)
    logging.info(results)
    
    # Prototyping geocode stuff:

    # sql = 'select address,response from geocodes where address = ?'
    # c = conn.cursor()
    # cache = {}
    # address = options.address    
    # for row in c.execute(sql, (address,)):
    #     cache[row[0]] = row[
    # if cache.has_key(address):
    #     logging.info('CACHE HIT: address=%s' % address)
    #     sys.exit(1)
    # logging.info('CACHE MISS: address=%s' % address)
    # params = urllib.urlencode(dict(address=address, sensor='true'))
    # url = 'http://maps.googleapis.com/maps/api/geocode/json?%s' % params
    # response = simplejson.loads(urllib.urlopen(url).read())
    # logging.info('Geocode received from %s' % url)
    # sql = 'insert into geocodes values (?, ?)'
    # cursor = conn.cursor()
    # cursor.execute(sql, (address, simplejson.dumps(response)))
    # conn.commit() 
   
