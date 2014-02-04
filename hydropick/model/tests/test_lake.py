#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import os
import unittest

from shapely.geometry.base import BaseGeometry

from traits import has_traits

from hydropick.model.lake import Lake

has_traits.CHECK_INTERFACES = 2


class TestLake(unittest.TestCase):
    """ Tests for the Lake class """

    def setUp(self):
        self.test_dir = os.path.dirname(__file__)

    def test_read_shapefile(self):
        filename = os.path.join(self.test_dir, 'files', 'Granger_Lake1283.shp')
        name = 'Granger'
        lake = Lake(name=name, shoreline_file=filename)
        self.assertIsInstance(lake.shoreline, BaseGeometry)
        self.assertEqual(lake.elevation, 504.0)

if __name__ == "__main__":
    unittest.main()
