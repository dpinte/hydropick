#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import logging

from traits.api import File, HasTraits, List, Str, Supports, provides

from .i_survey import ISurvey
from .i_lake import ILake
from .i_survey_line import ISurveyLine
from .i_survey_line_group import ISurveyLineGroup
from .i_core_sample import ICoreSample

logger = logging.getLogger(__name__)

@provides(ISurvey)
class Survey(HasTraits):
    """ The a basic implementation of the ISurvey interface

    A survey has a lake, a set of survey lines, and a collection of
    user-assigned line groups.

    """
    # XXX there should probably be some other survey metadata saved in this object

    #: The name of the survey
    name = Str

    #: Notes about the survey as a whole
    comments = Str

    #: The lake being surveyed
    lake = Supports(ILake)

    #: The lines in the survey
    survey_lines = List(Supports(ISurveyLine))

    #: The groupings of survey lines
    survey_line_groups = List(Supports(ISurveyLineGroup))

    #: The core samples taken in the survey
    core_samples = List(Supports(ICoreSample))
    
    #: backend hdf5 file
    hdf5_file = File

    def add_survey_line_group(self, group):
        """ Create a new line group, optionally with a set of lines """
        self.survey_line_groups.append(group)
        logger.debug("Added survey line group '{}'".format(group.name))

    def insert_survey_line_group(self, index, group):
        """ Create a new line group, optionally with a set of lines """
        self.survey_line_groups.insert(index, group)
        logger.debug("Inserted survey line group '{}' at index {}".format(
            group.name, index))

    def delete_survey_line_group(self, group):
        """ Delete a line group, returning its index """
        index = self.survey_line_groups.index(group)
        self.survey_line_groups.remove(group)
        logger.debug("Removed survey line group '{}' from index {}".format(
            group.name, index))
        return index
