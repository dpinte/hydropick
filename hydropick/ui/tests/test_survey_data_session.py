''' Unit tests for surveydatasession

'''
import os
import shutil
import tempfile
import unittest

from traits import has_traits

from hydropick.ui.survey_data_session import SurveyDataSession
from hydropick.io.import_survey import import_sdi, import_cores


class TestSurveyDataSession(unittest.TestCase):
    def setUp(self):
        has_traits.CHECK_INTERFACES = 1

        data_dir = 'SurveyData'
        survey_name = '12030221'
        self.tempdir = tempfile.mkdtemp()
        self.h5file = os.path.join(self.tempdir, 'test.h5')

        test_dir = os.path.dirname(__file__)
        data_path = os.path.join(test_dir, data_dir)
        lines, groups = import_sdi(data_path, self.h5file)
        self.core_samples = import_cores(os.path.join(data_path, 'Coring'), self.h5file)
        for line in lines:
            if line.name == survey_name:
                self.survey_line = line
                self.survey_line.core_samples = self.core_samples

        ##self.survey_line = SurveyLine(data_file_path=file_path)
        self.survey_line.load_data(self.h5file)
        self.data_session = SurveyDataSession(survey_line=self.survey_line)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_get_freq_choices(self):
        ''' check that this returns a sorted by float value list of strings.
            Or string list sorted by string value
        '''
        frequencies = self.data_session.frequencies.keys()
        frequencies = sorted(frequencies, key=lambda f: float(f))
        freq_choices = self.data_session.freq_choices
        # check returns list instance
        self.assertIsInstance(freq_choices, list, msg="does't return instance")
        # check list contains strings
        for s in freq_choices:
            self.assertIsInstance(s, str, msg="does't return strings")
        # check sorts correctly by freq numerical value
        self.assertEqual(frequencies, freq_choices, msg="can't sort by value")
        # check that if keys cannot be converted it returns sorted keys
        # create key errors
        for k in self.survey_line.frequencies.copy():
            v = self.survey_line.frequencies.pop(k)
            self.survey_line.frequencies[k + 'a'] = v

        frequencies = self.data_session.frequencies.keys()
        frequencies.sort()
        # get freq choices and check
        freq_choices = self.data_session.freq_choices
        self.assertEqual(frequencies, freq_choices)

    def test_get_nearest_point_to_core(self):
        ''' check that given a line and '''
        sds = self.data_session
        two_checked = False
        #check that we have at least one core sample
        self.assertTrue(len(sds.core_samples) > 0, msg='no core samples to test')
        for core in self.core_samples:
            # check returns correct types for all cores
            loc_index, loc, dist_fm_line = sds.get_nearest_point_to_core(core)
            self.assertIsInstance(loc_index, int)
            self.assertIsInstance(loc, float)
            self.assertIsInstance(dist_fm_line, float)
            # check values right for #2
            if core.core_id == '2':
                self.assertEqual(loc_index, 3234)
                self.assertAlmostEqual(loc, 3179.05763018)
                self.assertAlmostEqual(dist_fm_line, 1.1930846536)
                two_checked = True
        self.assertTrue(two_checked)


if __name__ == "__main__":
    # from package use "python -m unittest discover -v -s ./tests/"
    unittest.main()
