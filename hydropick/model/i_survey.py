#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from traits.api import Interface, Instance, List, Set

from .i_lake import ILake

class ISurvey(Interface):
    """ The abstract interface for a survey object.

    A survey has a lake, a set of survey lines, and a collection of
    user-assigned line groups.

    """
    # XXX there should probably be some other survey metadata saved in this object

    #: The lake being surveyed
    lake = Instance(ILake)

    #: The lines in the survey
    survey_lines = List

    #: The groupings of survey lines
    line_groups = Set

    #: The core samples taken in the survey
    core_samples = List


    def new_line_group(self, group, lines=None):
        """ Create a new line group, optionally with a set of lines """
        raise NotImplementedError

    def add_lines_to_group(self, group, lines):
        """ Add a set of lines to a group """
        raise NotImplementedError

    def remove_lines_from_group(self, group, lines):
        """ Add a set of lines to a group """
        raise NotImplementedError
