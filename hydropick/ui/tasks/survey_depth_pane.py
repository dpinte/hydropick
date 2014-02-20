#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from chaco.api import Plot
from traits.api import (DelegatesTo, Instance, on_trait_change, Property,
                        Supports, Bool)
from traitsui.api import View, Item, ModelView
from enable.component_editor import ComponentEditor
from pyface.tasks.api import TraitsDockPane

from hydropick.ui.survey_depth_line_view import DepthLineView
from hydropick.model.i_survey_line import ISurveyLine
from hydropick.model.depth_line import DepthLine


class SurveyDepthPane(TraitsDockPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_depth_line'
    name = "Depth Line"

    #: proxy for the task's current survey line
    current_survey_line = DelegatesTo('task')

    current_data_session = DelegatesTo('task')

    depth_line_view = Instance(DepthLineView)

    depth_line = Instance(DepthLine)

    #: proxy for the editor's current depth line
    selected_depth_line_name = DelegatesTo('task')

    # dict of algorithms though currently not use since datasession has it.
    algorithms = DelegatesTo('task')

    show_view = Bool(False)

    def _depth_line_view_default(self):
        return None

    def _selected_depth_line_name_changed(self):
        name = self.selected_depth_line_name
        d = self.current_data_session.depth_dict[self.selected_depth_line_name]
        self.depth_line_view.model = d
        self.depth_line_view.selected_depth_line_name = name

    @on_trait_change('current_data_session')
    def _set_depth_line_view(self):
        if self.current_data_session:
            self.depth_line_view = self._get_depth_line_view()

    def _get_depth_line_view(self):
        data = self.current_data_session
        sanity_check = data.survey_line is self.current_survey_line
        if data and sanity_check:
            view = DepthLineView(model=DepthLine(),
                                 selected_depth_line_name='none',
                                 data_session=self.current_data_session
                                 )
            self.show_view = True
        else:
            view = None
            self.show_view = False
        return view

    view = View(
        Item('depth_line_view',
             style='custom',
             visible_when='show_view',
             show_label=False
             ),
        kind='nonmodal'
        )
