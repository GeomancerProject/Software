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
    def get(self):
        keywords = [x.lower() for x in self.request.get('q', '').split(',') if x]
        logging.info('keywords=%s' % str(keywords))
        category = self.request.get('type', None)
        source = self.request.get('source', None)
        limit = self.request.get_range('limit', min_value=1, max_value=100, default=10)
        offset = self.request.get_range('offset', min_value=0, default=0)
        features = FeatureIndex.search(
            limit, offset, keywords=keywords, category=category, source=source)
        bounding_boxes = []`
        for f in features:
            data = simplejson.loads(f.json)
            bounding_boxes.append(BoundingBox(data.minx, data.maxy, data.maxx, data.miny))

        logging.info(str(results))
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(
            simplejson.dumps([simplejson.loads(x.j) for x in results]))        

application = webapp.WSGIApplication(
    [('/gaz/api', ApiHandler),], debug=True)
         
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
