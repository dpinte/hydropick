#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Instance, Property, Trait, Bool, Dict, Str, Either, Any
from traitsui.api import View, Item
from pyface.tasks.api import TraitsTaskPane

from ...model.i_survey_line import ISurveyLine
from ..surveydatasession import SurveyDataSession
from ..surveyline_view import SurveyLineView, EmptyView

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

    # once a valid survey line is selected a datasession will
    # created and stored for quick retrieval on line changes
    datasession_dict = Dict(Str, Instance(SurveyDataSession))

    # either a filled view or an empty view for no survey line.
    # survey_line_view = Either(
    #                          Instance(EmptyView),
    #                          Instance(SurveyLineView)
    #                          )

    show_view = Bool(False)
    #empty = Property(depends_on='show_view')

    # survey_data_session = Instance(SurveyDataSession)

    survey_line_view = Instance(SurveyLineView)
    #empty_view = Instance(EmptyView)

    # def _survey_line_changed(self):
    #     self.survey_data_session.surveyline = self.survey_line

    # def _survey_line_default(self):
    #     # XXX temporary hack!
    #     from ..my_depth_tester import get_survey_line
    #     return get_survey_line()

    # def _survey_data_session_default(self):
    #     return SurveyDataSession(surveyline=self.survey_line)

    # def _survey_line_view_default(self):
    #     return SurveyLineView(model=self.survey_data_session)


    def _survey_line_changed(self):
        ''' handle loading of survey line view if valid line provide or else
        provide an empty view.
        '''
        if self.survey_line is None:
            print 'surveyline is NOne'
            self.show_view = False
            self.survey_line_view = None
        else:
            datasession = self.datasession_dict.get(self.line_name, None)
            if datasession is None:
                # create new datasession object and entry for this surveyline.
                self.survey_line.load_data()
                datasession = SurveyDataSession(surveyline=self.survey_line)
                self.datasession_dict[self.line_name]=datasession
            self.survey_line_view = SurveyLineView(model=datasession)
            self.show_view = True

    # def _empty_view_default(self):
    #     return EmptyView()

    # def _survey_line_view_default(self):
    #     return EmptyView()

    # def _get_empty(self):
    #     return not self.show_view
    # view = View(
    #     Item('survey_line_view', style='custom', show_label=False,
    #          visible_when='show_view')
    # )

    view = View(
                # Item('empty_view', show_label=False,
                #      visible_when='empty'),
                Item('survey_line_view', style='custom', show_label=False,
                     visible_when='show_view')
    )
