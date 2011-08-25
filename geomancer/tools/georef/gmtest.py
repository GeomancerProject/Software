#!/usr/bin/env python

import setup_env
setup_env.fix_sys_path()

import unittest
import logging

import gm
#from gm import Locality, PredictionApi

class TestLocality(unittest.TestCase):
    
    def test_create_multi(self):
        locs = gm.Locality.create_muti('5 miles west of berkeley, california')
        self.assertEqual(2, len(locs))
        logging.info(locs)

        locs = gm.Locality.create_muti('5 miles west of berkeley, california;usa')
        self.assertEqual(3, len(locs))
        logging.info(locs)

class TestPredictionApi(unittest.TestCase):
    def test_predict(self):
        logging.info(gm.PredictionApi.predict('5 miles west of berkeley'))
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
