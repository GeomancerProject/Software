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

from util.bb import BoundingBox

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
        name = self.request.get('feature', None)
        category = self.request.get('type', None)
        source = self.request.get('source', None)
        limit = self.request.get_range('limit', min_value=1, max_value=100, default=10)
        offset = self.request.get_range('offset', min_value=0, default=0)
        
        if name:
            name = name.replace(',', '')
            logging.info('name=%s' % name)
            feature = Feature.get_by_name(name)
            if feature:
                self.response.headers["Content-Type"] = "application/json"
                self.response.out.write(feature.j)
                return
            else:
                keywords = self.tokenize(name.replace(',', ' ').split(), set())
                logging.info('keywords=%s' % str(keywords))
        
        features = FeatureIndex.search(
            limit, offset, keywords=keywords, category=category, source=source)

        bounding_boxes = []
        results = []
        for f in features:
            data = simplejson.loads(f.j)
            results.append(data)
            bounding_boxes.append(BoundingBox.create(
                    data['minx'], data['maxy'], data['maxx'], data['miny']))
            
        if not BoundingBox.intersect_all(bounding_boxes):
            results = []
        
        if len(keywords) > 0:
            result = dict(results=results, exact_match=False)
        else:
            result = results

        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps(result))
            

application = webapp.WSGIApplication(
    [('/gaz/api', ApiHandler),], debug=True)
         
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
