#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import os
import unittest
import shutil
import tempfile

from shapely.geometry import LineString
from traits import has_traits

from hydropick.model.survey import Survey
from hydropick.io import survey_io

has_traits.CHECK_INTERFACES = 2


class TestSurvey(unittest.TestCase):
    """ Tests for the Survey class """

    def setUp(self):
        self.line_name = '12041701'
        here = os.path.dirname(__file__)
        top = os.path.dirname(os.path.dirname(here))
        self.binaryfile = os.path.join(top, 'io', 'tests', 'files',
                                       '{}.bin'.format(self.line_name))
        self.tempdir = tempfile.mkdtemp()
        self.h5file = os.path.join(self.tempdir, 'test.h5')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_empty_survey(self):
        Survey(name='Empty Survey')

    def test_read_from_hdf(self):
        survey_io.import_survey_line_from_file(self.binaryfile, self.h5file, self.line_name)
        line = survey_io.read_survey_line_from_hdf(self.h5file, self.line_name)
        self.assertEqual(line.name, self.line_name)
        self.assertIsInstance(line.navigation_line, LineString)
        line.load_data(self.h5file)
        self.assertEqual(line.frequencies.keys(), ['24.0385', '208.333', '50.0'])
        # TODO: more tests here

if __name__ == "__main__":
    unittest.main()
