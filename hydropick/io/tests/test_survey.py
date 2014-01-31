#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import os
import shutil
import tempfile
import unittest

from shapely.geometry import LineString

from hydropick.io.survey import (read_survey_line_from_file,
                                 read_survey_line_from_hdf,
                                 write_survey_line_to_hdf)

class TestSurveyIO(unittest.TestCase):
    """ Tests for the survey line I/O """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.h5file = os.path.join(self.tempdir, 'test.h5')
        self.line_name = '12041701'
        self.binaryfile = os.path.join(os.path.dirname(__file__), 
                                       'files', 
                                       '{}.bin'.format(self.line_name))

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_read_from_file(self):
        line = read_survey_line_from_file(self.binaryfile, self.line_name)
        self.assertEqual(line.name, self.line_name)
        self.assertIsInstance(line.navigation_line, LineString)

    def test_hdf(self):
        line = read_survey_line_from_file(self.binaryfile, self.line_name)
        write_survey_line_to_hdf(self.h5file, line)
        h5line = read_survey_line_from_hdf(self.h5file, self.line_name)
        self.assertEqual(h5line.name, self.line_name)
        self.assertIsInstance(h5line.navigation_line, LineString)
        self.assert_(line.navigation_line.equals(h5line.navigation_line))
