'''
Script to test surveyline-view editor ui.

Creates surveyline object using an sdi bin file and the current sdi reader.
It then creates a datasession object with this and a surveyline_view object
with the datasession, finally bringing up that ui.

'''


import sys
import os
import numpy as np

from sdi import binary

# must use absolute import to run script directly
from hydropick.model.survey_line import SurveyLine
from hydropick.ui.surveydatasession import SurveyDataSession
from hydropick.ui.surveyline_view import SurveyLineView


# choose a sample file
# Update these path constants appropriately for users data directory

REL_PATH = '../../..'
REL_PATH = '/Users/bklappauf/mySoftware/projects/EnthoughtProjects/TWDB/code/'
FILE_DIR = 'DataForEnthought/CorpusChristi/2012/SurveyData/SDI_data/030112a'
FILE_NAME = '12030101.bin'

LOCAL_DATA_PATH = os.path.join(REL_PATH, FILE_DIR, FILE_NAME)

ATTR_LIST = ['intensity', 'num_pnts', 'pixel_resolution', 'depth_r1',
             'draft', 'heave','units','latitude','longitude',
             'interpolated_northing', 'interpolated_easting']

def create_surveyline():
    ''' Create survey line for testing views
    Fill just whichever attributes are needed for editing pane.
    '''

    print 'getting sdi data from :\n', LOCAL_DATA_PATH
    sdi_dict = binary.read(LOCAL_DATA_PATH)
    surveyline = SurveyLine()
    freq_dict_list = sdi_dict['frequencies']
    freq_dict = {}
    for d in freq_dict_list:
        # replace list with dict with freq ('kHz' value) as keys
        freq_dict[d['kHz']]=d

    # dict traits that need to be coded by freq
    surveyline.frequencies = {}
    surveyline.lake_depths = {}
    for key in freq_dict:
        d = freq_dict[key]
        # add desired info
        for k in ATTR_LIST:
            setattr(surveyline, k, d[k])
        # modify certain attributes: frequencies,lake_depths,pixel_resolution numpts
        surveyline.frequencies[str(key)] = surveyline.intensity.T
        surveyline.lake_depths['Lakedepth_{:.1f}'.format(key)] = surveyline.depth_r1
        surveyline.locations = np.vstack([surveyline.latitude, surveyline.longitude]).T
        surveyline.core_samples = []
        surveyline.preimpoundment_depths = {}
        surveyline.pixel_resolution = np.mean(surveyline.pixel_resolution)
        surveyline.num_depth_pnts = np.argmax(np.bincount(surveyline.num_pnts))
        surveyline.num_dist_pnts = surveyline.intensity.shape[0]
    return surveyline


if __name__ == '__main__':

    surveyline = create_surveyline()

    datasession = SurveyDataSession()
    datasession.surveyline = surveyline
    surveylineview = SurveyLineView(model=datasession)
    surveylineview.configure_traits()
