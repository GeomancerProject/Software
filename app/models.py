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
import logging
import simplejson

# Datastore Plus imports
from ndb import model
from ndb import query

# Get app info
try:
    appid = os.environ['APPLICATION_ID']
    appver = os.environ['CURRENT_VERSION_ID'].split('.')[0]
except:
    pass

class Feature(model.Model): 
    """Feature model."""
    name = model.StringProperty('n', required=True)
    j = model.TextProperty('j', required=True)
    @classmethod
    def create(cls, row):
        """Creates Feature from name, category, point, bounding box."""
        return Feature(
            id=fid,
            name=name,
            category=category,
            json=simplejson.dumps(row))

class FeatureIndex(model.Model): # parent=Feature
    """FetureIndex model for searching Feature entities."""
    k = model.StringProperty('k', repeated=True) # keywords
    s = model.StringProperty('s', repeated=True) # source
    c = model.StringProperty('c', required=True) # category (type)

    @classmethod
    def create(cls, fid, keywords):
        key = model.Key('FeatureIndex', parent=model.Key('Feature', fid))                        
        return FeatureIndex(key=key, keywords=keywords)

    @classmethod
    def search(cls, limit, offset, keywords=[], category=None, source=None):
        if len(keywords) == 0 and not category and not source:
            return []
        qry = FeatureIndex.query()
        for keyword in keywords:
            qry = qry.filter(FeatureIndex.k == keyword)   
        if category:
            qry = qry.filter(FeatureIndex.c == category)
        if source:
            qry = qry.filter(FeatureIndex.s == source)
        logging.info('QUERY='+str(qry))
        return model.get_multi([x.parent() for x in qry.fetch(limit, offset=offset, keys_only=True)])
