#!/usr/bin/env python
#
# Copyright 2011 The Regents of the University of California and Aaron Steele
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = 'Aaron Steele'

# Standard Python imports
import csv
import logging
import os
import simplejson

# Google App Engine imports
from google.appengine.ext import deferred
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.util import login_required
from google.appengine.datastore import datastore_rpc
from google.appengine.datastore import entity_pb

# Datastore Plus imports
from ndb import query, model

try:
    appid = os.environ['APPLICATION_ID']
    appver = os.environ['CURRENT_VERSION_ID'].split('.')[0]
except:
    pass

class Locality(model.Model): # id=locname
    loctype = model.StringProperty('t')
    json = model.StringProperty('j', indexed=False)
    created = model.DateTimeProperty('c', auto_now_add=True)

    @classmethod
    def get_key(cls, locname):
        return model.Key('Locality', locname)

    @classmethod
    def get_loctype(cls, locname):
        return cls.get_key(locname).get()

    @classmethod
    def put_loctype(cls, locname, loctype, json):
        cls(key=cls.get_key(locname), loctype=loctype, json=json).put()

class GetLoctype(webapp.RequestHandler):

    def get(self):
        self.post()

    def post(self):
        # TODO: required login?
        locname = self.request.get('locname', None)
        if not locname:
            logging.error('No locname parameter')
            return
        loc = Locality.get_loctype(locname)
        if not loc:
            logging.error('Locality for locname=%s not found' % locname)
            return
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(loc.json)

class PutLoctype(webapp.RequestHandler):

    def post(self):
        # TODO: require login?
        locname = self.request.get('locname', None)
        loctype = self.request.get('loctype', None)
        json = self.request.get('json', None)
        if not locname or not loctype or not json:
            logging.error('Missing required fields')
            return
        Locality.put_loctype(locname, loctype, json)
            
application = webapp.WSGIApplication(
    [('/cache/get_loctype', GetLoctype),
     ('/cache/put_loctype', PutLoctype),], debug=True)
         
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
