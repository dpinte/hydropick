#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import os
import logging

logger = logging.getLogger(__name__)

# XXX this is not fully implemented

def import_cores(directory):
    from sdi import corestick
    from ..model.core_sample import CoreSample

    cores = []
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1] == '.txt':
            # this is a corestick file
            logger.info("Reading corestick file '%s'", filename)
            for core_id, core in corestick.read(os.path.join(directory, filename)).items():
                core_sample = CoreSample(
                    core_id=core_id,
                    location=(core['easting'], core['northing']),
                    layer_boundaries=core['layer_interface_depths'],
                )
                cores.append(core_sample)
    return cores


def import_lake(directory):
    # XXX this needs a proper implementation
    from ..model.lake import Lake
    return Lake()
    pass


def import_sdi(directory):
    survey_lines = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if os.path.splitext(filename) == '.bin':
                # XXX read in the file with sdi and create a SurveyLine object
                logger.info("Reading sdi file '%s'", filename)
                pass
    return survey_lines


def import_survey(directory):
    """ Read in a project from the current directory-based format """
    from ..model.survey import Survey
    # read in core samples
    core_samples = import_cores(os.path.join(directory, 'Coring'))

    # read in lake
    lake = import_lake(os.path.join(directory, 'ForSurvey'))

    # read in sdi data
    survey_lines = []

    # read in edits to sdi data
    # XXX not implemented

    survey = Survey(
        #lake=lake,
        survey_lines=survey_lines,
        core_samples=core_samples,
    )

    return survey
