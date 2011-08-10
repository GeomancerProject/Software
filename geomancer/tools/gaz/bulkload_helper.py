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

"""This module contains transformation functions for the bulkloader."""

import test_util
test_util.fix_sys_path()

import logging

from django.utils import simplejson
from google.appengine.api import datastore
from google.appengine.ext.bulkload import transform
from google.appengine.ext.db import Expando

from ndb import model
from ndb import query


def get_feature_json():
    def wrapper(value, bulkload_state):        
        d = bulkload_state.current_dictionary
        feature = dict()
        for key,val in d.iteritems():
            if key == '__record_number__':
                continue
            if key in ['name', 'type', 'source']:
                feature[key] = val
            elif key in ['id', 'accuracy', 'radius', 'nameid']:
                feature[key] = int(val)
            else:
                feature[key] = float(val)
        return simplejson.dumps(feature)        
    return wrapper

def create_feature_index_key():
    def wrapper(value, bulkload_state): 
        return transform.create_deep_key(
            ('Feature', 'id'),
            ('FeatureIndex', 'id'))(value, bulkload_state)
    return wrapper

def tokenize(input, uniques=set()):
    n = len(input)
    if n == 0:
        return
    if n == 1:
        uniques.add(input[0].lower())
        return uniques
    uniques.add(reduce(lambda x,y: '%s %s' % (x.lower(), y.lower()), input))
    for i in range(n):
        tmp = list(input)
        tmp.pop(i)
        tokenize(tmp, uniques)
    return uniques

def get_keywords():
    def wrapper(value, bulkload_state):
        return list(tokenize([x for x in value.split()], set()))
    return wrapper
        
