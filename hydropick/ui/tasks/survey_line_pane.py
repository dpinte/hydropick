#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Instance, Property
from traitsui.api import View, Item
from pyface.tasks.api import TraitsTaskPane

from ...model.i_survey_line import ISurveyLine
from ..surveydatasession import SurveyDataSession
from ..surveyline_view import SurveyLineView

class SurveyLinePane(TraitsTaskPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_line'
    name = "Survey Line"

    survey_line = Instance(ISurveyLine)

    line_name = Property(depends_on='survey_line.name')
    def _get_line_name(self):
        if self.survey_line:
            return self.survey_line.name
        else:
            return 'None'

    survey_data_session = Instance(SurveyDataSession)

    survey_line_view = Instance(SurveyLineView)

    def _survey_line_default(self):
        # XXX temporary hack!
        from ..my_depth_tester import create_surveyline
        return create_surveyline()

    def _survey_data_session_default(self):
        return SurveyDataSession(surveyline=self.survey_line)

    def _survey_line_view_default(self):
        return SurveyLineView(model=self.survey_data_session)

    view = View(
        Item('survey_line_view', style='custom', show_label=False)
    )
