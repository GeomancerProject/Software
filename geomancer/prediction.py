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
import httplib2
import logging

# Google API modules
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
      
class PredictionApi(object):

    """Class for locality type prediction based on the Google Prediction API."""

    def __init__(self, model, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret        
        self.model = model
        self._set_flow()

    def get_type(self, query):
        storage = Storage('prediction.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            self._set_flow()
            credentials = run(self.FLOW, storage)
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build("prediction", "v1.3", http=http)
        try:
            train = service.training()
            body = {'input': {'csvInstance': [query]}}
            prediction = train.predict(body=body, data=self.model).execute()
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
            client_id=self.client_id,
            client_secret=self.client_secret,
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
