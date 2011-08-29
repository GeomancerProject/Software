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
from ndb import model

try:
    appid = os.environ['APPLICATION_ID']
    appver = os.environ['CURRENT_VERSION_ID'].split('.')[0]
except:
    pass

class CacheEntry(model.Model): # id=key
    value = model.StringProperty('v', indexed=False)
    created = model.DateTimeProperty('c', auto_now_add=True)

    @classmethod
    def get_key(cls, keyname):
        return model.Key('CacheEntry', keyname)

    @classmethod
    def getit(cls, keyname):
        return cls.get_key(keyname).get()

    @classmethod
    def putit(cls, keyname, value):
        cls(key=cls.get_key(keyname), value=value).put()

class GetHandler(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        # TODO: required login
        key = self.request.get('key', None)
        if not key:
            logging.error('Missing key parameter')
            return
        entry = CacheEntry.getit(key)        
        if not entry:
            logging.info('No CacheEntry found for key=%s' % key)
            return
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(entry.value)
        
class PutHandler(webapp.RequestHandler):
    def post(self):
        # TODO: require login
        key = self.request.get('key', None)
        value = self.request.get('value', None)
        if not key and not value:
            logging.error('The key and value parameters are both required')
            return
        logging.info('Putting %s=%s' % (key, value))
        CacheEntry.putit(key, value)
            
application = webapp.WSGIApplication(
    [('/cache/get', GetHandler),
     ('/cache/put', PutHandler),], debug=True)
         
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
