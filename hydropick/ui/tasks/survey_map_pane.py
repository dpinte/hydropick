#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from chaco.api import Plot
from traits.api import Instance, Property, Supports, Any
from traitsui.api import View, Item
from enable.component_editor import ComponentEditor
from pyface.tasks.api import TraitsDockPane

from hydropick.model.lake import Lake
from hydropick.ui.survey_map_view import SurveyMapView
from hydropick.model.i_survey import ISurvey


class SurveyMapPane(TraitsDockPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_map'
    name = "Map"

    survey = Supports(ISurvey)

    survey_map_view = Property(depends_on='survey')

    def _get_survey_map_view(self):
        lines = [line.navigation_line for line in self.survey.survey_lines]
        return SurveyMapView(model=self.survey)

    plot = Property(Instance(Plot), depends_on='survey')

    def _get_plot(self):
        return self.survey_map_view.plot

    view = View(Item('plot', editor=ComponentEditor(),
                     width=400,
                     height=200,
                     show_label=False))
