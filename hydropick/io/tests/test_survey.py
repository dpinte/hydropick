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

from shapely.geometry.base import BaseGeometry
from shapely.geometry import LineString

from hydropick.io import survey_io


class TestSurveyIO(unittest.TestCase):
    """ Tests for the survey line I/O """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.h5file = os.path.join(self.tempdir, 'test.h5')
        self.line_name = '12041701'
        files_dir = os.path.join(os.path.dirname(__file__), 'files')
        self.binary_file = os.path.join(
            files_dir, '{}.bin'.format(self.line_name))
        self.corestick_file = os.path.join(files_dir, 'Granger_CoreStick.txt')
        self.shoreline_file = os.path.join(files_dir, 'Granger_Lake1283.shp')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_import_and_read_from_binary(self):
        survey_io.import_survey_line_from_file(self.binary_file, self.h5file, self.line_name)
        line = survey_io.read_survey_line_from_hdf(self.h5file, self.line_name)
        line.load_data(self.h5file)
        self.assertEqual(line.name, self.line_name)
        self.assertIsInstance(line.navigation_line, LineString)

    def test_import_and_read_from_corestick(self):
        survey_io.import_core_samples_from_file(self.corestick_file, self.h5file)
        core_samples = survey_io.read_core_samples_from_hdf(self.h5file)
        self.assertIsInstance(core_samples, dict)
        self.assertEqual(len(core_samples), 6)

    def test_import_and_read_shoreline(self):
        lake_name = 'Granger'

        survey_io.import_shoreline_from_file(lake_name, self.shoreline_file, self.h5file)
        lake = survey_io.read_shoreline_from_hdf(self.h5file)

        self.assertIsInstance(lake.shoreline, BaseGeometry)
        self.assertEqual(len(lake.shoreline), 35)
        self.assertEqual(lake.elevation, 504.0)
        self.assertEqual(lake.name, lake_name)
