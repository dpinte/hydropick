''' Unit tests for surveydatasession

'''
import os
import unittest
import numpy as np

from surveydatasession import SurveyDataSession
from survey_line_sample_case import MySurveyLine

class SurveyDataSessionTestCase(unittest.TestCase):

    def setUp(self):
        self.source = SurveyDataSession()

    def check_types(self):
        # check return values for traits
        s = self.source
        self.assertTrue(isinstance(s.locations, np.ndarray))
        self.assertTrue(isinstance(s.lake_depths, dict))
        self.assertTrue(isinstance(s.frequencies, dict))
        self.assertTrue(isinstance(s.preimpoundment_depths, dict))
        self.assertTrue(isinstance(s.target_choices, list))
        self.assertTrue(isinstance(s.selected_target, str))
        self.assertTrue(isinstance(s.selected_freq, str))
        print 'shape is '
        for v in s.frequencies.values():
            print v.shape


    def test_default_values(self):
        # check trait types on new objet
        self.check_types()

    def test_change_survey(self):
        old_locations = self.source.locations
        newsurvey = MySurveyLine()
        newsurvey.locations = newsurvey.locations * 2
        self.source.surveyline = newsurvey
        self.assertAlmostEqual(old_locations[0,0]*2,self.source.locations[0,0])
        self.check_types()

if __name__ == "__main__":
    # from package use "python -m unittest discover -v -s ./tests/"
    unittest.main()
