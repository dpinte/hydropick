#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import unittest
from traits import has_traits
from hydropick.model.survey import Survey


has_traits.CHECK_INTERFACES = 2

class TestSurvey(unittest.TestCase):
    """ Tests for the Survey class """

    def test_empty_survey(self):
        Survey(name='Empty Survey')

if __name__ == "__main__":
    unittest.main()
