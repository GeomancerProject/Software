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
# import setup_env
# setup_env.fix_sys_path()

global verbosity
verbosity = 1

# Geomancer modules
from geomancer.parselocality import parse as parseloc
from cache import Cache
from localities import Locality, PredictionApi
from utils import UnicodeDictReader, UnicodeDictWriter, CredentialsPrompt

# Standard Python modules
import cgi
import logging
import optparse
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
        

class Geomancer(object):
    """Class for georeferencing addresses."""
    def __init__(self, predictor):
        self.predictor = predictor

    def predict(self, localities):
        """Predict locality type for each locality in a list."""
        for loc in localities:
            logging.info('Predicting locality type for "%s"' % loc.name)
            key = 'loctype-%s' % loc.name
            prediction = Cache.get(key)
            if not prediction:
                loctype, scores = self.predictor.get_type(loc.name)
                prediction = dict(locname=loc.name, loctype=loctype, scores=scores)
                Cache.put(key, prediction)
            loc.type = prediction['loctype']
            loc.type_scores = prediction['scores']
            logging.info('Predicted "%s" for "%s"' % (loc.type, loc.name))
        return localities

    def parse(self, localities):
        for loc in localities:
            logging.info('Parsing "%s" based on locality type "%s"' % (loc.name, loc.type))
            loc.parts = parseloc(loc.name, loc.type)
            logging.info('Parsed features "%s"' % list(loc.parts['features']))
        return localities

    def geocode(self, localities):        
        for loc in localities:
            loc.feature_geocodes = {}
            for feature in loc.parts['features']:              
                logging.info('Geocoding feature "%s"' % feature)  
                key = 'geocode-%s' % feature
                geocode = Cache.get(key)
                if not geocode:
                    geocode = self._google_geocode(feature)
                    Cache.put(key, geocode)
                loc.feature_geocodes[feature] = geocode 
                logging.info('Geocoded feature "%s"' % feature)
        return localities

    def georeferece(self, location):
        """Georeferences a location."""
        localities = Locality.create_muti(location)
        logging.info('Georeferencing "%s" with sub-localities %s' % (location, [x.name for x in localities]))
        localities_predicted = self.predict(localities)
        localities_parsed = self.parse(localities_predicted)
        localities_geocoded = self.geocode(localities_parsed)

    def _google_geocode(self, address):
        params = urllib.urlencode(dict(address=address, sensor='true'))
        url = 'http://maps.googleapis.com/maps/api/geocode/json?%s' % params
        return simplejson.loads(urllib.urlopen(url).read())

def PrintUpdate(msg):
    if verbosity > 0:
        print >>sys.stderr, msg

def StatusUpdate(msg):
    PrintUpdate(msg)

def ErrorUpdate(msg):
    PrintUpdate('ERROR: %s' % msg)

def _GeoreferenceOptions(self, parser):
    parser.add_option('-a', '--address', type='string', dest='address',
                      help='Address to geocode.')    
    parser.add_option('--config_file', type='string', dest='config_file',
                      metavar='FILE', help='YAML config file.')
    parser.add_option('--filename', type='string', dest='filename',
                      metavar='FILE', help='CSV file with data to bulkload.')                      
    parser.add_option('--url', type='string', dest='url',
                      help='URL endpoint to /remote_api to bulkload to.')                          
    parser.add_option('--host', type='string', dest='host',
                      help='App Engine host name for cache and bulkloading.')                          
    parser.add_option('--num_threads', type='int', dest='num_threads', default=5,
                      help='Number of threads to transfer records with.')                          
    parser.add_option('--batch_size', type='int', dest='batch_size', default=1,
                      help='Number of records to pst in each request.')                          
    parser.add_option('-l', '--localhost', dest='localhost', action='store_true', 
                      help='Shortcut for bulkloading to http://localhost:8080/_ah/remote_api')                          

class Action(object):
    """Contains information about a command line action."""

    def __init__(self, function, usage, short_desc, long_desc='',
                 error_desc=None, options=lambda obj, parser: None,
                 uses_basepath=True):
        """Initializer for the class attributes."""
        self.function = function
        self.usage = usage
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.error_desc = error_desc
        self.options = options
        self.uses_basepath = uses_basepath

    def __call__(self, appcfg):
        """Invoke this Action on the specified Vn."""
        method = getattr(appcfg, self.function)
        return method()

