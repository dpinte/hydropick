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

if __name__ == "__main__":
    unittest.main()
