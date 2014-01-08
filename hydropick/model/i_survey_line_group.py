#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from traits.api import Interface, Supports, List, Str
from .i_algorithm import IAlgorithm

class ISurveyLineGroup(Interface):
    """ An interface representing a group of survey lines """

    #: the user-defined name of the group
    name = Str

    #: the survey lines in the group
    survey_lines = List

    #: the lake depth algorithm to apply to the group
    lake_depth_algorithm = Supports(IAlgorithm)

    #: the preimpoundment depth algorithm to apply to the group
    preimpoundment_depth_algorithm = Supports(IAlgorithm)

    # XXX may want to add some analysis data here that is applied to the lines
    # in this group (eg. contrast settings, data view, etc.) so users can have
    # consistent settings for viewing a collection of lines
