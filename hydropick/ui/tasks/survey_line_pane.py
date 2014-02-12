#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Instance, Property, Bool, Dict, Str, DelegatesTo
from traitsui.api import View, Item
from pyface.tasks.api import TraitsTaskPane

from ...model.i_survey_line import ISurveyLine
from ..survey_data_session import SurveyDataSession
from ..survey_line_view import SurveyLineView


class SurveyLinePane(TraitsTaskPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_line'
    name = "Survey Line"

    # current survey line viewed in editing pane.
    # listener is set up in 'task.create_central_pane' to change line.
    survey_line = Instance(ISurveyLine)

    # provides string with name of line for keys or info.
    line_name = Property(depends_on='survey_line.name')

    def _get_line_name(self):
        if self.survey_line:
            return self.survey_line.name
        else:
            return 'None'

    # instance of survey_line view which displays selected surveyline
    survey_line_view = Instance(SurveyLineView)

    # once a valid survey line is selected a datasession will
    # created and stored for quick retrieval on line changes
    data_session_dict = Dict(Str, Instance(SurveyDataSession))

    #: dictionary of (name, class) pairs for available depth pic algorithms
    algorithms = DelegatesTo('task')

    # set when survey_line is none to prevent showing invalid view.
    show_view = Bool(False)

    def on_image_adjustment(self):
        ''' Open dialog to adjust image (B&C : task menu)'''
        self.survey_line_view.image_adjustment_dialog()

    def on_show_location_data(self):
        ''' Open dialog to show location data (task menu)'''
        self.survey_line_view.show_data_dialog()

    def on_new_depth_line(self):
        ''' Open dialog to create new depth line (task menu)'''
        self.survey_line_view.new_algorithm_line_dialog()
        
    def on_show_plot_view_selection(self):
        ''' Open dialog to change which plots to view (task menu)'''
        self.survey_line_view.plot_view_selection_dialog()

    def _survey_line_changed(self):
        ''' handle loading of survey line view if valid line provide or else
        provide an empty view.
        '''
        if self.survey_line is None:
            self.show_view = False
            self.survey_line_view = None
        else:
            data_session = self.data_session_dict.get(self.line_name, None)
            if data_session is None:
                # create new datasession object and entry for this surveyline.
                self.survey_line.load_data()
                data_session = SurveyDataSession(survey_line=self.survey_line)
                self.data_session_dict[self.line_name] = data_session

            self.survey_line_view = SurveyLineView(model=data_session,
                                                   algorithms=self.algorithms)
            self.show_view = True

    view = View(
        Item('survey_line_view', style='custom', show_label=False,
             visible_when='show_view')
        )
