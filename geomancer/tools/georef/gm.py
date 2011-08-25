#!/usr/bin/env python

# Copyright 2011 Aaron Steele
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

__author__ = "Aaron Steele"

import cgi
import logging
from optparse import OptionParser
import simplejson
import sqlite3
import sys
import urllib
import urllib2

import apiclient.errors
import gflags
import httplib2
import pprint

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
                      help='Bulkload YAML config file.')    
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

def _setupdb():
    conn = sqlite3.connect('gm.sqlite.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('create table if not exists geocodes' +
              '(address text, ' +
              'response text)')
    c.close()
    return conn


class PredictionApi(object):
    FLAGS = gflags.FLAGS

    FLOW = OAuth2WebServerFlow(
        client_id='1077648189165-7filsif33gnm6i92opietsrihppauune.apps.googleusercontent.com',
        client_secret='p6u7L1V-aEw2e12CWy-k77eZ',
        scope='https://www.googleapis.com/auth/prediction',
        user_agent='prediction-cmdline-sample/1.0')
    
    gflags.DEFINE_enum('logging_level', 'ERROR',
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'Set the level of logging detail.')

    gflags.DEFINE_string(
        'object_name',
        None,
        'Full Google Storage path of csv data (ex bucket/object)')

    gflags.MarkFlagAsRequired('object_name')
    
    OBJECT_NAME_ARG = '--object_name=biogeomancer/locs.csv'

    @classmethod
    def predict(cls, query):
        argv = ['./gm.py', cls.OBJECT_NAME_ARG]  
        print argv
        # Let the gflags module process the command-line arguments
        try:
            argv = cls.FLAGS(argv)
        except gflags.FlagsError, e:
            print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], cls.FLAGS)
            sys.exit(1)

        # Set the logging according to the command-line flag
        logging.getLogger().setLevel(getattr(logging, cls.FLAGS.logging_level))

        storage = Storage('prediction.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credntials = run(cls.FLOW, storage)

        # Create an httplib2.Http object to handle our HTTP requests and authorize it
        # with our good Credentials.
        http = httplib2.Http()
        http = credentials.authorize(http)

        service = build("prediction", "v1.3", http=http)

        try:
            # Start training on a data set
            train = service.training()
            body = {'id' : cls.FLAGS.object_name}
            start = train.insert(body=body).execute()

            print 'Started training'
            pprint.pprint(start)

            import time
            # Wait for the training to complete
            while True:
                try:
                    # We check the training job is completed. If it is not it will return an error code.
                    status = train.get(data=cls.FLAGS.object_name).execute()
                    # Job has completed.
                    pprint.pprint(status)
                    break
                except apiclient.errors.HttpError as error:
                    # Training job not yet completed.
                    print 'Waiting for training to complete.'
                    time.sleep(10)

            print 'Training is complete'

            # Now make a prediction using that training
            body = {'input': {'csvInstance': [query]}}
            prediction = train.predict(body=body, data=cls.FLAGS.object_name).execute()
            print 'The prediction is:'
            pprint.pprint(prediction)


        except AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                   "the application to re-authorize")

            
class GooglePredictionApi(object):

    AUTH = None
    MODEL = 'biogeomancer/locs.csv'
    CREDS = 'prediction-creds.txt'

    @classmethod
    def predict(cls, query):
        if not cls.AUTH:
            u,p = open(cls.CREDS, 'r').read().split(':')
            cls.AUTH = cls.GetAuthentication(u.strip(), p.strip())
        results = cls.Predict(query)

    @staticmethod
    def GetAuthentication(email, password):
        """Retrieves a Google authentication token.
        """
        url = 'https://www.google.com/accounts/ClientLogin'
        post_data = urllib.urlencode([
                ('Email', email),
                ('Passwd', password),
                ('accountType', 'HOSTED_OR_GOOGLE'),
                ('source', 'companyName-applicationName-versionID'),
                ('service', 'xapi'),
                ])
        result = urllib.urlopen(url=url, data=post_data)
        content = result.read()
        logging.info('CONTENT=%s' % content)
        content = '&'.join(content.split())
        query = cgi.parse_qs(content)
        auth = query['Auth'][0]
        logging.info('Auth: ' + auth)
        return auth

    @classmethod
    def Predict(cls, query, auth=None, model=None):
        if auth is None:
            auth = cls.AUTH
        if model is None:
            model = cls.MODEL

        url = ('https://www.googleapis.com/prediction/v1.3/training/'
               '%s/predict' % urllib.quote(model, ''))
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'GoogleLogin auth=%s' % auth,
            }
        post_data = GooglePredictionApi.GetPostData(query)
        logging.info('Post Data: '+ str(post_data))
        result = urllib2.urlopen(urllib2.Request(url=url, data=post_data, headers=headers))
        content = result.read()
        logging.info('Content: ' + content)
        json_content = simplejson.loads(content)['data']

        scores = []
        print simplejson.loads(content)
        # classification task
        if 'outputLabel' in json_content:
            prediction = json_content['outputLabel']
            jsonscores = json_content['outputMulti']
            scores = GooglePredictionApi.ExtractDictScores(jsonscores)
        # regression task
        else:
            prediction = json_content['outputValue']

        return [prediction, scores]

    @staticmethod
    def ExtractDictScores(jsonscores):
        scores = {}
        for pair in jsonscores:
            for key, value in pair.iteritems():
                if key == 'label':
                    label = value
                elif key == 'score':
                    score = value
            scores[label] = score
        return scores

    @staticmethod
    def GetPostData(query):
        data_input = {}
        data_input['mixture'] = [query]

        post_data = simplejson.dumps({
                'data': {
                    'input': data_input
                    }
                })
        return post_data

class Locality(object):
    """Class representing a sub-locality."""
    
    @classmethod
    def create_muti(cls, location):
        """Return list of Locality objects by splitting location on ',' and ';'."""
        return [Locality(loc) for loc in set(reduce(            
                    lambda x,y: x+y, 
                    [x.split(';') for x in location.split(',')]))]

    def __init__(self, loc):
        self.loc = loc
        self.type = None
        self.parts = {}
        self.features = set()
    
    def __repr__(self):
        return str(self.__dict__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    conn = _setupdb()
    
    sql = 'select address,response from geocodes where address = ?'
    c = conn.cursor()
    cache = {}
    address = options.address
    
    

    for row in c.execute(sql, (address,)):
        cache[row[0]] = row[1]
    
    if cache.has_key(address):
        logging.info('CACHE HIT: address=%s' % address)
        sys.exit(1)
    
    logging.info('CACHE MISS: address=%s' % address)
    params = urllib.urlencode(dict(address=address, sensor='true'))
    url = 'http://maps.googleapis.com/maps/api/geocode/json?%s' % params
    response = simplejson.loads(urllib.urlopen(url).read())
    logging.info('Geocode received from %s' % url)
    sql = 'insert into geocodes values (?, ?)'
    cursor = conn.cursor()
    cursor.execute(sql, (address, simplejson.dumps(response)))
    conn.commit()
    
