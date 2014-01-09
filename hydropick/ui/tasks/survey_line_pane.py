#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Supports
from traitsui.api import View
from pyface.tasks.api import TraitsTaskPane

from ...model.i_survey_line import ISurveyLine

class SurveyLinePane(TraitsTaskPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_line'
    name = "Survey Line"

    survey_line = Supports(ISurveyLine)

    view = View()
