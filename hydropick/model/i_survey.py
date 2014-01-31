#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Interface, Supports, List, Str

from .i_lake import ILake
from .i_survey_line import ISurveyLine
from .i_survey_line_group import ISurveyLineGroup
from .i_core_sample import ICoreSample

class ISurvey(Interface):
    """ The abstract interface for a survey object.

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


    def add_survey_line_group(self, group):
        """ Create a new line group, optionally with a set of lines """
        raise NotImplementedError

    def insert_survey_line_group(self, index, group):
        """ Create a new line group, optionally with a set of lines """
        raise NotImplementedError

    def delete_survey_line_group(self, group):
        """ Delete a line group, returning its index """
        raise NotImplementedError
