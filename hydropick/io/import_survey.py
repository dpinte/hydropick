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

    # find the GIS file in the directory
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1] == '.shp':
            return Lake(shoreline_file=os.path.join(directory, filename))
    pass


def import_sdi(directory):
    from sdi import binary
    from ..model.survey_line import SurveyLine
    from ..model.survey_line_group import SurveyLineGroup

    survey_lines = []
    survey_line_groups = []
    for root, dirs, files in os.walk(directory):
        group_lines = []
        for filename in files:
            if os.path.splitext(filename)[1] == '.bin':
                # XXX read in the file with sdi and create a SurveyLine object
                logger.info("Reading sdi file '%s'", filename)
                #data = binary.read(os.path.join(root, filename))
                line = SurveyLine(
                    name=os.path.splitext(filename)[0],
                    #frequencies=data['frequencies'],
                )
                group_lines.append(line)
        if group_lines:
            dirname = os.path.basename(root)
            group = SurveyLineGroup(name=dirname, survey_lines=group_lines)
            survey_lines += group_lines
            survey_line_groups.append(group)
    return survey_lines, survey_line_groups


def import_survey(directory):
    """ Read in a project from the current directory-based format """
    from ..model.survey import Survey
    # read in core samples
    core_samples = import_cores(os.path.join(directory, 'Coring'))

    # read in lake
    lake = import_lake(os.path.join(directory, 'ForSurvey'))

    # read in sdi data
    survey_lines, survey_line_groups = import_sdi(os.path.join(directory, 'SDI_Data'))

    # read in edits to sdi data
    # XXX not implemented

    survey = Survey(
        lake=lake,
        survey_lines=survey_lines,
        survey_line_groups=survey_line_groups,
        core_samples=core_samples,
    )

    return survey
