#!/usr/bin/env python

import setup_env
setup_env.fix_sys_path()

import cache
from cache import Cache

import unittest
import logging
import os
import simplejson
import yaml
import utils

import gm

class TestLocality(unittest.TestCase):
    
    def test_create_multi(self):
        locs = gm.Locality.create_muti('5 miles west of berkeley, california')
        self.assertEqual(2, len(locs))
        locs = gm.Locality.create_muti('5 miles west of berkeley, california;usa')
        self.assertEqual(3, len(locs))

class TestGeomancer(unittest.TestCase):
    # def test_predict(self):
    #     cache = gm.Cache('gmtest.cache.sqlite3.db')
    #     config = yaml.load(open('gm.yaml', 'r'))        
    #     predictor = gm.PredictionApi(config, cache)
    #     geomancer = gm.Geomancer(cache, predictor)
    #     results = geomancer.georeferece('5 miles west of berkeley, califorina, usa')
    #     logging.info(results)

#    def test_remote_cache(self):
#        remote = gm.RemoteCache('localhost:8080', 'foo', 'bar')
#        remote.put_loctype('berkeley', 'f', simplejson.dumps(dict(loctype='f', locname='berkley')))
#        loctype = remote.get_loctype('berkeley')
#        logging.info(loctype)

    #def test_auth(self):
        #logging.info(utils.CredentialsPrompt('localhost:8080'))
    pass
    
class TestCache(unittest.TestCase):
    def test_cache(self):
        Cache.config(local_filename='gmtest.db')
        key = u'aaron'
        value = dict(value='amazing')        
        Cache.put(key, value)
        self.assertEqual(value, Cache.get(key))
        self.assertEqual(None, Cache.get('foo'))
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
