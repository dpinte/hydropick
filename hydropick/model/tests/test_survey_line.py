#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import unittest
from traits import has_traits
from hydropick.model.survey_line import SurveyLine


has_traits.CHECK_INTERFACES = 2

class TestSurveyLine(unittest.TestCase):
    """ Tests for the SurveyLine class """
    # TODO: fill out with actual tests
    
    def test_empty_survey_line(self):
        SurveyLine(name='Empty Survey Line')

if __name__ == "__main__":
    unittest.main()
