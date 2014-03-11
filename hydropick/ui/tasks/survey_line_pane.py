#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import logging
from traits.api import (DelegatesTo, Instance, Property, Bool, Dict, List, Str,
                        Supports)
from traitsui.api import View, Item
from pyface.tasks.api import TraitsTaskPane

from ...model.i_survey_line import ISurveyLine
from ..survey_data_session import SurveyDataSession
from ..survey_line_view import SurveyLineView
from hydropick.model.i_core_sample import ICoreSample

logger = logging.getLogger(__name__)

CORE_DISTANCE_TOLERANCE = 200

class SurveyLinePane(TraitsTaskPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_line'
    name = "Survey Line"

    survey = DelegatesTo('task')

    # current survey line viewed in editing pane.
    # listener is set up in 'task.create_central_pane' to change line.

    survey_line = Instance(ISurveyLine)

    current_data_session = DelegatesTo('task')

    core_samples = List(Supports(ICoreSample))

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

    def on_change_settings(self):
        ''' Open dialog to adjust image (B&C : task menu)'''
        self.survey_line_view.line_settings_dialog()

    def on_cursor_freeze(self):
        ''' Currently just shows Key Binding to freeze cursor'''
        pass

    def on_change_colormap(self):
        ''' Open dialog to adjust image (B&C : task menu)'''
        self.survey_line_view.cmap_edit_dialog()

    def on_show_location_data(self):
        ''' Open dialog to show location data (task menu)'''
        self.survey_line_view.show_data_dialog()

    def on_show_plot_view_selection(self):
        ''' Open dialog to change which plots to view (task menu)'''
        self.survey_line_view.plot_view_selection_dialog()

    def _survey_line_changed(self):
        ''' handle loading of survey line view if valid line provide or else
        provide an empty view.
        '''
        if self.survey_line is None:
            logger.warning('current survey line is None')
            self.show_view = False
            self.survey_line_view = None
        else:
            data_session = self.data_session_dict.get(self.line_name, None)
            if data_session is None:
                # create new datasession object and entry for this surveyline.
                if self.survey_line.trace_num.size == 0:
                    # need to load data for this line
                    self.survey_line.load_data(self.survey.hdf5_file)
                data_session = SurveyDataSession(survey_line=self.survey_line,
                                                 algorithms=self.algorithms)
                self.data_session_dict[self.line_name] = data_session
            self.current_data_session = data_session

            # load relevant core samples into survey line
            # must do this before creating survey line view
            all_samples = self.survey.core_samples
            d = CORE_DISTANCE_TOLERANCE
            near_samples = self.survey_line.nearby_core_samples(all_samples, d)
            self.survey_line.core_samples = near_samples

            # create survey line view
            self.survey_line_view = SurveyLineView(model=data_session)
            self.show_view = True

    view = View(
        Item('survey_line_view', style='custom', show_label=False,
             visible_when='show_view')
        )
