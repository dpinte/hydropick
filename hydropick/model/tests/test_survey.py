#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import os
import unittest
from shapely.geometry import LineString

from traits import has_traits

from hydropick.model.survey import Survey
from hydropick.io.survey_io import read_survey_line_from_file

has_traits.CHECK_INTERFACES = 2


class TestSurvey(unittest.TestCase):
    """ Tests for the Survey class """

    def setUp(self):
        self.line_name = '12041701'
        here = os.path.dirname(__file__)
        top = os.path.dirname(os.path.dirname(here))
        self.binaryfile = os.path.join(top, 'io', 'tests', 'files', 
                                       '{}.bin'.format(self.line_name))

    def test_empty_survey(self):
        Survey(name='Empty Survey')

    def test_read_from_file(self):
        line = read_survey_line_from_file(self.binaryfile, self.line_name)
        self.assertEqual(line.name, self.line_name)
        self.assertIsInstance(line.navigation_line, LineString)
        line.load_data()
        self.assertEqual(line.frequencies.keys(), ['24.0385', '208.333', '50.0'])
        # TODO: more tests here

if __name__ == "__main__":
    unittest.main()
