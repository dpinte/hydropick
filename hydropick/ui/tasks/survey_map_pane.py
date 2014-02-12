#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from chaco.api import Plot
from traits.api import DelegatesTo, Instance, on_trait_change, Property, Supports
from traitsui.api import View, Item, ModelView
from enable.component_editor import ComponentEditor
from pyface.tasks.api import TraitsDockPane

from hydropick.ui.survey_map_view import SurveyMapView
from hydropick.ui.tasks.survey_task import SurveyTask
from hydropick.model.i_survey import ISurvey


class SurveyMapPane(TraitsDockPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_map'
    name = "Map"

    survey = Supports(ISurvey)

    survey_task = Supports(SurveyTask)

    #: proxy for the task's current survey line
    current_survey_line = DelegatesTo('survey_task')

    def _current_survey_line_changed(self):
        self.survey_map_view.current_survey_line = self.current_survey_line

    #: proxy for the task's current survey line group
    current_survey_line_group = DelegatesTo('survey_task')

    #: reference to the task's selected survey lines
    selected_survey_lines = DelegatesTo('survey_task')

    def _selected_survey_lines_changed(self):
        try:
            self.survey_map_view.selected_survey_lines = self.selected_survey_lines
        except:
            pass

    survey_map_view = Instance(ModelView)

    def _survey_map_view_default(self):
        return self._get_survey_map_view()

    @on_trait_change('survey')
    def _set_survey_map_view(self):
        self.survey_map_view = self._get_survey_map_view()

    def _get_survey_map_view(self):
        #from IPython import embed; embed()
        if self.survey_task is None:
            selected_survey_lines = []
            return None
        return SurveyMapView(model=self.survey,
                             survey_task=self.survey_task,
                             selected_survey_lines=self.selected_survey_lines)

    plot = Property(Instance(Plot), depends_on='survey_map_view')

    def _get_plot(self):
        try:
            return self.survey_map_view.plot
        except:
            return None

    view = View(Item('plot', editor=ComponentEditor(),
                     width=400,
                     height=200,
                     show_label=False))