class Gm(object):
    
    """Class for executing command line actions."""

    # Actions
    actions = dict(
        help=Action(
            function='Help',
            usage='%prog help <action>',
            short_desc='Print help for a specific action.',
            uses_basepath=False),
        georef=Action( 
            function='Georeference',
            usage='%prog [options] georef <file>',
            options=_GeoreferenceOptions,
            short_desc='Georeference.',
            long_desc="""TODO"""))

    def __init__(self, argv, parser_class=optparse.OptionParser):
        self.parser_class = parser_class
        self.argv = argv
        self.parser = self._GetOptionParser()
        for action in self.actions.itervalues():
            action.options(self, self.parser)
        self.options, self.args = self.parser.parse_args(argv[1:])
        if len(self.args) < 1:
            self._PrintHelpAndExit()
        action = self.args.pop(0)
        if action not in self.actions:
            self.parser.error("Unknown action: '%s'\n%s" %
                              (action, self.parser.get_description()))
        self.action = self.actions[action]
        self.parser, self.options = self._MakeSpecificParser(self.action)
        if self.options.help:
            self._PrintHelpAndExit()
        if self.options.verbose == 2:
            logging.getLogger().setLevel(logging.INFO)
        elif self.options.verbose == 3:
            logging.getLogger().setLevel(logging.DEBUG)
        verbosity = self.options.verbose

    def Run(self):
        try:
            self.action(self)
        except Exception as e:
            import traceback
            traceback.print_tb(sys.exc_info()[2])
            logging.info(e)
            raise e
        return 0

    def Help(self, action=None):
        """Prints help for a specific action."""
        if not action:
            if len(self.args) > 1:
                self.args = [' '.join(self.args)]

        if len(self.args) != 1 or self.args[0] not in self.actions:
            self.parser.error('Expected a single action argument. '
                              ' Must be one of:\n' +
                              self._GetActionDescriptions())
        action = self.args[0]
        action = self.actions[action]
        self.parser, unused_options = self._MakeSpecificParser(action)
        self._PrintHelpAndExit(exit_code=0)

    def Georeference(self):
        if self.options.localhost:
            host = 'localhost:8080'
        else:
            host = self.options.host
        config = yaml.load(open(self.options.config_file, 'r'))        
        predictor = PredictionApi(config)
        geomancer = Geomancer(predictor)
        results = geomancer.georeferece(self.options.address)  
        return results

    def _PrintHelpAndExit(self, exit_code=2):
        """Prints the parser's help message and exits the program."""
        self.parser.print_help()
        sys.exit(exit_code)

    def _GetActionDescriptions(self):
        """Returns a formatted string containing the short_descs for all actions."""
        action_names = self.actions.keys()
        action_names.sort()
        desc = ''
        for action_name in action_names:
            desc += '  %s: %s\n' % (action_name, self.actions[action_name].short_desc)
        return desc

    def _MakeSpecificParser(self, action):
        """Creates a new parser with documentation specific to 'action'."""
        parser = self._GetOptionParser()
        parser.set_usage(action.usage)
        parser.set_description('%s\n%s' % (action.short_desc, action.long_desc))
        action.options(self, parser)
        options, unused_args = parser.parse_args(self.argv[1:])
        return parser, options

    def _GetOptionParser(self):
        """Creates an OptionParser with generic usage and description strings."""

        class Formatter(optparse.IndentedHelpFormatter):
            """Custom help formatter that does not reformat the description."""
            def format_description(self, description):
                """Very simple formatter."""
                return description + '\n'
        desc = self._GetActionDescriptions()
        desc = ('Action must be one of:\n%s'
                'Use \'help <action>\' for a detailed description.') % desc
        parser = self.parser_class(usage='%prog [options] <action>',
                                   description=desc,
                                   formatter=Formatter(),
                                   conflict_handler='resolve')
        parser.add_option('-h', '--help', action='store_true',
                          dest='help', help='Show the help message and exit.')
        parser.add_option('-v', '--verbose', action='store_const', const=2,
                          dest='verbose', default=1,
                          help='Print info level logs.')
        return parser


def main(argv):
    logging.basicConfig(format=('%(asctime)s %(levelname)s: %(message)s'))
    try:
        result = Gm(argv).Run()
        if result:
            sys.exit(result)
    except KeyboardInterrupt:
        StatusUpdate('Interrupted.')
        sys.exit(1)
    except Exception as e:
        logging.info(e)

if __name__ == '__main__':
    main(sys.argv)
    
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
   