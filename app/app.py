#!/usr/bin/env python
#
# Copyright 2011 Aaron Steele
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
from ndb import query

from geomancer.gm.bb import BoundingBox

from models import Feature, FeatureIndex
try:
    appid = os.environ['APPLICATION_ID']
    appver = os.environ['CURRENT_VERSION_ID'].split('.')[0]
except:
    pass


# ------------------------------------------------------------------------------
# Handlers

class BaseHandler(webapp.RequestHandler):
    """Base handler for handling common stuff like template rendering."""
    def render_template(self, file, template_args):
        path = os.path.join(os.path.dirname(__file__), "templates", file)
        self.response.out.write(template.render(path, template_args))
    def push_html(self, file):
        path = os.path.join(os.path.dirname(__file__), "html", file)
        self.response.out.write(open(path, 'r').read())

class ApiHandler(BaseHandler):

    def tokenize(self, seq, uniques=set()):
        n = len(seq)
        if n == 0:
            return
        if n == 1:
            uniques.add(seq[0].lower())
            return uniques
        uniques.add(reduce(lambda x,y: '%s %s' % (x.lower(), y.lower()), seq))
        for i in range(n):
            tmp = list(seq)
            tmp.pop(i)
            self.tokenize(tmp, uniques)
        return uniques

    def get(self):
        keywords = []
        place = self.request.get('place', None)
        category = self.request.get('type', None)
        source = self.request.get('source', None)
        limit = self.request.get_range('limit', min_value=1, max_value=100, default=10)
        offset = self.request.get_range('offset', min_value=0, default=0)
        
        if place:
            # Search Feature on id where id is each name in palce (names comma separated)
            features = Feature.search(place)
            logging.info('FEATURES=%s' % [f.key for f in features])
            n = len(features)
            results = []
            if n == 1: # Exact match on one Feature
                results.append(simplejson.loads(features[0].j))
            elif n > 1: # Exact match on multiple Features
                bboxes = []
                for feature in features:
                    data = simplejson.loads(feature.j)
                    bboxes.append(
                        BoundingBox.create(
                            data['minx'], 
                            data['maxy'], 
                            data['maxx'], 
                            data['miny']))                    
                if BoundingBox.intersect_all(bboxes): # Return all features with intersection=True
                    results = dict(
                        features=[simplejson.loads(feature.j) for feature in features],
                        intersection=True)
                else: # Return all features with intersection=False
                    results = dict(
                        features=[simplejson.loads(feature.j) for feature in features],
                        intersection=False)
            if len(results) > 0: # If exact results return them
                self.response.headers["Content-Type"] = "application/json"
                self.response.out.write(simplejson.dumps(results))
                return
        
        # Search FeatureIndex on keywords derived from each place name
        if place:
            results = set()
            search_results = FeatureIndex.search_place_keywords(place)
            if len(search_results) == 1: # Keyword FeatureIndex hit on single name
                name, features = search_results.popitem()
                results = [simplejson.loads(feature.j) for feature in features]                
                self.response.headers["Content-Type"] = "application/json"
                self.response.out.write(simplejson.dumps(results))
                return
            # Perform cross-product intersection tests and return all matching pairs
            for name,features in search_results.iteritems():
                for feature in features:                    
                    for other_name, other_features in search_results.iteritems():
                        if name == other_name:
                            continue                        
                        data = simplejson.loads(feature.j)
                        fbbox = BoundingBox.create(data['minx'], data['maxy'], data['maxx'], data['miny'])
                        for other_feature in other_features:
                            data = simplejson.loads(other_feature.j)
                            obbox = BoundingBox.create(data['minx'], data['maxy'], data['maxx'], data['miny'])                           
                            logging.info('feature=%s, other_feature=%s, fbbox=%s, obbox=%s' % (feature, other_feature, fbbox, obbox))
                            if BoundingBox.intersect_all([fbbox, obbox]):
                                results.update([feature, other_feature])
            self.response.headers["Content-Type"] = "application/json"
            self.response.out.write(simplejson.dumps(list(results)))

application = webapp.WSGIApplication(
    [('/gaz/api', ApiHandler),], debug=True)
         
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
