''' Unit tests for surveydatasession

'''
import os
import shutil
import tempfile
import unittest
import numpy as np

from hydropick.model.survey_line import SurveyLine
from traits.interface_checker import InterfaceError
from traits import has_traits

from hydropick.io import survey_io


class TestDepthLine(unittest.TestCase):
    ''' Test DepthLine Class'''

    def setUp(self):
        has_traits.CHECK_INTERFACES = 1
        self.test_dir = os.path.dirname(__file__)
        # filename = os.path.join(self.test_dir, 'files', '12030101.bin')
        # self.survey_line = SurveyLine(data_file_path=filename)
        # self.survey_line.load_data()
        linename = '12030101'
        filename = os.path.join(self.test_dir, 'files', linename + '.bin')
        self.tempdir = tempfile.mkdtemp()
        self.h5file = os.path.join(self.tempdir, 'test.h5')
        survey_io.import_survey_line_from_file(filename, self.h5file, linename)
        self.survey_line = survey_io.read_survey_line_from_hdf(self.h5file,
                                                               linename)
        self.survey_line.load_data(self.h5file)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_provides(self):
        ''' check that the algorithms provide the IDepthLine interface

        '''
        has_traits.CHECK_INTERFACES = 2
        try:
            from hydropick.model import depth_line
            # reload in case it was previously imported in different test
            reload(depth_line)
        except InterfaceError as err:
            self.assertTrue(False, msg='Interface Error: {}'.format(err))

    def test_existence(self):
        ''' check is instance of DepthLine'''
        try:
            from hydropick.model.depth_line import DepthLine
            lake_line = self.survey_line.lake_depths['depth_r1']
            self.assertIsInstance(lake_line, DepthLine)
        except Exception as err:
            self.assertTrue(False, msg='undefined: {}'.format(err))

    def test_distance_array(self):
        ''' check the process_line returns an array'''
        try:

            lake_line = self.survey_line.lake_depths['depth_r1']
            N = self.survey_line.trace_num.size
            print N, lake_line.depth_array.size
            dist_array = lake_line.distance_array(self.survey_line.trace_num)
            self.assertFalse(np.any(dist_array - self.survey_line.trace_num))
        except Exception as err:
            self.assertTrue(False, msg='distance array err: {}'.format(err))


if __name__ == "__main__":
    # from package use "python -m unittest discover -v -s ./tests/"
    unittest.main()
