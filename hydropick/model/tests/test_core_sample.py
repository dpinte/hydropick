#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import unittest
from traits import has_traits
from hydropick.model.core_sample import CoreSample


has_traits.CHECK_INTERFACES = 2

class TestCoreSample(unittest.TestCase):
    """ Tests for the CoreSample class

    Currently only verifies that a new instance can be created, and
    that it follows the ICoreSample interface.
    """
    # TODO: fill out with actual tests
    
    def test_empty_core_sample(self):
        CoreSample(name='Empty Core Sample')

if __name__ == "__main__":
    unittest.main()
