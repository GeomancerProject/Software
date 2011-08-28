#!/usr/bin/env python

import setup_env
setup_env.fix_sys_path()

import unittest
import logging
import yaml

import gm

class TestLocality(unittest.TestCase):
    
    def test_create_multi(self):
        locs = gm.Locality.create_muti('5 miles west of berkeley, california')
        self.assertEqual(2, len(locs))
        locs = gm.Locality.create_muti('5 miles west of berkeley, california;usa')
        self.assertEqual(3, len(locs))

class TestGeomancer(unittest.TestCase):
    def test_predict(self):
        cache = gm.Cache('gmtest.cache.sqlite3.db')
        config = yaml.load(open('gm.yaml', 'r'))        
        predictor = gm.PredictionApi(config, cache)
        geomancer = gm.Geomancer(cache, predictor)
        results = geomancer.georeferece('5 miles west of berkeley, califorina, usa')
        logging.info(results)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
