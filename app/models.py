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

def tokenize(seq, uniques=set()):
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
        tokenize(tmp, uniques)
    return uniques

class Feature(model.Model): # id=name
    j = model.TextProperty('j', required=True) # json

    def __str__(self):
        return str(self.key)

    @classmethod
    def search(cls, place): # place = "indian rock, berkeley"
        names = [x.strip().lower() for x in place.split(',')]
        keys = [cls.key_from_name(name) for name in names]
        return [feature for feature in model.get_multi(keys) if feature]

    @classmethod
    def create(cls, row):
        return Feature(id=row['name'], j=simplejson.dumps(row))

    @classmethod
    def key_from_name(cls, name):
        return model.Key(
            'Feature', 
            unicode('-'.join(name.lower().split())))

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
    def search_place_keywords(cls, place, limit=10, offset=0):
        names = [name.strip().lower() for name in place.split(',')]
        results = {}
        for name in names:
            qry = cls.query()
            for token in tokenize(name.split()):
                qry = qry.filter(cls.k == token)
            results[name] = model.get_multi(
                [key.parent() \
                     for key in qry.fetch(limit, offset=offset, keys_only=True)])
        return results        
    
    @classmethod
    def search(cls, limit=0, offset=10, name=None, keywords=[], category=None, source=None):
        if len(keywords) == 0 and not category and not source and not name:
            return FeatureIndex.query().fetch(limit, offset=offset)
        qry = FeatureIndex.query()
        for keyword in keywords:
            qry = qry.filter(FeatureIndex.k == keyword)   
        if category:
            qry = qry.filter(FeatureIndex.c == category)
        if source:
            qry = qry.filter(FeatureIndex.s == source)
        logging.info('QUERY='+str(qry))
        return model.get_multi([x.parent() for x in qry.fetch(limit, offset=offset, keys_only=True)])
