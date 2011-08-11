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

class Feature(model.Model): # id=name
    j = model.TextProperty('j', required=True) # json

    @classmethod
    def create(cls, row):
        return Feature(id=row['name'], j=simplejson.dumps(row))

    @classmethod
    def key_from_name(cls, name):
        return model.Key(
            'Feature', 
            unicode('-'.join(name.replace(',', ' ').lower().split())))

    @classmethod
    def get_by_name(cls, name):
        return cls.key_from_name(name).get()

    @classmethod
    def get_by_name_multi(cls, names):
        return model.get_multi([cls.key_from_name(name) for name in names])

class FeatureIndex(model.Model): # parent=Feature, id=feature_name
    n = model.StringProperty('n', required=True) # name
    s = model.StringProperty('s', repeated=True) # source
    c = model.StringProperty('c', required=True) # category (type)
    k = model.StringProperty('k', repeated=True) # keywords

    @classmethod
    def key_from_name(cls, name):
        parent = Feature.key_from_name(name)
        return model.Key('FeatureIndex', parent.id(), parent=parent) 

    @classmethod
    def create(cls, row, keywords):
        parent = Feature.key_from_name(row['name'])
        return FeatureIndex(
            parent=parent,
            n=row['name'],
            s=row['source'],
            c=row['type'],
            k=keywords)

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
